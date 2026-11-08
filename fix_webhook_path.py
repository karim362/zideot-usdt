with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن الجزء الخاص بالـ Webhook واستبداله
old_webhook = """@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    return "Webhook is set and running perfectly!", 200"""

new_webhook = """@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook_root():
    # تعيين الويب هوك عند زيارة الصفحة الرئيسية
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + BOT_TOKEN)
    return "Webhook is set and running perfectly!", 200"""

if old_webhook in content:
    content = content.replace(old_webhook, new_webhook)
    print("✅ تم تعديل مسار الـ Webhook")
else:
    print("⚠️ لم يتم العثور على الكود القديم، قد يكون معدلاً.")

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
