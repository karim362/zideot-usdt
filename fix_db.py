with open('bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('import psycopg2\nfrom psycopg2.extras import DictCursor', 'import psycopg\nfrom psycopg.rows import dict_row')
content = content.replace('psycopg2.connect', 'psycopg.connect')
content = content.replace('cursor_factory=DictCursor', 'row_factory=dict_row')

with open('bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ تم تعديل كود البوت لاستخدام psycopg")
