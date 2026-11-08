with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# إضافة مسار الاختبار قبل قسم الـ Webhook
test_route = """
@app.route('/test')
def test_route():
    return "✅ Render updated successfully! Webhook route is ready."

# ===== إعداد Webhook ====="""

if "@app.route('/test')" not in content:
    content = content.replace("# ===== إعداد Webhook =====", test_route)
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ تم إضافة مسار الاختبار /test")
else:
    print("⚠️ مسار الاختبار موجود مسبقاً.")
