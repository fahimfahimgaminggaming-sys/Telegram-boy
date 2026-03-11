import telebot
from telebot import types
import time
import random

from config import BOT_TOKEN, ADMIN_ID
from database import *

bot = telebot.TeleBot(BOT_TOKEN)

FORCE_CHANNELS = [
"@Task_Updates_Group",
"@Crypto_Tech_Zone",
"@AIRDROP_OFFICIALBD20"
]

# ================= JOIN CHECK =================

def check_join(user_id):

    for ch in FORCE_CHANNELS:

        try:

            member = bot.get_chat_member(ch,user_id)

            if member.status not in ["member","administrator","creator"]:
                return False

        except:
            return False

    return True


# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    uid = message.from_user.id

    if not check_join(uid):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
            "📢 Join Updates",
            url="https://t.me/Task_Updates_Group")
        )

        markup.add(
            types.InlineKeyboardButton(
            "📢 Crypto Tech",
            url="https://t.me/Crypto_Tech_Zone")
        )

        markup.add(
            types.InlineKeyboardButton(
            "📢 Airdrop",
            url="https://t.me/AIRDROP_OFFICIALBD20")
        )

        markup.add(
            types.InlineKeyboardButton(
            "✅ Check Join",
            callback_data="checkjoin")
        )

        bot.send_message(
        uid,
        "❌ Join all channels first",
        reply_markup=markup
        )

        return

    user = get_user(uid)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("👤 Profile","💰 Balance")
    markup.row("📥 Deposit","📋 Tasks")
    markup.row("👥 Referral","🎁 Bonus")
    markup.row("🏆 Leaderboard","📊 Statistics")

    bot.send_message(
    uid,
    f"👋 Welcome\n\n💰 Balance: {user['balance']} $",
    reply_markup=markup
    )


# ================= JOIN BUTTON =================

@bot.callback_query_handler(func=lambda c:c.data=="checkjoin")
def check(call):

    if check_join(call.from_user.id):

        start(call.message)

    else:

        bot.answer_callback_query(
        call.id,
        "Join all channels first"
  )
      # ================= PROFILE =================

@bot.message_handler(func=lambda m:m.text=="👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    bot.send_message(
    message.chat.id,
    f"""
👤 USER PROFILE

ID: {message.from_user.id}
Balance: {user['balance']} $
"""
    )


# ================= BALANCE =================

@bot.message_handler(func=lambda m:m.text=="💰 Balance")
def balance(message):

    user = get_user(message.from_user.id)

    bot.send_message(
    message.chat.id,
    f"💰 Balance: {user['balance']} $"
    )


# ================= DEPOSIT MENU =================

@bot.message_handler(func=lambda m:m.text=="📥 Deposit")
def deposit(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("⭐ Stars Deposit","💰 Crypto Deposit")
    markup.row("📊 Deposit History")

    bot.send_message(
    message.chat.id,
    "Choose deposit method",
    reply_markup=markup
    )


# ================= STARS =================

@bot.message_handler(func=lambda m:m.text=="⭐ Stars Deposit")
def stars(message):

    bot.send_message(
    message.chat.id,
    "Send stars amount\n\n1 ⭐ = 0.013$"
    )


# ================= CRYPTO =================

@bot.message_handler(func=lambda m:m.text=="💰 Crypto Deposit")
def crypto(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("USDT","BTC")
    markup.row("ETH","TRX")

    bot.send_message(
    message.chat.id,
    "Choose crypto",
    reply_markup=markup
)
  # ================= TASK LIST =================

@bot.message_handler(func=lambda m:m.text=="📋 Tasks")
def tasks(message):

    task_list = get_tasks()

    if not task_list:

        bot.send_message(message.chat.id,"❌ No tasks")
        return

    for task in task_list:

        markup = types.InlineKeyboardMarkup()

        markup.add(
        types.InlineKeyboardButton(
        "🔗 Join Channel",
        url=f"https://t.me/{task['channel'].replace('@','')}")
        )

        markup.add(
        types.InlineKeyboardButton(
        "✅ Verify",
        callback_data=f"verify_{task['_id']}")
        )

        bot.send_message(
        message.chat.id,
        f"""
📢 Task

Channel: {task['channel']}
Reward: {task['reward']} $
""",
        reply_markup=markup
        )


# ================= VERIFY =================

@bot.callback_query_handler(func=lambda c:c.data.startswith("verify"))
def verify(call):

    tid = call.data.split("_")[1]

    task = get_task(tid)

    uid = call.from_user.id

    try:

        member = bot.get_chat_member(task["channel"],uid)

        if member.status not in ["member","administrator","creator"]:

            bot.answer_callback_query(call.id,"Join first")
            return

        add_balance(uid,task["reward"])

        bot.send_message(
        uid,
        f"💰 You earned {task['reward']} $"
        )

    except:

        bot.answer_callback_query(call.id,"Error")
      # ================= REFERRAL =================

@bot.message_handler(func=lambda m:m.text=="👥 Referral")
def referral(message):

    uid = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    bot.send_message(
    uid,
    f"""
👥 Referral Program

Invite friends

🔗 {link}
"""
    )


# ================= BONUS =================

bonus_db = {}

@bot.message_handler(func=lambda m:m.text=="🎁 Bonus")
def bonus(message):

    uid = message.from_user.id

    now = time.time()

    if uid in bonus_db:

        if now - bonus_db[uid] < 86400:

            bot.send_message(uid,"Come tomorrow")
            return

    reward = round(random.uniform(0.01,0.05),2)

    add_balance(uid,reward)

    bonus_db[uid] = now

    bot.send_message(
    uid,
    f"🎁 Bonus\n+{reward}$"
    )


# ================= ADMIN ADD TASK =================

@bot.message_handler(commands=['addtask'])
def addtask(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        _,channel,reward = message.text.split()

        reward = float(reward)

        create_task(channel,reward)

        bot.send_message(
        message.chat.id,
        "✅ Task added"
        )

    except:

        bot.send_message(
        message.chat.id,
        "Usage:\n/addtask @channel 0.01"
        )


print("Bot Started...")

bot.infinity_polling(skip_pending=True)
      
