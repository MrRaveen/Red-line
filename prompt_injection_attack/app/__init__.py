import logging
from flask import Flask
from config import settings

def create_app(config_class=None):
    # Set up basic logging for the console based on the .env LOG_LEVEL
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    
    app = Flask(__name__)
    
    # Load configuration, initialize extensions here
    
    # Register blueprints
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app
