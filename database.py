from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)

db = client["telegram_bot"]

users = db["users"]
tasks = db["tasks"]
deposits = db["deposits"]


# ================= USER =================

def get_user(user_id):

    user = users.find_one({"user_id": user_id})

    if not user:

        users.insert_one({
            "user_id": user_id,
            "balance": 0,
            "referrals": 0,
            "tasks": 0
        })

    return users.find_one({"user_id": user_id})


# ================= BALANCE =================

def add_balance(user_id, amount):

    users.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": amount}}
    )


def remove_balance(user_id, amount):

    users.update_one(
        {"user_id": user_id},
        {"$inc": {"balance": -amount}}
    )


# ================= TASK =================

def create_task(channel, reward):

    tasks.insert_one({
        "channel": channel,
        "reward": reward
    })


def get_tasks():

    return list(tasks.find())


# ================= DEPOSIT =================

def add_deposit(user_id, amount, method):

    deposits.insert_one({
        "user_id": user_id,
        "amount": amount,
        "method": method
    })


def get_deposits(user_id):

    return list(deposits.find({"user_id": user_id}))
