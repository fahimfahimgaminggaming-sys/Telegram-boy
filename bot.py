import telebot
import requests
from config import BOT_TOKEN, NOWPAY_API_KEY
from database import get_user

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):

    user = get_user(message.from_user.id)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $

Choose option 👇
"""

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💰 Deposit")
    markup.add("👤 Profile")

    bot.send_message(message.chat.id, text, reply_markup=markup)
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
  @bot.message_handler(func=lambda m: m.text == "💰 Deposit")
def deposit(message):

    bot.send_message(
        message.chat.id,
        "💰 Send amount in USD\n\nExample: 10"
    )
  @bot.message_handler(func=lambda m: m.text.isdigit())
def create_payment(message):

    amount = float(message.text)

    headers = {
        "x-api-key": NOWPAY_API_KEY,
        "Content-Type": "application/json"
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
    pay_amount = res["pay_amount"]

    bot.send_message(
        message.chat.id,
        f"""
💰 PAYMENT CREATED

Amount: {amount} USD

Send:
{pay_amount} USDT

Address:
{pay_address}

Network: TRC20
"""
    )
  bot.infinity_polling()
