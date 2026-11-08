with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. إضافة كود الـ Inline Mode (عشان يبعت في جروبات كتير)
inline_code = """
# ===== ميزة الإرسال الجماعي للجروبات (Inline Mode) =====
@bot.inline_handler(lambda query: query.query == '')
def query_text(inline_query):
    try:
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={inline_query.from_user.id}"
        
        magic_text = (
            "🔥🔥 **اكتشاف جديد في عالم الكريبتو!** 🔥🔥\\n\\n"
            "💰 **هل أنت مستعد لتحويل وقتك إلى أرباح حقيقية؟**\\n"
            "🚀 **Zideot USDT** هي منصتك الأولى لربح عملة **USDT** مجاناً!\\n\\n"
            "❓ **كيف تبدأ؟**\\n"
            "1️⃣ اضغط على الرابط بالأسفل.\\n"
            "2️⃣ شاهد إعلانات قصيرة (ثواني معدودة).\\n"
            "3️⃣ اجمع النقاط وحولها لدولارات حقيقية.\\n\\n"
            "🎁 **نظام المكافآت:**\\n"
            "⚡️ كل 10 إعلانات = **1 USDT** (بدون رأس مال!)\\n"
            "👥 كل 10 إحالات = **1 USDT** (أرباح من دعوة أصدقائك)\\n"
            "💳 **الحد الأدنى للسحب:** 10 USDT فقط!\\n\\n"
            "⏳ **لا تفوت الفرصة!** الأماكن محدودة.\\n\\n"
            "👇 **اضغط هنا وابدأ الربح الآن:**"
        )

        # النتيجة اللي هتظهر في الجروبات
        result = types.InlineQueryResultArticle(
            id='1',
            title='🚀 شارك البوت واربح!',
            description='اضغط هنا لإرسال الرسالة الترويجية في الجروب',
            input_message_content=types.InputTextMessageContent(
                message_text=f"{magic_text}\\n{ref_link}",
                parse_mode='Markdown'
            ),
            thumb_url='https://cryptologos.cc/logos/tether-usdt-logo.png?v=026',
            thumb_width=128,
            thumb_height=128
        )
        bot.answer_inline_query(inline_query.id, [result], cache_time=1)
    except Exception as e:
        print(f"Inline Error: {e}")
"""

# إضافة الكود قبل تشغيل السيرفر
if "@bot.inline_handler" not in content:
    content = content.replace("# ===== إعداد Webhook =====", inline_code + "\n# ===== إعداد Webhook =====")

# 2. تعديل زر الدعوة عشان يستخدم ميزة الـ Inline
old_btn = 'btn_share = types.InlineKeyboardButton(text="🎁 دعوة أصدقائك", url=f"https://t.me/share/url?url={ref_link}&text={share_text}")'
new_btn = '''btn_share = types.InlineKeyboardButton(
        text="🎁 دعوة أصدقائك (الوضع المطور)", 
        switch_inline_query=""
    )'''

if old_btn in content:
    content = content.replace(old_btn, new_btn)
else:
    # محاولة ثانية لو الاسم متغير
    import re
    content = re.sub(r'btn_share = types\.InlineKeyboardButton\(.*?url=f"https://t\.me/share/url\?url=\{ref_link\}&text=\{share_text\}"\)', new_btn, content, flags=re.DOTALL)

# 3. تحديث نصوص الإحالة
content = content.replace('كل 100 إحالة = 1.0000000 USDT', 'كل 10 إحالات = 1.0000000 USDT')
content = content.replace('0.0100000 USDT` لكل شخص', '0.1000000 USDT` لكل شخص')
content = content.replace('كل 100 إعلان = 1.0000000 USDT', 'كل 10 إعلانات = 1.0000000 USDT')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ تم إضافة ميزة الإرسال الجماعي (Inline Mode) بنجاح!")
