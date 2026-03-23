import os, datetime
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Тема на статията
topic_title = "Safe Online Shopping 2026: The Ultimate Protection Guide"

try:
    # 1. ГЕНЕРИРАНЕ С НОВИЯ ДВИГАТЕЛ (GEMINI 3 FLASH)
    response = client.models.generate_content(
        model='gemini-3-flash', 
        contents=f"Write a 1000 word SEO article about: {topic_title}. Format as strict HTML. Return ONLY raw HTML code."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    filename = f"safety-guide-{datetime.date.today()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Новата статия е готова: {filename}")

    # 2. ИНТЕГРАЦИЯ В index.html
    target_file = "index.html" 
    with open(target_file, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    # ТВОЯТ ТАЕН КОД (БЕЗ ИНТЕРВАЛИ)
    anchor = "<li></li>"
    
    if filename in index_content:
        print(f"Линкът {filename} вече е там.")
    elif anchor in index_content:
        new_entry = f'{anchor}\n  <li>🚀 <a href="{filename}" style="color:#93c5fd;text-decoration:none;">{topic_title}</a></li>'
        updated_html = index_content.replace(anchor, new_entry)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print(f"БИНГО: Машината успешно обнови оригиналната страница!")
    else:
        print(f"ГРЕШКА: Липсва котвата {anchor} в index.html!")

except Exception as e:
    print(f"Критична грешка: {e}")
