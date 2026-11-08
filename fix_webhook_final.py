with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن دالة استقبال الرسائل وتصحيحها
old_route = """@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200"""

new_route = """@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}")
        return "Error", 500"""

if old_route in content:
    content = content.replace(old_route, new_route)
    print("✅ تم تحديث مسار استقبال الرسائل")
else:
    print("⚠️ الكود قد يكون مختلفاً، جاري المحاولة...")
    # محاولة استبدال أي كود مشابه
    import re
    content = re.sub(r"@app\.route\('/' \+ BOT_TOKEN.*?return \"!\", 200", new_route, content, flags=re.DOTALL)

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
