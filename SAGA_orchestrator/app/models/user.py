from datetime import datetime
from app import db

class Users(db.Document):
    meta = {'collection': 'users'}
    username = db.StringField(required=True, unique=True)
    email = db.StringField(required=True)
    password = db.StringField(required=True)#hash
    created_at = db.DateTimeField(default=datetime.utcnow)

