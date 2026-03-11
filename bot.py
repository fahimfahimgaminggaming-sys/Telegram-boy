import telebot
from telebot import types
import time
import random
import requests

from config import BOT_TOKEN, ADMIN_ID
from database import *

bot = telebot.TeleBot(BOT_TOKEN)

# ================= SETTINGS =================

PC_COIN_PRICE = 0.013

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
        callback_data="check_join")
        )

        bot.send_message(
        uid,
        "❌ Please join all channels first",
        reply_markup=markup
        )

        return

    user = get_user(uid)

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

    bot.send_message(
    uid,
    text,
    reply_markup=markup
    )


# ================= CHECK JOIN =================

@bot.callback_query_handler(func=lambda c:c.data=="check_join")
def check(call):

    if check_join(call.from_user.id):

        bot.answer_callback_query(
        call.id,
        "Join verified"
        )

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

🆔 ID: {message.from_user.id}

💰 Balance: {user['balance']} $

⭐ PC Coin Rate:
1 Coin = {PC_COIN_PRICE}$
"""
    )


# ================= BALANCE =================

@bot.message_handler(func=lambda m:m.text=="💰 Balance")
def balance(message):

    user = get_user(message.from_user.id)

    bot.send_message(
    message.chat.id,
    f"""
💰 Your Balance

{user['balance']} $
"""
    )


# ================= BACK =================

@bot.message_handler(func=lambda m:m.text=="⬅ Back")
def back(message):

    start(message)
  # ================= STARS DEPOSIT =================

@bot.message_handler(func=lambda m: m.text=="⭐ Stars Deposit")
def stars_deposit(message):

    bot.send_message(
        message.chat.id,
        """
⭐ Telegram Stars Deposit

Send how many PC Coins you want.

1 PC Coin = 1 ⭐
Minimum = 1
"""
    )

    bot.register_next_step_handler(message,create_star_invoice)


# ================= CREATE INVOICE =================

def create_star_invoice(message):

    try:

        amount = int(message.text)

        if amount < 1:

            bot.send_message(message.chat.id,"Minimum 1 PC Coin")
            return

        prices = [types.LabeledPrice("PC Coin", amount)]

        bot.send_invoice(
            chat_id=message.chat.id,
            title="PC Coin Deposit",
            description=f"Buy {amount} PC Coins",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="stars-deposit",
            payload=f"pc_{amount}"
        )

    except:

        bot.send_message(message.chat.id,"Send number only")


# ================= PRE CHECKOUT =================

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):

    bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True
    )


# ================= PAYMENT SUCCESS =================

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):

    uid = message.from_user.id

    stars = message.successful_payment.total_amount

    usd = stars * 0.013

    add_balance(uid,usd)

    bot.send_message(
        uid,
        f"""
⭐ Stars Payment Success

Stars Paid: {stars}

💰 Balance Added: {usd}$

Thank you for deposit
"""
  )
  # ================= CRYPTO DEPOSIT MENU =================

@bot.message_handler(func=lambda m: m.text=="💰 Crypto Deposit")
def crypto_menu(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("🪙 CryptoBot Pay")
    markup.row("🚀 xRocket Pay")
    markup.row("🌐 NOWPayments")
    markup.row("📊 Deposit History")
    markup.row("⬅ Back")

    bot.send_message(
        message.chat.id,
        "Choose crypto payment method",
        reply_markup=markup
    )


# ================= CRYPTOBOT PAYMENT =================

CRYPTOBOT_CREATE = "https://pay.crypt.bot/api/createInvoice"

@bot.message_handler(func=lambda m: m.text=="🪙 CryptoBot Pay")
def cryptobot(message):

    bot.send_message(
        message.chat.id,
        "Enter deposit amount in USD\nMinimum 0.5$"
    )

    bot.register_next_step_handler(message, cryptobot_invoice)


def cryptobot_invoice(message):

    try:

        amount = float(message.text)

        if amount < 0.5:

            bot.send_message(message.chat.id,"Minimum deposit 0.5$")
            return

        data = {
            "asset":"USDT",
            "amount":amount
        }

        headers = {
            "Crypto-Pay-API-Token":CRYPTOBOT_TOKEN
        }

        r = requests.post(
            CRYPTOBOT_CREATE,
            json=data,
            headers=headers
        )

        result = r.json()

        pay_url = result["result"]["pay_url"]

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "💳 Pay Now",
                url=pay_url
            )
        )

        bot.send_message(
            message.chat.id,
            f"💰 Deposit {amount}$",
            reply_markup=markup
        )

    except:

        bot.send_message(message.chat.id,"Payment error")


# ================= XROCKET PAYMENT =================

@bot.message_handler(func=lambda m: m.text=="🚀 xRocket Pay")
def xrocket(message):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "💳 Pay via xRocket",
            url="https://t.me/xrocket"
        )
    )

    bot.send_message(
        message.chat.id,
        """
