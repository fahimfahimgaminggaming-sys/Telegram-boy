import telebot
from config import BOT_TOKEN
from database import get_user

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id
    user = get_user(user_id)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $

Choose option 👇
"""

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👤 Profile")

    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    text = f"""
👤 PROFILE

🆔 ID: {message.from_user.id}
💰 Balance: {user['balance']} $
"""

    bot.send_message(message.chat.id, text)


print("Bot Running...")
bot.infinity_polling()
