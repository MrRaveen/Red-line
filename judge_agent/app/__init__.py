from flask import Flask

def create_app(config_class=None):
    app = Flask(__name__)

    from .api.v1_routes import v1_routes
    app.register_blueprint(v1_routes, url_prefix='/api/v1')
    
    return app
