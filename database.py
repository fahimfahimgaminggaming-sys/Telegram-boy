from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["telegram_bot"]

users = db["users"]

def get_user(user_id):

    user = users.find_one({"user_id": user_id})

    if not user:
        users.insert_one({
            "user_id": user_id,
            "balance": 0
        })

    return users.find_one({"user_id": user_id})
