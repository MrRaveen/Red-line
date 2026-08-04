import logging
from flask import Flask
from config import settings
from .config import Config
from extensions import init_redis

def create_app(config_class=None):
    #basic log config
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    app = Flask(__name__)
    if config_class is None:
        config_class = Config
    app.config.from_object(config_class)

    #redis config
    # init_redis(app)
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app

