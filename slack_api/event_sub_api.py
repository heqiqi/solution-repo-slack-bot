from flask import Flask, request, copy_current_request_context
from flask_sqlalchemy import SQLAlchemy
from slackeventsapi import SlackEventAdapter
from slack_sdk.web import WebClient
from typing import List, Dict
from pathlib import Path
from utils.bedrock import BedrockHandler, KBHandler
from utils.slack_message import SlackMessageProcessor
from models.chat_messages import ConversationHistory
from datetime import datetime
from utils.logger import logger

def init_slack_adapter(app):
    app

# TODO mv slack function in this file