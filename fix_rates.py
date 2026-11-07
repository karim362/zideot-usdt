with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# تغيير مكافأة الإحالة من 0.01 إلى 0.1 (عشان كل 10 إحالات = 1 USDT)
content = content.replace('balance + 0.01 WHERE user_id = %s', 'balance + 0.1 WHERE user_id = %s')
content = content.replace('0.0100000 USDT` لكل شخص', '0.1000000 USDT` لكل شخص')

# تغيير النصوص في رسالة الترحيب
content = content.replace('👈 كل 100 إعلان = 1.0000000 USDT', '👈 كل 10 إعلانات = 1.0000000 USDT')
content = content.replace('👈 كل إحالة (دعوة صديق) = 0.0100000 USDT', '👈 كل 10 إحالات (دعوة أصدقاء) = 1.0000000 USDT')

# الرسالة السحرية للإحالة
magic_text = "🛑 توقف عن التمرير! هذا البوت سيغير حياتك المالية... 🤯\\n\\n💸 هل تتخيل تحويل وقتك الضائع إلى دولارات حقيقية (USDT) بدون أي رأس مال؟\\n🔥 أنا للتو بدأت أسحب أرباحي! الطريقة سهلة جداً وسريعة.\\n\\n👇 اضغط على الرابط الآن قبل أن يتم إغلاق التسجيل:"
import urllib.parse
encoded_magic = urllib.parse.quote(magic_text)
import re
content = re.sub(r'share_text = urllib\.parse\.quote\(".*?"\)', f'share_text = "{encoded_magic}"', content)

# تحديث نص زر الإحالات
content = content.replace('كل 100 إحالة = 1.0000000 USDT', 'كل 10 إحالات = 1.0000000 USDT')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ تم تحديث البوت ورسالة الدعوة السحرية")
