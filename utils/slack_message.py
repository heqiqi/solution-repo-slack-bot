"""
Process slack message on event api
"""
import re, json
from models.chat_messages import ConversationHistory


class SlackMessageProcessor:
    def __init__(self,thread_ts):
        self.message_queue = []
        self.thread_ts = thread_ts

    @staticmethod
    def process_message(message):
        """
        Process incoming Slack message event
        """
        channel = message["channel"]
        thread =  message['ts']
        if 'event_ts' in message:
            thread = message['event_ts']
        if 'thread_ts' in message:
            thread = message['thread_ts']
        text = message['text'] if message['channel_type'] == 'im' else  re.sub('<.*?>', '', message['text'])
        username = message['user']
        if 'user_profile' in message:
            username = message['user_profile']['name']
        return channel, thread, text, username
    
    @staticmethod
    def process_interactive_message(message):
        """
        Process incoming interactive message 
        """
        trigger_id = message["trigger_id"]
        username = message['user']['username']
        msg_type = message["type"]
        m = ''
        if 'message' in message:
            m = message['message']
        industry = ''
        scenario = ''
        if msg_type == "block_actions":
            channel = message['channel']['id']
            thread =  message['message']['thread_ts']
            action_value = message['actions'][0]['value']
        else:
            callback_id = message['view']['callback_id']
            channel, thread = callback_id.split('#')
            action_value = 'modal_submitted'
            industry = message['view']['state']['values']['industry_input_block']['select_industry']['selected_option']['value']
            scenario = message['view']['state']['values']['use_case_input_block']['input_usecase']['value']
        return trigger_id, channel, thread, action_value, username, m, industry, scenario

    def save_history_message(self, username, channel, m):
        """
        Process a regular text message
        """
        #self.message_queue.append(m)
        ConversationHistory.add(username=username, channel=channel, thread_ts=self.thread_ts, message=m)
        
    def get_history_message(self):
        """
        Retrieve the message history from the message queue
        
        Returns:
            list: A list of message dictionaries representing the conversation history
        """
        msg_list =  ConversationHistory.get_messags_by_thread(self.thread_ts)
        prompt = []
        for m in msg_list:
            #print(f'aaa{m.message}bbb')
            prompt.append(json.loads(m.message))
        print(f'{prompt}')
        return prompt
       

