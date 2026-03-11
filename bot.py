import telebot
import requests
import time
from telebot import types
from config import BOT_TOKEN, NOWPAY_API_KEY
from database import get_user
from pymongo import MongoClient
from config import MONGO_URI

bot = telebot.TeleBot(BOT_TOKEN)

client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users = db["users"]
payments = db["payments"]


# ---------------- MENU ----------------

def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 Deposit")
    markup.row("👤 Profile", "💵 Balance")
    return markup


# ---------------- START ----------------

@bot.message_handler(commands=['start'])
def start(message):

    user = get_user(message.from_user.id)

    text = f"""
👋 Welcome {message.from_user.first_name}

💵 Balance: {user['balance']} $

Choose option 👇
"""

    bot.send_message(message.chat.id, text, reply_markup=menu())


# ---------------- PROFILE ----------------

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    text = f"""
👤 PROFILE

🆔 ID: {message.from_user.id}
💵 Balance: {user['balance']} $
"""

    bot.send_message(message.chat.id, text)


# ---------------- BALANCE ----------------

@bot.message_handler(func=lambda m: m.text == "💵 Balance")
def balance(message):

    user = get_user(message.from_user.id)

    bot.send_message(message.chat.id, f"💵 Your balance: {user['balance']} $")


# ---------------- DEPOSIT ----------------

@bot.message_handler(func=lambda m: m.text == "📥 Deposit")
def deposit(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⭐ Stars payment")
    markup.row("💰 Crypto payment")
    markup.row("⬅ Back")

    bot.send_message(message.chat.id, "Choose deposit method:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "⬅ Back")
def back(message):
    start(message)


# ---------------- STARS PAYMENT ----------------

@bot.message_handler(func=lambda m: m.text == "⭐ Stars payment")
def stars(message):

    prices = [types.LabeledPrice(label="Stars Deposit", amount=100)]

    bot.send_invoice(
        message.chat.id,
        title="Stars Deposit",
        description="Deposit using Telegram Stars",
        invoice_payload="stars",
        provider_token="",
        currency="XTR",
        prices=prices
    )


@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def stars_success(message):

    amount = message.successful_payment.total_amount / 100

    users.update_one(
        {"user_id": message.from_user.id},
        {"$inc": {"balance": amount}}
    )

    bot.send_message(
        message.chat.id,
        f"✅ Stars payment received\n💰 {amount}$ added to balance"
    )


# ---------------- CRYPTO PAYMENT ----------------

@bot.message_handler(func=lambda m: m.text == "💰 Crypto payment")
def crypto(message):

    msg = bot.send_message(message.chat.id, "Send amount in USD (example: 10)")
    bot.register_next_step_handler(msg, create_payment)


def create_payment(message):

    try:
        amount = float(message.text)

        url = "https://api.nowpayments.io/v1/payment"

        headers = {
            "x-api-key": NOWPAY_API_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "price_amount": amount,
            "price_currency": "usd",
            "pay_currency": "usdttrc20"
        }

        r = requests.post(url, json=data, headers=headers).json()

        payment_id = r["payment_id"]
        address = r["pay_address"]
        pay_amount = r["pay_amount"]

        payments.insert_one({
            "payment_id": payment_id,
            "user_id": message.from_user.id,
            "amount": amount,
            "status": "waiting"
        })

        text = f"""
💰 SEND PAYMENT

Amount: {pay_amount} USDT
Address:
{address}

After payment bot will auto detect.
"""

        bot.send_message(message.chat.id, text)

    except:
        bot.send_message(message.chat.id, "❌ Invalid amount")


# ---------------- AUTO DETECT PAYMENT ----------------

def check_payments():

    while True:

        pending = payments.find({"status": "waiting"})

        for p in pending:

            payment_id = p["payment_id"]

            url = f"https://api.nowpayments.io/v1/payment/{payment_id}"

            headers = {"x-api-key": NOWPAY_API_KEY}

            r = requests.get(url, headers=headers).json()

            if r["payment_status"] == "finished":

                users.update_one(
                    {"user_id": p["user_id"]},
                    {"$inc": {"balance": p["amount"]}}
                )

                payments.update_one(
                    {"payment_id": payment_id},
                    {"$set": {"status": "done"}}
                )

                bot.send_message(
                    p["user_id"],
                    f"✅ Crypto payment received\n💰 {p['amount']}$ added"
                )

        time.sleep(30)


import threading
threading.Thread(target=check_payments).start()


print("Bot running...")
bot.infinity_polling()
