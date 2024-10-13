from flask import request, Blueprint
from slack_sdk.web import WebClient
import os, urllib.parse, json
from datetime import datetime
from utils.logger import logger
from utils.slack_message import SlackMessageProcessor
from models.resolved_request import ResolvedRequest
from models.need_help import NeedHelp


SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
slack_client = WebClient(SLACK_BOT_TOKEN)

slack_api_routes = Blueprint('simple',__name__,template_folder='templates')
# Flask health check
@slack_api_routes.route("/")
def hello():
    return "Hello there, health!"

@slack_api_routes.route("/slack/interactive-endpoint", methods=['POST'])
def slack_interactive():
    #logger.debug(f"before parser")
    headers = request.headers
    #logger.debug(f"headers:\n\n\n {headers}")
    body = request.get_data()
    msg = parser_interactive_msg(body)
    logger.debug(f"\n\n\n decoded payload:\n {msg}\n\n\n ")
    tri_id, channel, thread, action_value, username, payload_msg, industry, scenario = SlackMessageProcessor.process_interactive_message(msg)
    action_cases = {
        "need_help": lambda: slack_client.views_open(
            trigger_id=tri_id,
            view=need_help_view(channel, thread)
        ),
        "solution_found": lambda: resolved_request_action(username, channel, thread, payload_msg),
        "modal_submitted": lambda: need_help_action(username, channel, thread, payload_msg, industry, scenario),
        # "modal_submitted": lambda: slack_client.views_update(
        #     trigger_id=tri_id,
        #     view=need_help_view(),
        #     view_id='V07PGQDNWRJ'
        # ),
        # Add more cases as needed
    }
    action_cases.get(action_value, lambda: slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread,
            text="请继续与我对话，提供更多信息:handshake:"
        ))()
   
    return "", 200

def resolved_request_action(username, channel, thread, message):
    slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread,
            text="感谢使用,祝项目顺利，进度:100:"
        )
    
    ResolvedRequest.add(username=username, thread_ts=thread, message=message)

def need_help_action(username, channel, thread, message, industry, scenario):
    slack_client.chat_postMessage(
                channel=channel,
                thread_ts=thread,
                text="已经收到反馈，会尽快请Solution Repo团队查找方案。"
    )
    NeedHelp.add(username=username, industry=industry, scenario=scenario)

def parser_interactive_msg(body:str)-> dict:
    decoded_body = body.decode('utf-8')
    payload = decoded_body.split('payload=')[1]  
    return json.loads(urllib.parse.unquote(payload))  # Decode URL-encod

def need_help_view(channel, thread):
    with open("./views/collect_info_modal.json", encoding="utf-8") as f:
        modal_view = json.load(f)
    modal_view['callback_id']='{}#{}'.format(channel, thread)
    return modal_view