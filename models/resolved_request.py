from . import db
from models.base_model import BaseModel
from sqlalchemy import Column, String, Text, Integer, UnicodeText
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
import json

class ResolvedRequest(db.Model, BaseModel):
    __tablename__ = 'resolved_request'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, comment='用户的login')
    thread_ts = Column(String(256), nullable=False, comment='聊天的channel', index=True)
    message = Column(UnicodeText, nullable=False, comment='对话内容')
    createAt = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    modifyAt = Column(DateTime, nullable=True, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    version = Column(Integer, nullable=True)

    def __init__(self, username, thread_ts, message, version=1):
        self.username = username
        self.thread_ts = thread_ts
        self.message = json.dumps(message, ensure_ascii=False)
        self.version = version

    def __repr__(self):
        return json.dumps({
            'id': self.id,
            'username': self.username,
            'thread_ts': self.thread_ts,
            'channel': self.channel,
            'message': self.message,
            'createAt': self.createAt.isoformat() if self.createAt else None,
            'modifyAt': self.modifyAt.isoformat() if self.modifyAt else None,
            'version': self.version
        }, default=str)
        
        

