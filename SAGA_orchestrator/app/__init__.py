from app.config import Config
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_mongoengine import MongoEngine
db = MongoEngine()
jwt = JWTManager()
def create_app(config_class=None):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    #jwt setup
    jwt.init_app(app)
    #mongoengine setup
    db.init_app(app)
    # Register blueprints
    from .api.v1_routes import v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    # from .api.dashboard_routes import dashboard_bp
    # app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    from .api.auth_routes import auth_routes_bp
    app.register_blueprint(auth_routes_bp,url_prefix='/api/auth')
    from .api.dashboard_routes_v2 import dashboard_bp_v2
    app.register_blueprint(dashboard_bp_v2,url_prefix='/api/dashboard')
    return app