🚀 xRocket Payment

Click button to open wallet
""",
        reply_markup=markup
    )


# ================= NOWPAYMENTS =================

NOWPAY_CREATE = "https://api.nowpayments.io/v1/payment"

@bot.message_handler(func=lambda m: m.text=="🌐 NOWPayments")
def nowpayments(message):

    bot.send_message(
        message.chat.id,
        "Enter deposit amount in USD"
    )

    bot.register_next_step_handler(message, create_nowpayment)


def create_nowpayment(message):

    try:

        amount = float(message.text)

        data = {
            "price_amount":amount,
            "price_currency":"usd",
            "pay_currency":"usdt"
        }

        headers = {
            "x-api-key":NOWPAY_API_KEY
        }

        r = requests.post(
            NOWPAY_CREATE,
            json=data,
            headers=headers
        )

        result = r.json()

        pay_url = result["invoice_url"]

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "💳 Pay Now",
                url=pay_url
            )
        )

        bot.send_message(
            message.chat.id,
            "Open payment link",
            reply_markup=markup
        )

    except:

        bot.send_message(message.chat.id,"Payment error")


# ================= DEPOSIT HISTORY =================

deposit_history = {}

@bot.message_handler(func=lambda m: m.text=="📊 Deposit History")
def history(message):

    uid = message.from_user.id

    if uid not in deposit_history:

        bot.send_message(message.chat.id,"No deposits yet")
        return

    text = "📊 Deposit History\n\n"

    for h in deposit_history[uid]:

        text += f"{h}\n"

    bot.send_message(message.chat.id,text)
  # ================= TASK DATABASE =================

tasks = {}
task_counter = 1
completed_tasks = {}

# ================= VIEW TASKS =================

@bot.message_handler(func=lambda m: m.text == "📋 Tasks")
def view_tasks(message):

    uid = message.from_user.id

    if not tasks:

        bot.send_message(uid,"❌ No tasks available")
        return

    send_task(uid,0)


# ================= SEND TASK =================

def send_task(uid,index):

    task_list = list(tasks.items())

    if not task_list:

        bot.send_message(uid,"❌ No tasks available")
        return

    if index >= len(task_list):

        bot.send_message(uid,"✅ No more tasks")
        return

    tid,task = task_list[index]

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "🔗 Join Channel",
            url=f"https://t.me/{task['channel'].replace('@','')}"
        )
    )

    markup.add(
        types.InlineKeyboardButton(
            "⏭ Skip",
            callback_data=f"skip_{index+1}"
        ),
        types.InlineKeyboardButton(
            "✅ Verify +0.01$",
            callback_data=f"verify_{tid}_{index}"
        )
    )

    bot.send_message(
        uid,
        f"""
📢 Task

Channel: {task['channel']}

