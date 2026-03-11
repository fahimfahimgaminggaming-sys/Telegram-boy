import telebot
from telebot import types
from config import BOT_TOKEN, ADMIN_ID

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ================= FORCE JOIN =================

CHANNELS = [
"@Task_Updates_Group",
"@Crypto_Tech_Zone",
"@AIRDROP_OFFICIALBD20"
]

def check_join(user_id):

    for ch in CHANNELS:

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

    if not check_join(uid):

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
            "📢 Task Group",
            url="https://t.me/Task_Updates_Group"))

        markup.add(
            types.InlineKeyboardButton(
            "📢 Crypto Tech Zone",
            url="https://t.me/Crypto_Tech_Zone"))

        markup.add(
            types.InlineKeyboardButton(
            "📢 Airdrop Official",
            url="https://t.me/AIRDROP_OFFICIALBD20"))

        markup.add(
            types.InlineKeyboardButton(
            "✅ Check Join",
            callback_data="check_join"))

        bot.send_message(
            uid,
            "🚫 Please join all channels first",
            reply_markup=markup
        )

        return

    show_menu(uid)


# ================= CHECK JOIN =================

@bot.callback_query_handler(func=lambda c: c.data=="check_join")
def check(call):

    if check_join(call.from_user.id):

        bot.send_message(
            call.message.chat.id,
            "✅ Access granted"
        )

        show_menu(call.from_user.id)

    else:

        bot.answer_callback_query(
            call.id,
            "❌ Join all channels first"
        )


# ================= MAIN MENU =================

def show_menu(uid):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("📋 Tasks","📢 Promote")
    markup.row("💰 Balance","📥 Deposit")
    markup.row("👥 Referral","🎁 Bonus")
    markup.row("🏆 Leaderboard","👤 Profile")

    bot.send_message(
        uid,
        "🚀 <b>Welcome to PROCOIN BOT</b>",
        reply_markup=markup
    )


# ================= ADMIN PANEL =================

@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("👥 Users","📢 Tasks")
    markup.row("💰 Deposits","📊 Stats")
    markup.row("📨 Broadcast","⚙ Settings")

    bot.send_message(
        message.chat.id,
        "👑 <b>ADMIN PANEL</b>",
        reply_markup=markup
    )

# ================= PROFILE =================

@bot.message_handler(func=lambda m: m.text == "👤 Profile")
def profile(message):

    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"""
👤 <b>USER PROFILE</b>

🆔 ID: {message.from_user.id}
👤 Username: @{message.from_user.username}

💰 Balance: {user['balance']} $
📊 Tasks Completed: {user['tasks']}
👥 Referrals: {user['referrals']}
"""
    )


# ================= BALANCE =================

@bot.message_handler(func=lambda m: m.text == "💰 Balance")
def balance(message):

    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"""
💰 <b>WALLET</b>

Balance: {user['balance']} $
"""
    )


# ================= ADMIN USERS =================

@bot.message_handler(func=lambda m: m.text == "👥 Users")
def users(message):

    if message.from_user.id != ADMIN_ID:
        return

    total = total_users()

    bot.send_message(
        message.chat.id,
        f"""
👥 <b>BOT USERS</b>

Total Users: {total}
"""
    )


# ================= ADD BALANCE =================

