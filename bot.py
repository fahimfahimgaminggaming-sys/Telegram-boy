import telebot
import requests
from telebot import types
from config import BOT_TOKEN, NOWPAY_API_KEY
from database import get_user, update_balance

bot = telebot.TeleBot(BOT_TOKEN)

# --------- MAIN MENU ----------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📥 Deposit", "👤 Profile")
    markup.row("💵 Balance")
    return markup

# --------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    text = f"""
👋 Welcome {message.from_user.first_name}

💵 Balance: {user['balance']} $

Choose option 👇
"""
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

# --------- PROFILE ----------
@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):
    user = get_user(message.from_user.id)

    text = f"""
👤 PROFILE

🆔 ID: {message.from_user.id}
💵 Balance: {user['balance']} $
"""
    bot.send_message(message.chat.id, text)

# --------- BALANCE ----------
@bot.message_handler(func=lambda m: m.text == "💵 Balance")
def balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💵 Your balance: {user['balance']} $")

# --------- DEPOSIT MENU ----------
@bot.message_handler(func=lambda m: m.text == "📥 Deposit")
def deposit(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("⭐ Stars payment")
    markup.row("💰 Crypto payment link")
    markup.row("⬅ Back")

    bot.send_message(message.chat.id, "Choose deposit method:", reply_markup=markup)

# --------- BACK ----------
@bot.message_handler(func=lambda m: m.text == "⬅ Back")
def back(message):
    start(message)

# --------- STARS PAYMENT ----------
@bot.message_handler(func=lambda m: m.text == "⭐ Stars payment")
def stars(message):

    prices = [types.LabeledPrice(label="Deposit", amount=100)]  # 1 Star = 100 units

    bot.send_invoice(
        message.chat.id,
        title="Stars Deposit",
        description="Deposit using Telegram Stars",
        invoice_payload="stars-deposit",
        provider_token="",
        currency="XTR",
        prices=prices
    )

# --------- PRECHECKOUT ----------
@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --------- SUCCESSFUL PAYMENT ----------
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):

    amount = message.successful_payment.total_amount / 100
    update_balance(message.from_user.id, amount)

    bot.send_message(
        message.chat.id,
        f"✅ Payment received\n💰 {amount} added to your balance."
    )

# --------- CRYPTO PAYMENT ----------
@bot.message_handler(func=lambda m: m.text == "💰 Crypto payment link")
def crypto(message):
    msg = bot.send_message(message.chat.id, "Send amount in USD (example: 10)")
    bot.register_next_step_handler(msg, create_crypto_payment)

def create_crypto_payment(message):

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

        pay_address = r["pay_address"]
        pay_amount = r["pay_amount"]

        text = f"""
💰 SEND PAYMENT

Amount: {pay_amount} USDT
Address:
{pay_address}

After payment press:
✅ I Paid
"""

        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✅ I Paid", callback_data="check_payment")
        markup.add(btn)

        bot.send_message(message.chat.id, text, reply_markup=markup)

    except:
        bot.send_message(message.chat.id, "❌ Invalid amount")

# --------- AUTO PAYMENT CHECK ----------
@bot.callback_query_handler(func=lambda call: call.data == "check_payment")
def check(call):
    bot.answer_callback_query(call.id, "⏳ Checking payment...")

    # demo auto detect message
    bot.send_message(
        call.message.chat.id,
        "🤖 Payment will be auto detected after blockchain confirmation."
    )

# --------- RUN BOT ----------
print("Bot running...")
bot.infinity_polling()
