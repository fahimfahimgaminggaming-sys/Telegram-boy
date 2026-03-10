import telebot
from telebot import types
import time
import random

TOKEN = "8719865837:AAE3dmy2T3hmjEWLaOjDyRi5kU9zb9DY5t8"
ADMIN_ID = 7015857680

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ================= CHANNELS =================

FORCE_CHANNELS = [
    "@Crypto_Tech_Zone",
    "@AIRDROP_OFFICIALBD20"
]

# ================= DATABASE =================

users = {}
referrals = {}
daily_bonus = {}
join_reward = {}

# ================= REGISTER =================

def register(uid, username=None):

    if uid not in users:

        users[uid] = {
            "balance": 0,
            "spent": 0,
            "username": username or "NoUser"
        }

# ================= CHECK JOIN =================

def is_joined(user_id):

    for ch in FORCE_CHANNELS:

        try:

            member = bot.get_chat_member(ch, user_id)

            if member.status not in ["member","administrator","creator"]:
                return False

        except:
            return False

    return True

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):

    uid = message.from_user.id
    register(uid, message.from_user.username)

    # referral system
    if message.text != "/start":

        try:

            ref = int(message.text.split()[1])

            if ref != uid and ref in users:

                if ref not in referrals:
                    referrals[ref] = 0

                referrals[ref] += 1

                if referrals[ref] <= 10:
                    reward = 2
                else:
                    reward = 1

                users[ref]["balance"] += reward

                bot.send_message(
                    ref,
                    f"👥 New referral joined!\n"
                    f"💰 Reward: {reward} PC\n"
                    f"📊 Total referrals: {referrals[ref]}"
                )

        except:
            pass

    if not is_joined(uid):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "🔔 Join Channel 1",
                url="https://t.me/Crypto_Tech_Zone"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "🔔 Join Channel 2",
                url="https://t.me/AIRDROP_OFFICIALBD20"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "✅ Check Join",
                callback_data="check_join"
            )
        )

        bot.send_message(
            uid,
            "🚫 Join both channels to use the bot.",
            reply_markup=markup
        )

        return

    if uid not in join_reward:

        users[uid]["balance"] += 4
        join_reward[uid] = True

        bot.send_message(uid,"🎉 You received 4 PC for joining channels!")

    show_menu(uid)

# ================= CHECK BUTTON =================

@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(call):

    uid = call.from_user.id

    if is_joined(uid):

        if uid not in join_reward:

            users[uid]["balance"] += 4
            join_reward[uid] = True

            bot.send_message(uid,"🎉 You received 4 PC")

        show_menu(uid)

    else:

        bot.answer_callback_query(call.id,"❌ Join both channels first")

# ================= MENU =================

def show_menu(uid):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("📋 View Tasks", "🚀 Create Promotion")
    markup.row("🎁 Daily Bonus", "👥 Refer & Earn")
    markup.row("💳 Deposit", "👤 Profile")
    markup.row("🏆 Leaderboard")

    bot.send_message(uid,"💎 Welcome to PROCOIN BOT",reply_markup=markup)

# ================= PROFILE =================

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    uid = message.from_user.id
    register(uid)

    user = users[uid]

    bot.send_message(
        uid,
        f"""
👤 <b>@{user['username']}</b>

💰 Balance: {user['balance']} PC
📈 Spent: {user['spent']} PC
"""
    )

# ================= DAILY BONUS =================

@bot.message_handler(func=lambda m: m.text == "🎁 Daily Bonus")
def bonus(message):

    uid = message.from_user.id
    register(uid)

    now = time.time()

    if uid in daily_bonus:

        if now - daily_bonus[uid] < 86400:

            bot.send_message(uid,"⏳ Come back tomorrow")
            return

    reward = random.randint(1,2)

    users[uid]["balance"] += reward
    daily_bonus[uid] = now

    bot.send_message(uid,f"🎁 You received {reward} PC")

# ================= REFERRAL =================

@bot.message_handler(func=lambda m: m.text == "👥 Refer & Earn")
def refer(message):

    uid = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    total = referrals.get(uid,0)

    bot.send_message(
        uid,
        f"""
👥 Your Referral Link:

{link}

📊 Total Referrals: {total}

💰 Reward:
1-10 refer = 2 PC
After 10 = 1 PC
"""
    )

