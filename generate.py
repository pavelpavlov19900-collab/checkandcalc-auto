import os, datetime
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

topic_title = "Safe Online Shopping 2026: The Ultimate Protection Guide"

try:
    # 1. Генериране на статията
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=f"Write a 1000 word SEO article about: {topic_title}. Return ONLY raw HTML."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    filename = f"safety-guide-{datetime.date.today()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. ТЕСТОВА ИНТЕГРАЦИЯ В test.html (ПЪРВО ТЕСТВАМЕ ТУК!)
    target_file = "test.html" # Когато тестваш успешно, тук ще напишем "index.html"
    
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Твоята нова котва
    anchor = "<li></li>"
    
    if filename in content:
        print("Линкът вече е там. Спирам.")
    elif anchor in content:
        # Създаваме чист списъчен елемент за новата статия
        new_entry = f'{anchor}\n  <li>🚀 <a href="{filename}">{topic_title}</a></li>'
        new_content = content.replace(anchor, new_entry)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Успешно добавен линк в {target_file}")
    else:
        print(f"Грешка: Не намерих котвата {anchor} в {target_file}")

except Exception as e:
    print(f"Грешка в системата: {e}")
