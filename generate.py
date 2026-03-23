import os, datetime
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

topic_title = "Safe Online Shopping 2026: The Ultimate Protection Guide"

try:
    # 1. ГЕНЕРИРАНЕ
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=f"Write a 1000 word SEO article about: {topic_title}. Format as strict HTML. Return ONLY raw HTML code."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    filename = f"safety-guide-{datetime.date.today()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. ТАЙНИЯТ КОД Е ТУК (ИНСПЕКЦИЯ):
    target_file = "index.html" 
    with open(target_file, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    # ЕТО ГО ТВОЯТ ТАЕН КОД, ПРИЯТЕЛЮ:
    anchor = "<li></li>"
    
    if filename in index_content:
        print("Вече съществува.")
    elif anchor in index_content:
        # Тук става вграждането:
        new_entry = f'{anchor}\n  <li>🚀 <a href="{filename}" style="color:#93c5fd;text-decoration:none;">{topic_title}</a></li>'
        updated_html = index_content.replace(anchor, new_entry)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated_html)
        print("БИНГО! Линкът е на мястото си!")
    else:
        print(f"ГРЕШКА: Роботът не намери '{anchor}' в твоя index.html")

except Exception as e:
    print(f"Грешка: {e}")
