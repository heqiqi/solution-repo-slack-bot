from flask import Flask, request, copy_current_request_context
from flask_sqlalchemy import SQLAlchemy
from slackeventsapi import SlackEventAdapter
from slack_sdk.web import WebClient
from typing import List, Dict
from pathlib import Path
from utils.bedrock import BedrockHandler, KBHandler
from utils.slack_message import SlackMessageProcessor
from models.chat_messages import ConversationHistory
import os, openai, json, boto3, threading,re
from datetime import datetime
from utils.logger import logger
from models import init_db
from slack_api.interactive_api import slack_api_routes


#global variable
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_BOT_ID = os.environ.get("SLACK_BOT_ID")
FLASK_PORT = os.environ.get("FLASK_PORT")

openai.api_key = OPENAI_API_KEY
openai.api_base = "https://api.aihubmix.com/v1"

slack_msg_history = {}

app = Flask(__name__)
app.register_blueprint(slack_api_routes)

#slack configure
slack_client = WebClient(SLACK_BOT_TOKEN)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

init_db(app)

# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    emoji = event_data["event"]["reaction"]
    print(emoji)

@slack_events_adapter.on("app_mention")
def handle_mentions(event_data):
    event = event_data["event"]
    # slack_client.chat_postMessage(
    #     channel=event["channel"],
    #     text=f"Hello, this is solution bot:\n>{event['text']}",
    # )


# Example responder to greetings
@slack_events_adapter.on("message")
def handle_message(event_data):
    logger.debug(f"Received event_data: {event_data}")
    message = event_data["event"]
    if message.get("subtype") is None and message.get("bot_id") is None:
        threading.Thread(target=execute_engin_thread, args=(message, datetime.now().timestamp())).start()
    

def execute_engin_thread(message, i):
    # print(f"in thread: {i}\n Received message: {message}")
    with app.app_context():
        text = message['text']
        pattern = r"<@U[A-Z0-9]+>"
        if  bool(re.search(pattern, text)) and (SLACK_BOT_ID not in text):
            logger.debug(f"\nignore bot message: {text}\n")
            return
        if ('thread_ts' not in message) and (SLACK_BOT_ID not in text) and (message['channel_type'] == "channel") and (message['type'] == "message"):
            logger.debug(f"\n chat in channel not @ bot, so ignore: {text}\n")
            return
        channel, thread, text, username = SlackMessageProcessor.process_message(message)
        logger.debug(
            f"thread Received message: {channel},{thread},{text},{username}"
        )
        
        message_processor = get_msg_history(thread)
        intention = intention_detect(text)
        logger.debug(f"intention:\n {intention} {text}")
        prompt = {"role": "user", "content": [{"text": text}]}
        message_processor.save_history_message(username, channel, prompt)
        if not intention:
            logger.debug(
                f"MSG Q: {message_processor.get_history_message()}"
            )
            resp = claud_response(message_processor.get_history_message())
            output = {"role": "assistant", "content": [{"text": resp}]}
            message_processor.save_history_message(username, channel, output)
            slack_client.chat_postMessage(thread_ts=thread, channel=channel, text=resp)
        else:
            slack_client.chat_postMessage(
                thread_ts=thread, channel=channel, text='收到请求，正在为您检索Solution Repo...'
            )
            logger.debug(f"MSG Q {message_processor.get_history_message()}")
            docs = retriever.get_relevant_docs(str(prompt))
            context = retriever.parse_kb_output_to_string(docs)
            logger.debug(f"doc:\n\n{docs}, context:\n\n{context}")
            message_processor.save_history_message(username, channel,
                {"role": "assistant", "content": [{"text": context}]}
            )
            gen_prompt = [{
                "role": "user",
                "content": [{"text": f"请根据下面的背景知识:\n{context} \n\n 以中文回答下面的问题: {text}"}],
            }]
            resp = claud_response(gen_prompt)
            slack_client.chat_postMessage(
                thread_ts=thread, channel=channel, text=resp, blocks=generate_slack_reply(resp)
            )