💰 Reward: {task['reward']} $
""",
        reply_markup=markup
    )


# ================= SKIP TASK =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def skip_task(call):

    index = int(call.data.split("_")[1])

    bot.answer_callback_query(call.id,"⏭ Task skipped")

    send_task(call.from_user.id,index)


# ================= VERIFY TASK =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("verify_"))
def verify_task(call):

    data = call.data.split("_")

    tid = int(data[1])
    index = int(data[2])

    uid = call.from_user.id

    if tid not in tasks:

        bot.answer_callback_query(call.id,"Task not found")
        return

    if uid not in completed_tasks:
        completed_tasks[uid] = set()

    if tid in completed_tasks[uid]:

        bot.answer_callback_query(call.id,"Already completed")
        return

    task = tasks[tid]

    try:

        member = bot.get_chat_member(task["channel"],uid)

        if member.status not in ["member","administrator","creator"]:

            bot.answer_callback_query(call.id,"❌ Join channel first")
            return

        add_balance(uid,task["reward"])

        completed_tasks[uid].add(tid)

        bot.answer_callback_query(call.id,"✅ Reward added")

        bot.send_message(
            uid,
            f"💰 You earned {task['reward']} $"
        )

        send_task(uid,index+1)

    except:

        bot.answer_callback_query(call.id,"❌ Verification failed")
      # ================= ADMIN ADD TASK =================

@bot.message_handler(commands=['addtask'])
def add_task(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "Send channel username\nExample:\n@channel"
    )

    bot.register_next_step_handler(message,get_channel)


# ================= GET CHANNEL =================

def get_channel(message):

    channel = message.text.strip()

    try:

        bot_member = bot.get_chat_member(channel, bot.get_me().id)

        if bot_member.status not in ["administrator","creator"]:

            bot.send_message(
                message.chat.id,
                "❌ Bot must be admin in channel"
            )
            return

    except:

        bot.send_message(message.chat.id,"❌ Invalid channel")
        return

    bot.send_message(
        message.chat.id,
        "💰 Reward per user\nExample: 0.01"
    )

    bot.register_next_step_handler(
        message,
        lambda m:get_reward(m,channel)
    )


# ================= GET REWARD =================

def get_reward(message,channel):

    try:

        reward = float(message.text)

        if reward < 0.01:

            bot.send_message(
                message.chat.id,
                "❌ Minimum reward 0.01$"
            )
            return

    except:

        bot.send_message(message.chat.id,"❌ Invalid reward")
        return

    bot.send_message(
        message.chat.id,
        "👥 How many members?"
    )

    bot.register_next_step_handler(
        message,
        lambda m:finalize_task(m,channel,reward)
    )


# ================= FINALIZE TASK =================

def finalize_task(message,channel,reward):

    global task_counter

    try:

        members = int(message.text)

        if members <= 0:
            raise ValueError

    except:

        bot.send_message(message.chat.id,"❌ Invalid number")
        return

    tasks[task_counter] = {

        "channel":channel,
        "reward":reward,
        "remaining":members

    }

    bot.send_message(
        message.chat.id,
        f"""
✅ Promotion created

ID: {task_counter}

Channel: {channel}
Reward: {reward}$
Members: {members}
"""
    )

    task_counter += 1


# ================= MY PROMOTIONS =================

@bot.message_handler(commands=['mytasks'])
def my_tasks(message):

    if message.from_user.id != ADMIN_ID:
        return

    if not tasks:

        bot.send_message(
            message.chat.id,
            "❌ No active promotions"
        )
        return

    for tid,task in tasks.items():

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "🛑 Cancel Promotion",
                callback_data=f"cancel_{tid}"
            )
        )

        bot.send_message(
            message.chat.id,
            f"""
📢 Promotion ID: {tid}

