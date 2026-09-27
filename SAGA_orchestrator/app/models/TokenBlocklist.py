from app import db, jwt
from datetime import datetime

class TokenBlocklist(db.Document):
    meta = {'collection':'tokenBlockList',
    'indexes':[
        'jti',
        {
            'fields': ['created_at'],
            'expireAfterSeconds': 86400
        }
    ]
    }
    jti = db.StringField(required = True)
    created_at = db.DateTimeField(default=datetime.utcnow)

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header,jwt_payload:dict)->bool:
    jti = jwt_payload['jti']
    token = TokenBlocklist.objects(jti=jti).first()
    return token is not None


