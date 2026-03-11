import telebot
from telebot import types
import time
import random

from config import BOT_TOKEN, ADMIN_ID
from database import get_user, add_balance, remove_balance, users

bot = telebot.TeleBot(BOT_TOKEN)

tasks = {}
task_id = 1
completed = {}
referrals = {}
daily_bonus = {}

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    user = get_user(message.from_user.id)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $

Choose option 👇
"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("👤 Profile","💰 Balance")
    markup.row("📥 Deposit","📋 Tasks")
    markup.row("👥 Referral","🎁 Bonus")
    markup.row("🏆 Leaderboard","📊 Statistics")

    bot.send_message(message.chat.id,text,reply_markup=markup)


# ================= PROFILE =================

@bot.message_handler(func=lambda m: m.text=="👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    bot.send_message(message.chat.id,f"""
👤 USER PROFILE

🆔 ID: {message.from_user.id}
💰 Balance: {user['balance']} $
""")


# ================= BALANCE =================

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def balance(message):

    user = get_user(message.from_user.id)

    bot.send_message(message.chat.id,f"""
💰 Your Balance

{user['balance']} $
""")


# ================= DEPOSIT MENU =================

@bot.message_handler(func=lambda m: m.text=="📥 Deposit")
def deposit(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("⭐ Stars deposit","💰 Crypto deposit")
    markup.row("📊 Deposit history","⬅ Back")

    bot.send_message(message.chat.id,"Choose deposit method",reply_markup=markup)


# ================= STARS =================

@bot.message_handler(func=lambda m: m.text=="⭐ Stars deposit")
def stars(message):

    bot.send_message(message.chat.id,"Send stars amount\n1 ⭐ = 0.013$")


# ================= CRYPTO =================

@bot.message_handler(func=lambda m: m.text=="💰 Crypto deposit")
def crypto(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("USDT BEP20","BTC")
    markup.row("ETH","TRX")
    markup.row("⬅ Back")

    bot.send_message(message.chat.id,"Choose crypto",reply_markup=markup)


# ================= HISTORY =================

@bot.message_handler(func=lambda m: m.text=="📊 Deposit history")
def history(message):

    bot.send_message(message.chat.id,"📊 No deposits yet")


# ================= TASK LIST =================

@bot.message_handler(func=lambda m: m.text=="📋 Tasks")
def tasklist(message):

    if not tasks:

        bot.send_message(message.chat.id,"❌ No tasks available")
        return

    for tid,data in tasks.items():

        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton("🔗 Join",url=f"https://t.me/{data['channel'].replace('@','')}"))

        markup.add(types.InlineKeyboardButton("✅ Verify",callback_data=f"verify_{tid}"))

        bot.send_message(message.chat.id,f"""
📢 Task

Channel: {data['channel']}
Reward: {data['reward']} $
""",reply_markup=markup)


# ================= VERIFY =================

@bot.callback_query_handler(func=lambda call: call.data.startswith("verify"))
def verify(call):

    tid = int(call.data.split("_")[1])

    if tid not in tasks:
        return

    uid = call.from_user.id

    if uid not in completed:
        completed[uid] = set()

    if tid in completed[uid]:

        bot.answer_callback_query(call.id,"Already done")
        return

    task = tasks[tid]

    try:

        member = bot.get_chat_member(task['channel'],uid)

        if member.status not in ["member","administrator","creator"]:

            bot.answer_callback_query(call.id,"Join channel first")
            return

        add_balance(uid,task['reward'])

        completed[uid].add(tid)

        bot.answer_callback_query(call.id,"Reward added")

        bot.send_message(uid,f"💰 You earned {task['reward']} $")

    except:

        bot.answer_callback_query(call.id,"Verification failed")


# ================= REFERRAL =================

@bot.message_handler(func=lambda m: m.text=="👥 Referral")
def referral(message):

    uid = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    total = referrals.get(uid,0)

    bot.send_message(uid,f"""
👥 Referral Program

Invite friends

🔗 {link}

Referrals: {total}
""")


# ================= BONUS =================

@bot.message_handler(func=lambda m: m.text=="🎁 Bonus")
def bonus(message):

    uid = message.from_user.id

    now = time.time()

    if uid in daily_bonus:

        if now-daily_bonus[uid] < 86400:

            bot.send_message(uid,"Come tomorrow")
            return

    reward = round(random.uniform(0.01,0.05),2)

    add_balance(uid,reward)

    daily_bonus[uid] = now

    bot.send_message(uid,f"🎁 Bonus\n+{reward}$")


# ================= LEADERBOARD =================

@bot.message_handler(func=lambda m: m.text=="🏆 Leaderboard")
def leaderboard(message):

    top = sorted(users.find(),key=lambda x:x['balance'],reverse=True)[:10]

    text = "🏆 Top Users\n\n"

    i = 1

    for u in top:

        text += f"{i}. {u['balance']} $\n"

        i+=1

    bot.send_message(message.chat.id,text)


# ================= STATS =================

@bot.message_handler(func=lambda m: m.text=="📊 Statistics")
def stats(message):

    user = get_user(message.from_user.id)

    bot.send_message(message.chat.id,f"""
📊 Your Stats

💰 Balance: {user['balance']} $
""")


# ================= ADMIN PROMOTE =================

@bot.message_handler(commands=['addtask'])
def addtask(message):

    if message.from_user.id != ADMIN_ID:
        return

    global task_id

    try:

        _, channel, reward = message.text.split()

        reward = float(reward)

        tasks[task_id] = {
            "channel":channel,
            "reward":reward
        }

        bot.send_message(message.chat.id,"Task added")

        task_id +=1

    except:

        bot.send_message(message.chat.id,"Usage:\n/addtask @channel 0.01")


print("Bot Started...")

bot.infinity_polling(skip_pending=True)
