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

import sys
from flask import request

@app.before_request
def spy_on_requests():
    # بنطبع أي طلب جاي من تيليجرام
    if request.path == '/webhook' and request.method == 'POST':
        print("\n" + "="*40)
        print("🚨 [SPY] تيليجرام بعتت طلب جديد!")
        print(f"🔗 المسار: {request.path}")
        print(f"📦 البيانات الخام: {request.get_data()[:300]}...") # بنطبع أول 300 حرف
        print("="*40 + "\n")

CORS(app)

try:
    bot.set_my_commands([
        types.BotCommand("/start", "القائمة الرئيسية 🏠"),
        types.BotCommand("/ping", "اختبار اتصال البوت 🏓")
    ])
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
        c.execute("UPDATE users SET balance = balance + 0.1 WHERE user_id = %s", (referrer_id,))
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
    ref_link = f"{bot_info.username}?start={user_id}"
    share_text = "%F0%9F%94%A5%F0%9F%94%A5%20%2A%2A%D8%A7%D9%83%D8%AA%D8%B4%D8%A7%D9%81%20%D8%AC%D8%AF%D9%8A%D8%AF%20%D9%81%D9%8A%20%D8%B9%D8%A7%D9%84%D9%85%20%D8%A7%D9%84%D9%83%D8%B1%D9%8A%D8%A8%D8%AA%D9%88%21%2A%2A%20%F0%9F%94%A5%F0%9F%94%A5%0A%0A%F0%9F%92%B0%20%2A%2A%D9%87%D9%84%20%D8%A3%D9%86%D8%AA%20%D9%85%D8%B3%D8%AA%D8%B9%D8%AF%20%D9%84%D8%AA%D8%AD%D9%88%D9%8A%D9%84%20%D9%88%D9%82%D8%AA%D9%83%20%D8%A5%D9%84%D9%89%20%D8%A3%D8%B1%D8%A8%D8%A7%D8%AD%20%D8%AD%D9%82%D9%8A%D9%82%D9%8A%D8%A9%D8%9F%2A%2A%0A%F0%9F%9A%80%20%2A%2AZideot%20USDT%2A%2A%20%D9%87%D9%8A%20%D9%85%D9%86%D8%B5%D8%AA%D9%83%20%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89%20%D9%84%D8%B1%D8%A8%D8%AD%20%D8%B9%D9%85%D9%84%D8%A9%20%2A%2AUSDT%2A%2A%20%D9%85%D8%AC%D8%A7%D9%86%D8%A7%D9%8B%21%0A%0A%E2%9D%93%20%2A%2A%D9%83%D9%8A%D9%81%20%D8%AA%D8%A8%D8%AF%D8%A3%D8%9F%2A%2A%0A1%EF%B8%8F%E2%83%A3%20%D8%A7%D8%B6%D8%BA%D8%B7%20%D8%B9%D9%84%D9%89%20%D8%A7%D9%84%D8%B1%D8%A7%D8%A8%D8%B7%20%D8%A8%D8%A7%D9%84%D8%A3%D8%B3%D9%81%D9%84.%0A2%EF%B8%8F%E2%83%A3%20%D8%B4%D8%A7%D9%87%D8%AF%20%D8%A5%D8%B9%D9%84%D8%A7%D9%86%D8%A7%D8%AA%20%D9%82%D8%B5%D9%8A%D8%B1%D8%A9%20%28%D8%AB%D9%88%D8%A7%D9%86%D9%8A%20%D9%85%D8%B9%D8%AF%D9%88%D8%AF%D8%A9%29.%0A3%EF%B8%8F%E2%83%A3%20%D8%A7%D8%AC%D9%85%D8%B9%20%D8%A7%D9%84%D9%86%D9%82%D8%A7%D8%B7%20%D9%88%D8%AD%D9%88%D9%84%D9%87%D8%A7%20%D9%84%D8%AF%D9%88%D9%84%D8%A7%D8%B1%D8%A7%D8%AA%20%D8%AD%D9%82%D9%8A%D9%82%D9%8A%D8%A9.%0A%0A%F0%9F%8E%81%20%2A%2A%D9%86%D8%B8%D8%A7%D9%85%20%D8%A7%D9%84%D9%85%D9%83%D8%A7%D9%81%D8%A2%D8%AA%3A%2A%2A%0A%E2%9A%A1%EF%B8%8F%20%D9%83%D9%84%2010%20%D8%A5%D8%B9%D9%84%D8%A7%D9%86%D8%A7%D8%AA%20%3D%20%2A%2A1%20USDT%2A%2A%20%28%D8%A8%D8%AF%D9%88%D9%86%20%D8%B1%D8%A3%D8%B3%20%D9%85%D8%A7%D9%84%21%29%0A%F0%9F%91%A5%20%D9%83%D9%84%2010%20%D8%A5%D8%AD%D8%A7%D9%84%D8%A7%D8%AA%20%3D%20%2A%2A1%20USDT%2A%2A%20%28%D8%A3%D8%B1%D8%A8%D8%A7%D8%AD%20%D9%85%D9%86%20%D8%AF%D8%B9%D9%88%D8%A9%20%D8%A3%D8%B5%D8%AF%D9%82%D8%A7%D8%A6%D9%83%29%0A%F0%9F%92%B3%20%2A%2A%D8%A7%D9%84%D8%AD%D8%AF%20%D8%A7%D9%84%D8%A3%D8%AF%D9%86%D9%89%20%D9%84%D9%84%D8%B3%D8%AD%D8%A8%3A%2A%2A%2010%20USDT%20%D9%81%D9%82%D8%B7%21%0A%0A%E2%8F%B3%20%2A%2A%D9%84%D8%A7%20%D8%AA%D9%81%D9%88%D8%AA%20%D8%A7%D9%84%D9%81%D8%B1%D8%B5%D8%A9%21%2A%2A%20%D8%A7%D9%84%D8%A3%D9%85%D8%A7%D9%83%D9%86%20%D9%85%D8%AD%D8%AF%D9%88%D8%AF%D8%A9%20%D9%88%D8%A7%D9%84%D9%85%D9%83%D8%A7%D9%81%D8%A2%D8%AA%20%D8%AA%D9%86%D9%81%D8%AF%20%D8%A8%D8%B3%D8%B1%D8%B9%D8%A9.%0A%0A%F0%9F%91%87%20%2A%2A%D8%A7%D8%B6%D8%BA%D8%B7%20%D9%87%D9%86%D8%A7%20%D9%88%D8%A7%D8%A8%D8%AF%D8%A3%20%D8%A7%D9%84%D8%B1%D8%A8%D8%AD%20%D8%A7%D9%84%D8%A2%D9%86%3A%2A%2A"
    btn_share = types.InlineKeyboardButton(text="🎁 دعوة أصدقائك", url=f"share/url?url={ref_link}&text={share_text}")
    
    markup.add(btn_app)
    markup.add(btn_balance, btn_refs)
    markup.add(btn_withdraw, btn_share)
    btn_test = types.InlineKeyboardButton("🏓 اختبار الاتصال", callback_data="test_ping")
    markup.add(btn_test)

    welcome_text = (
        f"🔥 **هل أنت مستعد لتحويل وقتك إلى أرباح حقيقية؟!** 💸\n\n"
        f"🚀 **مرحباً بك في Zideot USDT** - منصتك الأولى لربح عملة USDT مجاناً!\n\n"
        f"⚡️ **نظام الأرباح السريع:**\n"
        f"👈 كل 10 إعلانات = 1.0000000 USDT\n"
        f"👈 كل 10 إحالات (دعوة أصدقاء) = 1.0000000 USDT\n"
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
        f"💰 **مكافأة الإحالة:** `0.1000000 USDT` لكل شخص.\n"
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


# ===== ميزة الإرسال الجماعي للجروبات (Inline Mode) =====
@bot.inline_handler(lambda query: query.query == '')
def query_text(inline_query):
    try:
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={inline_query.from_user.id}"
        
        magic_text = (
            "🔥🔥 **اكتشاف جديد في عالم الكريبتو!** 🔥🔥\n\n"
            "💰 **هل أنت مستعد لتحويل وقتك إلى أرباح حقيقية؟**\n"
            "🚀 **Zideot USDT** هي منصتك الأولى لربح عملة **USDT** مجاناً!\n\n"
            "❓ **كيف تبدأ؟**\n"
            "1️⃣ اضغط على الرابط بالأسفل.\n"
            "2️⃣ شاهد إعلانات قصيرة (ثواني معدودة).\n"
            "3️⃣ اجمع النقاط وحولها لدولارات حقيقية.\n\n"
            "🎁 **نظام المكافآت:**\n"
            "⚡️ كل 10 إعلانات = **1 USDT** (بدون رأس مال!)\n"
            "👥 كل 10 إحالات = **1 USDT** (أرباح من دعوة أصدقائك)\n"
            "💳 **الحد الأدنى للسحب:** 10 USDT فقط!\n\n"
            "⏳ **لا تفوت الفرصة!** الأماكن محدودة.\n\n"
            "👇 **اضغط هنا وابدأ الربح الآن:**"
        )

        # النتيجة اللي هتظهر في الجروبات
        result = types.InlineQueryResultArticle(
            id='1',
            title='🚀 شارك البوت واربح!',
            description='اضغط هنا لإرسال الرسالة الترويجية في الجروب',
            input_message_content=types.InputTextMessageContent(
                message_text=f"{magic_text}\n{ref_link}",
                parse_mode='Markdown'
            ),
            thumb_url='https://cryptologos.cc/logos/tether-usdt-logo.png?v=026',
            thumb_width=128,
            thumb_height=128
        )
        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    except Exception as e:
        print(f"Inline Error: {e}")


@app.route('/test')
def test_route():
    return "✅ Render updated successfully! Webhook route is ready."


# ===== أمر اختبار البوت =====
@bot.message_handler(commands=['ping'])
def ping_test(message):
    print(f"\n[!] تم استلام /ping من: {message.from_user.id}")
    try:
        print(f"[!] جاري إرسال الرد...")
        bot.reply_to(message, "🏓 البوت شغال والويب هوك متصل بنجاح!")
        print(f"[!] ✅ تم إرسال الرد بنجاح!")
    except Exception as e:
        print(f"[!] ❌ فشل إرسال الرد: {e}")

@bot.message_handler(func=lambda message: True)
def debug_all(message):
    print(f"\n[!] رسالة جديدة: {message.text} من {message.from_user.id}")


@bot.callback_query_handler(func=lambda call: call.data == "test_ping")
def callback_test_ping(call):
    bot.answer_callback_query(call.id, "🏓 البوت شغال والاتصال سليم 100%!", show_alert=True)


@app.route('/routes')
def show_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    return "<br>".join(routes)

# ===== إعداد Webhook =====
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://zideot-usdt-2.onrender.com')



@app.route('/webhook', methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # طباعة محتوى الرسالة بوضوح
        print(f"
[FINAL DEBUG] Received update:")
        if update.message:
            print(f"  - Chat ID: {update.message.chat.id}")
            print(f"  - Text: {update.message.text}")
            print(f"  - Content Type: {update.message.content_type}")
        
        # تمرير التحديث للبوت
        bot.process_new_updates([update])
        print(f"[FINAL DEBUG] ✅ Update processed successfully")
        
        return "!", 200
    except Exception as e:
        import traceback
        print(f"
❌ [FINAL ERROR] {e}")
        traceback.print_exc()
        return "Error", 500


@app.route("/")
def webhook():
    # مسح الويب هوك القديم وتعيين رابط الموقع الجديد
    bot.remove_webhook()
    # ملاحظة: هنستخدم مسار /webhook بدل التوكن
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    return "Webhook is set and running perfectly!", 200


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
