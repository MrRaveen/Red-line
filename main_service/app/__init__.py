import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app(config_class=None):
    load_dotenv() # load env
    app = Flask(__name__)
    # postgres DB config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app