# ================= LEADERBOARD =================

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard(message):

    if not referrals:

        bot.send_message(message.chat.id,"❌ No referrals yet")
        return

    sorted_refs = sorted(
        referrals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = "🏆 <b>Top Referrers</b>\n\n"

    for i,(uid,count) in enumerate(sorted_refs[:10],1):

        user = users.get(uid,{})
        username = user.get("username","NoUser")

        text += f"{i}. @{username} — {count} referrals\n"

    bot.send_message(message.chat.id,text)
    # ================= TASK DATABASE =================

tasks = {}
task_counter = 1
completed_tasks = {}

# ================= CREATE PROMOTION =================

@bot.message_handler(func=lambda m: m.text == "🚀 Create Promotion")
def create_promo(message):

    bot.send_message(
        message.chat.id,
        "📢 Send channel username\nExample: @channel"
    )

    bot.register_next_step_handler(message,get_channel)

# ================= GET CHANNEL =================

def get_channel(message):

    uid = message.from_user.id
    channel = message.text.strip()

    try:

        bot_member = bot.get_chat_member(channel, bot.get_me().id)

        if bot_member.status not in ["administrator","creator"]:

            bot.send_message(
                uid,
                "❌ Bot must be admin in channel"
            )
            return

    except:

        bot.send_message(uid,"❌ Invalid channel")
        return

    bot.send_message(uid,"💰 Reward per user (Minimum 2 PC)")

    bot.register_next_step_handler(
        message,
        lambda m:get_reward(m,channel)
    )

# ================= GET REWARD =================

def get_reward(message,channel):

    uid = message.from_user.id

    try:

        reward = int(message.text)

        if reward < 2:

            bot.send_message(uid,"❌ Minimum reward = 2 PC")
            return

    except:

        bot.send_message(uid,"❌ Invalid reward")
        return

    bot.send_message(uid,"👥 How many members?")

    bot.register_next_step_handler(
        message,
        lambda m:finalize(m,channel,reward)
    )

# ================= FINALIZE TASK =================

def finalize(message,channel,reward):

    global task_counter

    uid = message.from_user.id

    try:

        members = int(message.text)

        if members <= 0:
            raise ValueError

    except:

        bot.send_message(uid,"❌ Invalid number")
        return

    total = reward * members

    if users[uid]["balance"] < total:

        bot.send_message(uid,"❌ Not enough balance")
        return

    users[uid]["balance"] -= total
    users[uid]["spent"] += total

    tasks[task_counter] = {

        "owner":uid,
        "channel":channel,
        "reward":reward,
        "remaining":members

    }

    bot.send_message(
        uid,
        f"✅ Promotion created\nID: {task_counter}"
    )

    task_counter += 1

# ================= VIEW TASK =================

@bot.message_handler(func=lambda m: m.text == "📋 View Tasks")
def view_tasks(message):

    send_task(message.from_user.id,0)

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
            "✅ Verify",
            callback_data=f"verify_{tid}_{index}"
        )
    )

    bot.send_message(
        uid,
        f"""
📢 Task ID: {tid}

💰 Reward: {task['reward']} PC
👥 Remaining: {task['remaining']}
""",
        reply_markup=markup
    )

# ================= SKIP =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def skip_task(call):

    index = int(call.data.split("_")[1])

    bot.answer_callback_query(call.id,"⏭ Task skipped")

    send_task(call.from_user.id,index)
# ================= DEPOSIT DATABASE =================

deposit_requests = {}
deposit_history = {}

# ================= DEPOSIT START =================

@bot.message_handler(func=lambda m: m.text == "💳 Deposit")
def deposit_start(message):

    bot.send_message(
        message.chat.id,
        "💰 How many PC coins do you want to buy?\n\nMinimum = 20 PC"
    )

    bot.register_next_step_handler(message, deposit_amount)


# ================= GET AMOUNT =================

def deposit_amount(message):

    uid = message.from_user.id

    try:
        pc = int(message.text)
    except:
        bot.send_message(uid,"❌ Send a valid number")
        return

    usd = pc / 100

    if usd < 0.2:

        bot.send_message(
            uid,
            "❌ Minimum deposit = 0.2$\n(20 PC)"
        )
        return

    deposit_requests[uid] = {
        "pc": pc,
        "usd": usd
    }

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "✅ Confirm",
            callback_data=f"confirm_dep_{uid}"
        ),
        types.InlineKeyboardButton(
            "❌ Cancel",
            callback_data="cancel_dep"
        )
    )

    bot.send_message(
        uid,
        f"""
💰 Deposit Summary

PC Coins: {pc}
USD Price: {usd}$

Confirm deposit?
""",
        reply_markup=markup
  )
  
# ================= CONFIRM =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_dep"))
def confirm_deposit(call):

    uid = call.from_user.id

    data = deposit_requests.get(uid)

    if not data:
        return

    bot.send_message(
        uid,
        f"""
💳 Deposit PC Coins

Amount: {data['usd']}$

Send payment to:

USDT (BEP20)
0x92bef3f9fa9d6c2268b8260563a062e11e286c87

TRX (TRC20)
TWASfH7D7ZbZ1pkH9tzja4b37RgNHScTtQ

📸 Send payment screenshot here.
"""
    )

    bot.answer_callback_query(call.id)


