from . import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
import json

class BaseModel:
    @classmethod
    def add(cls, **kwargs):
        try:
            new_record = cls(**kwargs)
            db.session.add(new_record)
            db.session.commit()
            return new_record
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def find(cls, **kwargs):
        try:
            return cls.query.filter_by(**kwargs).all()
        except Exception as e:
            raise e


class ConversationHistory(db.Model, BaseModel):
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, comment='用户的login')
    channel = Column(String(256), nullable=False, comment='channel')
    thread_ts = Column(String(256), nullable=False, comment='聊天的channel', index=True)
    message = Column(Text, nullable=False, comment='对话内容')
    createAt = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    modifyAt = Column(DateTime, nullable=True, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    version = Column(Integer, nullable=True)

    def __init__(self, username, channel, thread_ts, message, version=1):
        self.username = username
        self.channel = channel
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
        
    @classmethod
    def get_messags_by_thread(cls, thread):
        try:
            return cls.query.filter_by(thread_ts=thread).order_by(cls.modifyAt.asc()).all()
        except Exception as e:
            raise e
        