def generate_slack_reply(content) -> dict:
    return [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": content
            }
        },
        {
			"type": "divider"
		},
        {
        "type": "actions",
        "elements": [
        {
        #   "style": "primary",
          "text": {
            "text": ":white_check_mark:已解决",
            "type": "plain_text"
          },
          "type": "button",
          "value": "solution_found"
        },
        {
        #   "style": "primary",
          "text": {
            "text": ":x:没帮助",
            "type": "plain_text"
          },
          "type": "button",
          "value": "need_help"
        }
      ]
    }
    ]

def get_msg_history(thread:str) -> SlackMessageProcessor:
    if thread not in slack_msg_history:
        slack_msg_processor = SlackMessageProcessor(thread)
        slack_msg_history[thread] =  slack_msg_processor
    return slack_msg_history[thread]

def gpt_response(direct_message_history: List[Dict[str, str]], reset = 0):
    if reset:
        logger.debug('TODO: clean chat history')
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = direct_message_history
    )
    return {response['choices'][0]['message']['role']: response['choices'][0]['message']['content']}

def claud_response(message_history:List):
    """
    Invoke the Claude model using the Bedrock handler and return the response text.

    Args:
        direct_message_history (list): A list of message dictionaries containing the conversation history.

    Returns:
        str: The text content of the Claude model's response.
    """
    messages = [ 
        {"role": "user", "content": [{"text":"你好"}] },
        {"role": "assistant", "content": [{"text":"你好"}] },
        {"role": "user", "content": [{"text":"再次你好"}] }
     ]
    print(f"messages: {message_history}")
    response = bedrock_handler.invoke_model(message_history)
    
    # Extract the text content from the response
    if response and 'output' in response:
        for content_item in response["output"]["message"]["content"]:
            if 'text' in content_item:
                return content_item['text']
    
    # Return an empty string if no text content is found
    return ""

def get_retriever():
    with open("./config.json", encoding="utf-8") as f:
        configs = json.load(f)
    bedrock_agent_runtime_client = boto3.client(
        "bedrock-agent-runtime", region_name=configs["bedrock_region"]
    )
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime", region_name=configs["bedrock_region"]
    )
    model_id = configs["multimodal_llms"]["Anthropic Claude 3.5 Sonnet"]
    bedrock_handler = BedrockHandler(
        bedrock_runtime, model_id, configs["claude_model_params"]
    )
    retriever = KBHandler(
        bedrock_agent_runtime_client, configs["kb_configs"], kb_id=configs["kb_id"]
    )
    return bedrock_handler,retriever


def intention_detect(user_input: str):
    user_prompt = """
    You are tasked with determining whether a user's query is about seeking a aws solution to a problem or not. This is important for properly categorizing and routing user inquiries.

Here is the user's query:
<user_query>
{{USER_QUERY}}
</user_query>

Carefully analyze the query and determine if it appears to be seeking a solution or resolution to a problem. Consider the following criteria:

1. Does the query describe a problem or issue?
2. Is the user explicitly asking for help or a solution?
3. Does the query imply a need for assistance or guidance?
4. Is there a clear indication of dissatisfaction or a desire for improvement?

After analyzing the request, provide your response in the following JSON format without xml:

{
  "is_solution_request": boolean
}


    """
    messages = [
        #{"role": "system", "content": [{'text': '你是由Anthropic开发的 AI 人工智能助手'}]},
        {"role": "user", "content": [{'text':  user_prompt.replace("{{USER_QUERY}}", user_input)}] }
    ]
    response = bedrock_handler.invoke_model(messages)
    # logger.debug(f"response: {response}")
    full_response = response["output"]["message"]["content"][0]["text"]
    return ("true" in full_response)


bedrock_handler, retriever = get_retriever()

# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=FLASK_PORT,host='0.0.0.0')