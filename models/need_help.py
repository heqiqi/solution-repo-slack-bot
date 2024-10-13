from . import db
from models.base_model import BaseModel
from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.sql import func
import json

class NeedHelp(db.Model, BaseModel):
    __tablename__ = 'need_help'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(128), nullable=False, comment='用户的login')
    industry = Column(String(256), nullable=False, comment='行业')
    scenario = Column(Text, nullable=False, comment='场景')
    createAt = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    modifyAt = Column(DateTime, nullable=True, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    version = Column(Integer, nullable=True)

    def __init__(self, username, industry, scenario, version=1):
        self.username = username
        self.industry = industry
        self.scenario = scenario
        self.version = version

    def __repr__(self):
        return json.dumps({
            'id': self.id,
            'username': self.username,
            'industry': self.industry,
            'scenario': self.scenario,
            'createAt': self.createAt.isoformat() if self.createAt else None,
            'modifyAt': self.modifyAt.isoformat() if self.modifyAt else None,
            'version': self.version
        }, default=str)
        
        

