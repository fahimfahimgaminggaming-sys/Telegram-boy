import telebot
import requests
from telebot import types
from config import BOT_TOKEN, NOWPAY_API_KEY
from database import get_user

bot = telebot.TeleBot(BOT_TOKEN)

START COMMAND

@bot.message_handler(commands=['start'])
def start(message):

user = get_user(message.from_user.id)

text = f"""

👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $

Choose option 👇
"""

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add("💰 Deposit")
markup.add("👤 Profile")

bot.send_message(message.chat.id, text, reply_markup=markup)

PROFILE

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

user = get_user(message.from_user.id)

bot.send_message(
    message.chat.id,
    f"""

👤 USER PROFILE

🆔 ID: {message.from_user.id}
💰 Balance: {user['balance']} $
"""
)

DEPOSIT MENU

@bot.message_handler(func=lambda m: m.text == "💰 Deposit")
def deposit_menu(message):

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add("⭐ Stars Deposit")
markup.add("💰 Crypto Deposit")
markup.add("⬅ Back")

bot.send_message(
    message.chat.id,
    "💰 Choose deposit method:",
    reply_markup=markup
)

BACK BUTTON

@bot.message_handler(func=lambda m: m.text == "⬅ Back")
def back(message):
start(message)

STARS PAYMENT

@bot.message_handler(func=lambda m: m.text == "⭐ Stars Deposit")
def stars_payment(message):

prices = [types.LabeledPrice("Stars Deposit", 100)]

bot.send_invoice(
    message.chat.id,
    title="Stars Deposit",
    description="Deposit using Telegram Stars",
    provider_token="",
    currency="XTR",
    prices=prices,
    start_parameter="stars-deposit",
    payload="stars-deposit"
)

STARS CHECKOUT

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

STARS SUCCESS

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):

bot.send_message(
    message.chat.id,
    "⭐ Payment successful!\nBalance will be added soon."
)

CRYPTO DEPOSIT

@bot.message_handler(func=lambda m: m.text == "💰 Crypto Deposit")
def crypto_deposit(message):

bot.send_message(
    message.chat.id,
    "💰 Send deposit amount in USD\nExample: 5"
)

CREATE CRYPTO PAYMENT LINK

@bot.message_handler(func=lambda m: m.text.isdigit())
def create_payment(message):

amount = float(message.text)

headers = {
    "x-api-key": NOWPAY_API_KEY,
    "Content-Type": "application/json"
}

data = {
    "price_amount": amount,
    "price_currency": "usd"
}

r = requests.post(
    "https://api.nowpayments.io/v1/invoice",
    json=data,
    headers=headers
)

res = r.json()

payment_url = res["invoice_url"]

bot.send_message(
    message.chat.id,
    f"""

💰 CRYPTO PAYMENT

Amount: {amount} USD

Pay here:
{payment_url}

After payment bot will auto detect.
"""
)

bot.infinity_polling()
