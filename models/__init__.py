from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

db = SQLAlchemy()

def init_db(app):
    # Use the custom engine for SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Psa123456#@database-slackbot-instance-1.cdk2cayg4rmm.us-west-2.rds.amazonaws.com:3306/slack_bot?charset=utf8'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': QueuePool,
        'pool_pre_ping': True,
        'pool_recycle': 1200  # Recycle connections after 1 hour
    }
    app.config['JSON_AS_ASCII'] = False

    db.init_app(app)