# ================= RECEIVE SCREENSHOT =================

@bot.message_handler(content_types=['photo'])
def receive_deposit(message):

    uid = message.from_user.id

    if uid not in deposit_requests:
        return

    data = deposit_requests[uid]

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approve_dep_{uid}"
        ),
        types.InlineKeyboardButton(
            "❌ Reject",
            callback_data=f"reject_dep_{uid}"
        )
    )

    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"""
💳 Deposit Request

User: {uid}
PC: {data['pc']}
USD: {data['usd']}$
""",
        reply_markup=markup
    )


# ================= APPROVE =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_dep"))
def approve_deposit(call):

    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[2])

    data = deposit_requests.get(uid)

    if not data:
        return

    register(uid)

    users[uid]["balance"] += data["pc"]

    deposit_history.setdefault(uid, []).append(data)

    del deposit_requests[uid]

    bot.send_message(
        uid,
        f"✅ Deposit Approved\n💰 {data['pc']} PC added"
    )

    bot.answer_callback_query(call.id,"Approved")


# ================= REJECT =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_dep"))
def reject_deposit(call):

    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[2])

    if uid in deposit_requests:
        del deposit_requests[uid]

    bot.send_message(uid,"❌ Deposit rejected")

    bot.answer_callback_query(call.id,"Rejected")

# ================= RECEIVE SCREENSHOT =================

@bot.message_handler(content_types=['photo'])
def receive_deposit(message):

    uid = message.from_user.id

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton(
            "✅ Approve Deposit",
            callback_data=f"approve_{uid}"
        )
    )

    bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=f"Deposit request from user {uid}",
        reply_markup=markup
    )


# ================= APPROVE DEPOSIT =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def approve_deposit(call):

    if call.from_user.id != ADMIN_ID:
        return

    uid = int(call.data.split("_")[1])

    register(uid)

    users[uid]["balance"] += 100

    bot.send_message(uid,"✅ Deposit approved\n💰 100 PC added")

    bot.answer_callback_query(call.id,"Approved")
# ================= VERIFY =================

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

        bot.answer_callback_query(call.id,"Already done")
        return

    task = tasks[tid]

    try:

        member = bot.get_chat_member(task["channel"],uid)

        if member.status not in ["member","administrator","creator"]:

            bot.answer_callback_query(call.id,"❌ Join channel first")
            return

        users[uid]["balance"] += task["reward"]

        task["remaining"] -= 1

        completed_tasks[uid].add(tid)

        bot.answer_callback_query(call.id,"✅ Reward added")

        bot.send_message(uid,f"🎉 You earned {task['reward']} PC")

        if task["remaining"] <= 0:

            del tasks[tid]

        send_task(uid,index+1)

    except:

        bot.answer_callback_query(call.id,"❌ Verification failed")
        # ================= MY PROMOTIONS =================

@bot.message_handler(func=lambda m: m.text == "📢 My Promotions")
def my_promotions(message):

    uid = message.from_user.id

    user_tasks = [(tid,t) for tid,t in tasks.items() if t["owner"] == uid]

    if not user_tasks:

        bot.send_message(uid,"❌ You have no active promotions")
        return

    for tid,task in user_tasks:

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "🛑 Cancel Promotion",
                callback_data=f"cancel_{tid}"
            )
        )

        bot.send_message(
            uid,
            f"""
📢 Promotion ID: {tid}

📺 Channel: {task['channel']}
💰 Reward: {task['reward']} PC
👥 Remaining: {task['remaining']}
""",
            reply_markup=markup
        )

# ================= CANCEL PROMOTION =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("cancel_"))
def cancel_promo(call):

    uid = call.from_user.id
    tid = int(call.data.split("_")[1])

    if tid not in tasks:

        bot.answer_callback_query(call.id,"Task not found")
        return

    task = tasks[tid]

    if task["owner"] != uid:

        bot.answer_callback_query(call.id,"❌ Not your task")
        return

    refund = task["reward"] * task["remaining"]

    users[uid]["balance"] += refund

    del tasks[tid]

    bot.answer_callback_query(call.id,"Promotion cancelled")

    bot.send_message(
        uid,
        f"🛑 Promotion cancelled\n💰 Refunded: {refund} PC"
    )

# ================= TASK FILTER MENU =================

