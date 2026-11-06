import telebot
from telebot import types
import os
import psycopg
from psycopg.rows import dict_row
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import urllib.parse

BOT_TOKEN = os.environ.get('BOT_TOKEN', '9009396106:AAFNaCQLDqU4jaKoRiq-FCnWvXY8ABNbkrc')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
CORS(app)

try:
    bot.set_my_commands([types.BotCommand("/start", "القائمة الرئيسية 🏠")])
except Exception as e:
    print("Error setting commands:", e)

def get_db_connection():
    return psycopg.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id BIGINT PRIMARY KEY, 
                 balance REAL DEFAULT 0.0, 
                 referrals INTEGER DEFAULT 0,
                 referrer_id BIGINT DEFAULT NULL)''')
    conn.commit()
    c.close()
    conn.close()
init_db()

def get_user(user_id):
    conn = get_db_connection()
    c = conn.cursor(row_factory=dict_row)
    c.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = c.fetchone()
    c.close()
    conn.close()
    return user

def create_user(user_id, referrer_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, referrer_id) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (user_id, referrer_id))
    conn.commit()
    c.close()
    conn.close()

def add_points(user_id, amount):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))
    conn.commit()
    c.close()
    conn.close()

def add_referral(referrer_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id = %s", (referrer_id,))
    c.execute("SELECT referrals FROM users WHERE user_id = %s", (referrer_id,))
    result = c.fetchone()
    if result:
        c.execute("UPDATE users SET balance = balance + 0.01 WHERE user_id = %s", (referrer_id,))
    conn.commit()
    c.close()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    args = message.text.split()
    user = get_user(user_id)
    if not user:
        referrer_id = None
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if referrer_id != user_id: add_referral(referrer_id)
            except: pass
        create_user(user_id, referrer_id)
        user = get_user(user_id)

    balance = user['balance'] if user else 0.0
    referrals = user['referrals'] if user else 0

    markup = types.InlineKeyboardMarkup()
    btn_app = types.InlineKeyboardButton(
        text="🔥 ابدأ الربح الآن", 
        web_app=types.WebAppInfo(url=f"https://zideot-usdt-app.netlify.app/?user_id={user_id}&balance={balance}&refs={referrals}") 
    )
    btn_balance = types.InlineKeyboardButton("💳 رصيدي الحالي", callback_data="check_balance")
    btn_refs = types.InlineKeyboardButton("👥 إحالاتي", callback_data="check_refs")
    btn_withdraw = types.InlineKeyboardButton("💸 سحب الأرباح", callback_data="withdraw")
    
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    share_text = urllib.parse.quote("🔥 انضم إليّ في Zideot USDT واربح عملة USDT مجاناً من مشاهدة الإعلانات! اضغط هنا:")
    btn_share = types.InlineKeyboardButton(text="🎁 دعوة أصدقائك", url=f"https://t.me/share/url?url={ref_link}&text={share_text}")
    
    markup.add(btn_app)
    markup.add(btn_balance, btn_refs)
    markup.add(btn_withdraw, btn_share)

    welcome_text = (
        f"🔥 **هل أنت مستعد لتحويل وقتك إلى أرباح حقيقية؟!** 💸\n\n"
        f"🚀 **مرحباً بك في Zideot USDT** - منصتك الأولى لربح عملة USDT مجاناً!\n\n"
        f"⚡️ **نظام الأرباح السريع:**\n"
        f"👈 كل 100 إعلان = 1.0000000 USDT\n"
        f"👈 كل إحالة (دعوة صديق) = 0.0100000 USDT\n"
        f"💳 **الحد الأدنى للسحب:** 10.0000000 USDT\n\n"
        f"👇 **اضغط على الزر أدناه وابدأ الربح الآن!**"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_balance")
def callback_balance(call):
    user = get_user(call.from_user.id)
    balance = user['balance'] if user else 0.0
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"💎 **رصيدك الحالي:**\n`{balance:.7f} USDT`", parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "check_refs")
def callback_refs(call):
    user = get_user(call.from_user.id)
    refs = user['referrals'] if user else 0
    bot.answer_callback_query(call.id)
    text = (
        f"👥 **عدد إحالاتك:** `{refs}`\n\n"
        f"💰 **مكافأة الإحالة:** `0.0100000 USDT` لكل شخص.\n"
        f"*(تتم إضافتها تلقائياً لرصيدك بمجرد دخول صديقك من رابطك)*"
    )
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def callback_withdraw(call):
    user = get_user(call.from_user.id)
    balance = user['balance'] if user else 0.0
    if balance < 10.0:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"⚠️ **عذراً، رصيدك غير كافٍ للسحب.**\n\nالحد الأدنى للسحب: `10.0000000 USDT`\nرصيدك الحالي: `{balance:.7f} USDT`\n\nاستمر في جمع النقاط!", parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "💳 **يرجى إرسال عنوان محفظة USDT (TRC20) الخاصة بك الآن:**")
        bot.register_next_step_handler(msg, process_withdraw)

def process_withdraw(message):
    wallet = message.text.strip()
    if len(wallet) < 20:
        bot.send_message(message.chat.id, "⚠️ عنوان المحفظة غير صحيح. يرجى المحاولة مرة أخرى من البداية.")
        return
    
    user_id = message.from_user.id
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance - 10.0 WHERE user_id = %s", (user_id,))
    conn.commit()
    c.close()
    conn.close()

    bot.send_message(
        message.chat.id, 
        f"✅ **تم استلام طلب السحب بنجاح!**\n\n"
        f"💸 المبلغ: `10.0000000 USDT`\n"
        f"💳 المحفظة: `{wallet}`\n\n"
        f"⏳ سيتم تحويل المبلغ في غضون بضع ساعات. شكراً لك!", 
        parse_mode='Markdown'
    )

@app.route('/')
def index():
    return "Zideot USDT API is running perfectly!"

@app.route('/api/add_points', methods=['POST'])
def api_add_points():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        amount = float(data.get('amount', 0.01))
        add_points(user_id, amount)
        user = get_user(user_id)
        new_balance = user['balance']
        text = f"✅ **تمت إضافة المكافأة بنجاح!**\n\n💰 تم إضافة: `+{amount:.7f} USDT`\n💎 إجمالي رصيدك: `{new_balance:.7f} USDT`"
        bot.send_message(user_id, text, parse_mode='Markdown')
        return jsonify({"status": "success", "new_balance": new_balance}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_user/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = get_user(user_id)
    if user:
        return jsonify({"status": "success", "balance": user['balance'], "referrals": user['referrals']}), 200
    return jsonify({"status": "not_found", "balance": 0.0, "referrals": 0}), 200

@app.route('/api/withdraw', methods=['POST'])
def api_withdraw():
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        wallet = data.get('wallet')
        amount = 10.0
        user = get_user(user_id)
        if not user or user['balance'] < amount:
            return jsonify({"status": "error", "message": "رصيد غير كافٍ"}), 400
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
        conn.commit()
        c.close()
        conn.close()
        text = f"✅ **تم استلام طلب السحب بنجاح!**\n\n💸 المبلغ: `10.0000000 USDT`\n💳 المحفظة: `{wallet}`\n\n⏳ سيتم تحويل المبلغ في غضون بضع ساعات."
        bot.send_message(user_id, text, parse_mode='Markdown')
        return jsonify({"status": "success", "message": "تم السحب"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def run_polling():
    bot.infinity_polling()

threading.Thread(target=run_polling, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