@bot.message_handler(commands=['addbalance'])
def addbal(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        _, uid, amount = message.text.split()

        uid = int(uid)
        amount = float(amount)

        add_balance(uid, amount)

        bot.send_message(
            message.chat.id,
            "✅ Balance added"
        )

    except:

        bot.send_message(
            message.chat.id,
            "Usage:\n/addbalance user_id amount"
        )


# ================= REMOVE BALANCE =================

@bot.message_handler(commands=['removebalance'])
def removebal(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        _, uid, amount = message.text.split()

        uid = int(uid)
        amount = float(amount)

        remove_balance(uid, amount)

        bot.send_message(
            message.chat.id,
            "➖ Balance removed"
        )

    except:

        bot.send_message(
            message.chat.id,
            "Usage:\n/removebalance user_id amount"
        )


# ================= BROADCAST =================

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast ","")

    for user in users.find():

        try:
            bot.send_message(user["user_id"], text)
        except:
            pass

    bot.send_message(
        message.chat.id,
        "📨 Broadcast sent"
      )
  # ================= DEPOSIT MENU =================

@bot.message_handler(func=lambda m: m.text == "📥 Deposit")
def deposit_menu(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("⭐ Stars Deposit","💰 Crypto Deposit")
    markup.row("📊 Deposit History","🔙 Back")

    bot.send_message(
        message.chat.id,
        """
💰 <b>DEPOSIT MENU</b>

Choose payment method
""",
        reply_markup=markup
    )


# ================= STARS DEPOSIT =================

@bot.message_handler(func=lambda m: m.text == "⭐ Stars Deposit")
def stars_deposit(message):

    bot.send_message(
        message.chat.id,
        """
⭐ <b>Stars Deposit</b>

Send how many Stars you want to deposit

Rate:
1 ⭐ = 0.013$
Minimum: 1 ⭐
"""
    )

    bot.register_next_step_handler(message, stars_amount)


def stars_amount(message):

    try:

        stars = int(message.text)

        if stars < 1:
            raise ValueError

        usd = stars * 0.013

        bot.send_message(
            message.chat.id,
            f"""
⭐ Stars: {stars}

💰 Value: {usd}$

Payment will open automatically
"""
        )

    except:

        bot.send_message(
            message.chat.id,
            "❌ Send valid stars amount"
        )


# ================= CRYPTO DEPOSIT =================

@bot.message_handler(func=lambda m: m.text == "💰 Crypto Deposit")
def crypto_menu(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("USDT BEP20","BTC")
    markup.row("ETH","TRX")
    markup.row("DOGE","🔙 Back")

    bot.send_message(
        message.chat.id,
        """
💰 <b>Crypto Deposit</b>

Choose cryptocurrency
""",
        reply_markup=markup
    )


# ================= CRYPTO SELECT =================

@bot.message_handler(func=lambda m: m.text in ["USDT BEP20","BTC","ETH","TRX","DOGE"])
def crypto_select(message):

    coin = message.text

    bot.send_message(
        message.chat.id,
        f"""
💰 <b>{coin} Deposit</b>

Enter deposit amount in USD

Example:
1
5
10
"""
    )


# ================= DEPOSIT HISTORY =================

@bot.message_handler(func=lambda m: m.text == "📊 Deposit History")
def deposit_history(message):

    bot.send_message(
        message.chat.id,
        """
📊 <b>Deposit History</b>

No deposits yet
"""
  )
  # ================= TASK DATABASE =================

tasks = {}
task_counter = 1
completed_tasks = {}


# ================= CREATE PROMOTION =================

@bot.message_handler(func=lambda m: m.text == "📢 Promote")
def create_promo(message):

    bot.send_message(
        message.chat.id,
        "📢 Send channel username\nExample: @channel"
    )

    bot.register_next_step_handler(message, get_channel)


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

    bot.send_message(uid,"💰 Reward per user (Minimum 0.01$)")

    bot.register_next_step_handler(
        message,
        lambda m:get_reward(m,channel)
    )


# ================= GET REWARD =================

def get_reward(message,channel):

    uid = message.from_user.id

    try:

        reward = float(message.text)

        if reward < 0.01:

            bot.send_message(uid,"❌ Minimum reward = 0.01$")
            return

    except:

        bot.send_message(uid,"❌ Invalid reward")
        return

    bot.send_message(uid,"👥 How many members?")

    bot.register_next_step_handler(
        message,
        lambda m:finalize_task(m,channel,reward)
    )


# ================= FINALIZE TASK =================

def finalize_task(message,channel,reward):

    global task_counter

    uid = message.from_user.id
    user = get_user(uid)

    try:

        members = int(message.text)

        if members <= 0:
            raise ValueError

    except:

        bot.send_message(uid,"❌ Invalid number")
        return

    total_cost = reward * members

    if user["balance"] < total_cost:

        bot.send_message(
            uid,
            f"❌ Not enough balance\nRequired: {total_cost}$"
        )
        return

    remove_balance(uid,total_cost)

    tasks[task_counter] = {

        "owner":uid,
        "channel":channel,
        "reward":reward,
        "remaining":members

    }

    bot.send_message(
        uid,
        f"""
✅ Promotion created

ID: {task_counter}
Total Cost: {total_cost}$
"""
    )

    task_counter += 1


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

Channel: {task['channel']}
Reward: {task['reward']}$
Remaining: {task['remaining']}
""",
        reply_markup=markup
    )


# ================= SKIP =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("skip_"))
def skip_task(call):

    index = int(call.data.split("_")[1])

    bot.answer_callback_query(call.id,"⏭ Task skipped")

    send_task(call.from_user.id,index)


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

        bot.answer_callback_query(call.id,"Already completed")
        return

    task = tasks[tid]

    try:

        member = bot.get_chat_member(task["channel"],uid)

        if member.status not in ["member","administrator","creator"]:

            bot.answer_callback_query(call.id,"❌ Join channel first")
            return

        add_balance(uid,task["reward"])

        task["remaining"] -= 1

        completed_tasks[uid].add(tid)

        bot.answer_callback_query(call.id,"✅ Reward added")

        bot.send_message(
            uid,
            f"🎉 You earned {task['reward']}$"
        )

        if task["remaining"] <= 0:

            del tasks[tid]

        send_task(uid,index+1)

    except:

        bot.answer_callback_query(call.id,"❌ Verification failed")
      # ================= REFERRAL DATABASE =================

referrals = {}
daily_bonus = {}
promo_codes = {}


# ================= REFERRAL =================

@bot.message_handler(func=lambda m: m.text == "👥 Referral")
def referral(message):

    uid = message.from_user.id

    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    total = referrals.get(uid,0)

    bot.send_message(
        uid,
        f"""
👥 <b>Referral Program</b>

Invite friends and earn rewards

🔗 Your Link:
{link}

👥 Total Referrals: {total}
"""
    )


# ================= START REFERRAL =================

@bot.message_handler(commands=['start'])
def start_ref(message):

    uid = message.from_user.id

    args = message.text.split()

    if len(args) > 1:

        ref = int(args[1])

        if ref != uid:

            referrals[ref] = referrals.get(ref,0) + 1

            add_balance(ref,0.05)

            bot.send_message(
                ref,
                "👥 New referral joined\n💰 +0.05$"
            )


# ================= DAILY BONUS =================

@bot.message_handler(func=lambda m: m.text == "🎁 Bonus")
def daily(message):

    uid = message.from_user.id

    now = time.time()

    if uid in daily_bonus:

        if now - daily_bonus[uid] < 86400:

            bot.send_message(
                uid,
                "⏳ Come back tomorrow"
            )

            return

    reward = round(random.uniform(0.01,0.05),2)

    add_balance(uid,reward)

    daily_bonus[uid] = now

    bot.send_message(
        uid,
        f"🎁 Daily Bonus\n💰 +{reward}$"
    )


# ================= LEADERBOARD =================

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard(message):

    top = sorted(
        users.find(),
        key=lambda x:x["balance"],
        reverse=True
    )[:10]

    text = "🏆 <b>Top Users</b>\n\n"

    i = 1

    for u in top:

        text += f"{i}. {u.get('username','user')} — {u['balance']}$\n"

        i += 1

    bot.send_message(message.chat.id,text)


# ================= PROMO CODE =================

@bot.message_handler(commands=['createcode'])
def create_code(message):

    if message.from_user.id != ADMIN_ID:
        return

    try:

        _, code, reward = message.text.split()

        reward = float(reward)

        promo_codes[code] = reward

        bot.send_message(
            message.chat.id,
            f"✅ Promo code created\n{code}"
        )

    except:

        bot.send_message(
            message.chat.id,
            "Usage:\n/createcode CODE REWARD"
        )


# ================= REDEEM CODE =================

@bot.message_handler(commands=['redeem'])
def redeem(message):

    uid = message.from_user.id

    try:

        _, code = message.text.split()

        if code not in promo_codes:

            bot.send_message(uid,"❌ Invalid code")
            return

        reward = promo_codes[code]

        add_balance(uid,reward)

        del promo_codes[code]

        bot.send_message(
            uid,
            f"🎟 Code redeemed\n💰 +{reward}$"
        )

    except:

        bot.send_message(
            uid,
            "Usage:\n/redeem CODE"
        )


# ================= TASK ANNOUNCEMENT =================

GROUP_ID = "@Task_Updates_Group"

def announce_task(channel,reward,members):

    bot.send_message(
        GROUP_ID,
        f"""
📢 <b>New Task Added</b>

Channel: {channel}
Reward: {reward}$
Slots: {members}

Open bot to complete
"""
    )


# ================= STATISTICS =================

@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def stats(message):

    user = get_user(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"""
📊 <b>Your Statistics</b>

💰 Balance: {user['balance']}$
📢 Tasks Completed: {user['tasks']}
👥 Referrals: {user['referrals']}
"""
        )
  print("Bot Started...")

bot.infinity_polling(skip_pending=True)
  
