with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# مسح نظام الـ Polling القديم
old_polling = """def run_polling():
    bot.infinity_polling()

threading.Thread(target=run_polling, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)"""

# إضافة نظام Webhook الجديد
new_webhook = """# ===== إعداد Webhook =====
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://zideot-usdt-2.onrender.com')

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    return "Webhook is set and running perfectly!", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)"""

if old_polling in content:
    content = content.replace(old_polling, new_webhook)
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ تم تحويل البوت بنجاح إلى نظام Webhook!")
else:
    print("⚠️ لم يتم العثور على كود الـ Polling القديم، ربما تم تعديله.")