@bot.message_handler(commands=['tasks'])
def task_filter_menu(message):

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton("💰 High Reward",callback_data="filter_high")
    )

    markup.add(
        types.InlineKeyboardButton("🆕 New Tasks",callback_data="filter_new")
    )

    markup.add(
        types.InlineKeyboardButton("⚡ Fast Tasks",callback_data="filter_fast")
    )

    bot.send_message(message.chat.id,"📋 Choose task type:",reply_markup=markup)

# ================= HIGH REWARD TASK =================

@bot.callback_query_handler(func=lambda c: c.data == "filter_high")
def high_reward_tasks(call):

    sorted_tasks = sorted(
        tasks.items(),
        key=lambda x:x[1]["reward"],
        reverse=True
    )

    send_filtered_tasks(call.from_user.id,sorted_tasks)

# ================= NEW TASK =================

@bot.callback_query_handler(func=lambda c: c.data == "filter_new")
def new_tasks(call):

    new_list = list(tasks.items())[::-1]

    send_filtered_tasks(call.from_user.id,new_list)

# ================= FAST TASK =================

@bot.callback_query_handler(func=lambda c: c.data == "filter_fast")
def fast_tasks(call):

    fast_list = sorted(
        tasks.items(),
        key=lambda x:x[1]["remaining"]
    )

    send_filtered_tasks(call.from_user.id,fast_list)

# ================= FILTER TASK SENDER =================

def send_filtered_tasks(uid,task_list):

    if not task_list:

        bot.send_message(uid,"❌ No tasks available")
        return

    tid,task = task_list[0]

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
            callback_data=f"skip_1"
        ),
        types.InlineKeyboardButton(
            "✅ Verify",
            callback_data=f"verify_{tid}_0"
        )
    )

    bot.send_message(
        uid,
        f"""
📢 Task ID: {tid}

💰 Reward: {task['reward']} PC
👥 Remaining: {task['remaining']}
""",
        reply_markup=markup
    )

# ================= ADMIN PANEL =================

@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        """
👑 ADMIN PANEL

/users - Total users
/tasks - Active tasks
/broadcast - Send message
/stats - Bot stats
"""
    )

# ================= USERS COUNT =================

@bot.message_handler(commands=['users'])
def total_users(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id,f"👥 Total Users: {len(users)}")

# ================= TASK COUNT =================

@bot.message_handler(commands=['tasks'])
def total_tasks(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(message.chat.id,f"📢 Active Tasks: {len(tasks)}")

# ================= STATS =================

@bot.message_handler(commands=['stats'])
def stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    total_spent = sum(u["spent"] for u in users.values())

    bot.send_message(
        message.chat.id,
        f"""
📊 BOT STATS

👥 Users: {len(users)}
📢 Tasks: {len(tasks)}
💰 Total Spent: {total_spent} PC
"""
    )

# ================= BROADCAST =================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    sent = 0

    for uid in users:

        try:

            bot.send_message(uid,text)
            sent += 1

        except:
            pass

    bot.send_message(message.chat.id,f"✅ Sent to {sent} users")

# ================= TELEGRAM STARS PAYMENT =================

@bot.message_handler(func=lambda m: m.text == "⭐ Buy PC Coins")
def buy_stars(message):

    prices = [types.LabeledPrice("130 PC Coin", 100)]  # 100 Stars

    bot.send_invoice(
        message.chat.id,
        title="Buy PC Coins",
        description="100 Telegram Stars = 130 PC Coins",
        provider_token="",  # Stars payment uses empty provider
        currency="XTR",
        prices=prices,
        start_parameter="buy_pc",
        payload="stars_pc"
    )


# ================= PRE CHECKOUT =================

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):

    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# ================= TELEGRAM STARS PAYMENT =================

@bot.message_handler(func=lambda m: m.text == "⭐ Buy PC Coins")
def buy_stars(message):

    prices = [types.LabeledPrice("130 PC Coin", 100)]

    bot.send_invoice(
        message.chat.id,
        title="Buy PC Coins",
        description="100 Telegram Stars = 130 PC",
        provider_token="1877036958:TEST:8eb7056331115b05b7f0b1c602889daf3d5a2204",
        currency="XTR",
        prices=prices,
        start_parameter="buy_pc",
        payload="stars_pc"
    )


# ================= PRE CHECKOUT =================

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):

    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# ================= PAYMENT SUCCESS =================

@bot.message_handler(content_types=['successful_payment'])
def payment_success(message):

    uid = message.from_user.id

    register(uid)

    users[uid]["balance"] += 130

    bot.send_message(
        uid,
        "⭐ Payment successful!\n💰 130 PC added"
    )
    # ================= RUN BOT =================

print("Bot Started...")

bot.infinity_polling(skip_pending=True)
