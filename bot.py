import telebot
from telebot import types
import requests

from config import BOT_TOKEN, ADMIN_ID, NOWPAY_API_KEY
from database import get_user, users

bot = telebot.TeleBot(BOT_TOKEN)


# START
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    user = get_user(user_id)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $

Choose option 👇
"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Deposit")
    markup.add("💳 Withdraw")
    markup.add("👤 Profile")

    bot.send_message(message.chat.id, text, reply_markup=markup)


# PROFILE
@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    user_id = message.from_user.id
    user = get_user(user_id)

    text = f"""
👤 PROFILE

🆔 ID: {user_id}
💰 Balance: {user['balance']} $
"""

    bot.send_message(message.chat.id, text)


# DEPOSIT MENU
@bot.message_handler(func=lambda m: m.text == "💰 Deposit")
def deposit(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⭐ Stars Deposit")
    markup.add("💵 Crypto Deposit")
    markup.add("🔙 Back")

    bot.send_message(message.chat.id, "💰 Choose deposit method:", reply_markup=markup)


# STARS
@bot.message_handler(func=lambda m: m.text == "⭐ Stars Deposit")
def stars(message):

    bot.send_message(message.chat.id, "⭐ Stars payment coming soon")


# CRYPTO DEPOSIT
@bot.message_handler(func=lambda m: m.text == "💵 Crypto Deposit")
def crypto(message):

    bot.send_message(message.chat.id, "💰 Send amount in USD (example: 10)")


@bot.message_handler(func=lambda m: m.text.isdigit())
def create_payment(message):

    amount = float(message.text)

    headers = {
        "x-api-key": NOWPAY_API_KEY
    }

    data = {
        "price_amount": amount,
        "price_currency": "usd",
        "pay_currency": "usdttrc20"
    }

    r = requests.post(
        "https://api.nowpayments.io/v1/payment",
        json=data,
        headers=headers
    )

    res = r.json()

    pay_address = res["pay_address"]

    bot.send_message(
        message.chat.id,
        f"""
💰 SEND PAYMENT

Amount: {amount} USD
Address:

`{pay_address}`

After payment bot will auto detect.
""",
        parse_mode="Markdown"
    )


# WITHDRAW
@bot.message_handler(func=lambda m: m.text == "💳 Withdraw")
def withdraw(message):

    bot.send_message(message.chat.id, "💳 Withdraw system coming soon")


# BACK
@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def back(message):
    start(message)


bot.infinity_polling()
