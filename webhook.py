from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb+srv://botpassword123:botpassword123@cluster0.hrcnqqs.mongodb.net/?retryWrites=true&w=majority")
db = client["earn_bot"]

users = db["users"]
deposits = db["deposits"]

@app.route("/xrocket_webhook", methods=["POST"])
def webhook():

    data = request.json

    try:

        invoice_id = data.get("invoice_id")
        status = data.get("status")

        if status == "paid":

            dep = deposits.find_one({"invoice_id":invoice_id})

            if dep and dep["status"] == "pending":

                users.update_one(
                    {"user_id": dep["user_id"]},
                    {"$inc":{"balance": dep["amount"]}}
                )

                deposits.update_one(
                    {"invoice_id":invoice_id},
                    {"$set":{"status":"completed"}}
                )

        return jsonify({"ok":True})

    except Exception as e:
        return jsonify({"error":str(e)})

app.run(host="0.0.0.0", port=8080)
