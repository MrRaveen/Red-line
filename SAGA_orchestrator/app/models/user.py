from datetime import datetime
from pymongo import MongoClient
from app.config import Config

client = MongoClient(Config.MONGO_URI)
db = client["redline_logs"]
users_collection = db["users"]


def create_user(username: str, email: str, password: str):
    """Create a new user with plain string password storage."""
    if users_collection.find_one({"username": username}):
        return None, "Username already exists"
    user = {
        "username": username,
        "email": email,
        "password": password,
        "created_at": datetime.utcnow().isoformat()
    }
    result = users_collection.insert_one(user)
    return str(result.inserted_id), None


def check_user(username: str, password: str):
    """Check user credentials by direct string comparison."""
    return users_collection.find_one({"username": username, "password": password})