📺 Channel: {task['channel']}
💰 Reward: {task['reward']}$
👥 Remaining: {task['remaining']}
""",
            reply_markup=markup
        )


# ================= CANCEL PROMOTION =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("cancel_"))
def cancel_promotion(call):

    tid = int(call.data.split("_")[1])

    if call.from_user.id != ADMIN_ID:
        return

    if tid not in tasks:

        bot.answer_callback_query(
            call.id,
            "Task not found"
        )
        return

    del tasks[tid]

    bot.answer_callback_query(
        call.id,
        "Promotion cancelled"
    )

    bot.send_message(
        call.from_user.id,
        f"🛑 Promotion {tid} cancelled"
      )
  # ================= REFERRAL DATABASE =================

referrals = {}
daily_bonus = {}

# ================= START WITH REFERRAL =================

@bot.message_handler(commands=['start'])
def start(message):

    uid = message.from_user.id

    get_user(uid)

    if message.text != "/start":

        try:

            ref = int(message.text.split()[1])

            if ref != uid:

                if ref not in referrals:
                    referrals[ref] = 0

                referrals[ref] += 1

                reward = 0.01

                add_balance(ref,reward)

                bot.send_message(
                    ref,
                    f"""
👥 New referral joined

💰 Reward: {reward}$
📊 Total referrals: {referrals[ref]}
"""
                )

        except:
            pass

    user = get_user(uid)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Balance: {user['balance']} $
"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("👤 Profile","💰 Balance")
    markup.row("📥 Deposit","📋 Tasks")
    markup.row("👥 Referral","🎁 Bonus")
    markup.row("🏆 Leaderboard","📊 Statistics")

    bot.send_message(
        uid,
        text,
        reply_markup=markup
    )


# ================= REFERRAL LINK =================

@bot.message_handler(func=lambda m:m.text=="👥 Referral")
def referral(message):

    uid = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    total = referrals.get(uid,0)

    bot.send_message(
        uid,
        f"""
👥 Referral Program

Invite friends and earn 💰

🔗 Your Link:
{link}

📊 Referrals: {total}

💰 Reward per referral: 0.01$
"""
    )


# ================= DAILY BONUS =================

@bot.message_handler(func=lambda m:m.text=="🎁 Bonus")
def bonus(message):

    uid = message.from_user.id

    now = time.time()

    if uid in daily_bonus:

        if now - daily_bonus[uid] < 86400:

            bot.send_message(uid,"⏳ Come back tomorrow")
            return

    reward = round(random.uniform(0.01,0.03),3)

    add_balance(uid,reward)

    daily_bonus[uid] = now

    bot.send_message(
        uid,
        f"""
🎁 Daily Bonus

💰 You received: {reward}$
"""
    )


# ================= LEADERBOARD =================

@bot.message_handler(func=lambda m:m.text=="🏆 Leaderboard")
def leaderboard(message):

    top = sorted(
        users.find(),
        key=lambda x:x['balance'],
        reverse=True
    )[:10]

    text = "🏆 Top Users\n\n"

    i = 1

    for u in top:

        text += f"{i}. {u['balance']} $\n"

        i += 1

    bot.send_message(
        message.chat.id,
        text
    )


# ================= STATISTICS =================

@bot.message_handler(func=lambda m:m.text=="📊 Statistics")
def statistics(message):

    total_users = users.count_documents({})

    bot.send_message(
        message.chat.id,
        f"""
📊 Bot Statistics

👥 Users: {total_users}
📢 Tasks: {len(tasks)}
"""
  )
  # ================= ADMIN PANEL =================

banned_users = set()

@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("👥 Total Users","📊 Bot Stats")
    markup.row("📢 Broadcast","🚫 Ban User")
    markup.row("⬅ Back")

    bot.send_message(
        message.chat.id,
        "👑 Admin Panel",
        reply_markup=markup
    )


# ================= TOTAL USERS =================

@bot.message_handler(func=lambda m: m.text=="👥 Total Users")
def total_users(message):

    if message.from_user.id != ADMIN_ID:
        return

    count = users.count_documents({})

    bot.send_message(
        message.chat.id,
        f"👥 Total users: {count}"
    )


# ================= BOT STATS =================

@bot.message_handler(func=lambda m: m.text=="📊 Bot Stats")
def bot_stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    total_users = users.count_documents({})

    bot.send_message(
        message.chat.id,
        f"""
