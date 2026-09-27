from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import create_access_token
from flask import jsonify
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from SAGA_orchestrator.app.models.user import Users
def create_user(username: str, email: str, password: str):
    """Create a new user with plain string password storage."""
    if Users.objects(email=email).first():
        return None, "email already exists"
    
    user = Users(
        username=username,
        email=email,
        password=generate_password_hash(password)
    )
    user.save()
    return str(user.id), None

def check_user(email:str,password:str) -> dict :
    user = Users.objects(email=email).first()
    if not user or not check_password_hash(user.password,password):
        err = {
            'status':"failed",
            'message':'Invalid credentials',
            'data':{}
        }
        return err
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    payload = {
        'status':'success',
        'message':'login access',
        'data':{
            'access_token':access_token,
            'refresh_token':refresh_token
        }
    }    
    return payload
