from flask import Flask

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration, initialize extensions here
    
    # Register blueprints
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app