📊 Bot Statistics

👥 Users: {total_users}
📢 Active Tasks: {len(tasks)}
"""
    )


# ================= BROADCAST =================

@bot.message_handler(func=lambda m: m.text=="📢 Broadcast")
def broadcast_start(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "Send message to broadcast"
    )

    bot.register_next_step_handler(
        message,
        broadcast_send
    )


def broadcast_send(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text

    sent = 0

    for u in users.find():

        uid = u["user_id"]

        try:

            bot.send_message(uid,text)

            sent += 1

        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ Broadcast sent to {sent} users"
    )


# ================= BAN USER =================

@bot.message_handler(func=lambda m: m.text=="🚫 Ban User")
def ban_user_start(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "Send user ID to ban"
    )

    bot.register_next_step_handler(
        message,
        ban_user
    )


def ban_user(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        uid = int(message.text)

        banned_users.add(uid)

        bot.send_message(
            message.chat.id,
            f"🚫 User {uid} banned"
        )

    except:

        bot.send_message(
            message.chat.id,
            "Invalid user id"
        )


# ================= BAN CHECK =================

@bot.message_handler(func=lambda m: True)
def ban_check(message):

    if message.from_user.id in banned_users:

        bot.send_message(
            message.chat.id,
            "🚫 You are banned from this bot"
        )

        return
      # ================= DEPOSIT HISTORY =================

deposit_history = {}

def add_deposit(uid,amount,method):

    if uid not in deposit_history:
        deposit_history[uid] = []

    deposit_history[uid].append(
        f"{method} → {amount}$"
    )


@bot.message_handler(func=lambda m:m.text=="📊 Deposit History")
def deposit_history_view(message):

    uid = message.from_user.id

    if uid not in deposit_history:

        bot.send_message(
            message.chat.id,
            "📜 No deposits yet"
        )
        return

    text = "📜 Your Deposits\n\n"

    for h in deposit_history[uid]:

        text += f"{h}\n"

    bot.send_message(
        message.chat.id,
        text
    )


# ================= ANTI FRAUD =================

left_users = {}

def check_left(uid,channel):

    try:

        member = bot.get_chat_member(channel,uid)

        if member.status not in ["member","administrator","creator"]:

            if uid not in left_users:
                left_users[uid] = []

            left_users[uid].append(channel)

            remove_balance(uid,0.01)

            return True

    except:
        pass

    return False


# ================= AUTO TASK POST =================

TASK_GROUP = "@Task_Updates_Group"

def post_task_group(channel,reward):

    try:

        bot.send_message(
            TASK_GROUP,
            f"""
📢 New Task Added

🔗 Channel: {channel}

💰 Reward: {reward}$

🤖 Do task in bot
"""
        )

    except:
        pass


# ================= UPDATE FINALIZE TASK =================

def finalize_task(message,channel,reward):

    global task_counter

    try:

        members = int(message.text)

        if members <= 0:
            raise ValueError

    except:

        bot.send_message(message.chat.id,"❌ Invalid number")
        return

    tasks[task_counter] = {

        "channel":channel,
        "reward":reward,
        "remaining":members

    }

    post_task_group(channel,reward)

    bot.send_message(
        message.chat.id,
        f"""
✅ Promotion created

ID: {task_counter}

Channel: {channel}
Reward: {reward}$
Members: {members}
"""
    )

    task_counter += 1


# ================= WITHDRAW SYSTEM =================

withdraw_enabled = False

@bot.message_handler(func=lambda m:m.text=="💸 Withdraw")
def withdraw(message):

    if not withdraw_enabled:

        bot.send_message(
            message.chat.id,
            "❌ Withdraw system currently disabled"
        )
        return


# ================= RUN BOT =================

print("Bot Started...")

bot.infinity_polling(skip_pending=True)
