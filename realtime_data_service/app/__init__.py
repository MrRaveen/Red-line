from flask import Flask
from flask_cors import CORS

def create_app(config_class=None):
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration, initialize extensions here
    
    # Register blueprints
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app
