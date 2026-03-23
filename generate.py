import os, datetime, random
from google import genai

# Инициализация на клиента
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Тема на статията
topic_title = "Safe Online Shopping 2026: The Ultimate Protection Guide"

try:
    # 1. ГЕНЕРИРАНЕ (Използваме най-съвместимия модел)
    response = client.models.generate_content(
        model='gemini-1.5-flash', 
        contents=f"Write a 1000 word SEO article about: {topic_title}. Format as strict HTML. Return ONLY raw HTML code."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    # ПРАВИМ ИМЕТО УНИКАЛНО (добавяме случаен номер, за да тестваме успешно сега)
    rand_id = random.randint(1000, 9999)
    filename = f"safety-guide-{rand_id}.html"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Статията е създадена: {filename}")

    # 2. ИНТЕГРАЦИЯ В index.html
    target_file = "index.html" 
    with open(target_file, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    # ТВОЯТ ТАЕН КОД (БЕЗ ИНТЕРВАЛИ - провери го в index.html!)
    anchor = "<li></li>"
    
    if anchor in index_content:
        # МАГИЯТА: Инжектираме новия линк под котвата
        new_entry = f'{anchor}\n  <li>🚀 <a href="{filename}" style="color:#93c5fd;text-decoration:none;">{topic_title} (ID: {rand_id})</a></li>'
        updated_html = index_content.replace(anchor, new_entry)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print(f"🎯 БИНГО: Линкът е на витрината!")
    else:
        print(f"❌ ГРЕШКА: Не намерих '{anchor}' в index.html. Провери файла!")

except Exception as e:
    print(f"⚠️ Критична грешка: {e}")
