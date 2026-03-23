import os, datetime
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Темата на статията
topic_title = "The Ultimate Guide: How to spot fake online stores in 2026"

prompt = f"""Act as a Top-Tier SEO Expert. Write a comprehensive, 1000+ word guide on: '{topic_title}'. 
Requirements:
1. Format as strict HTML5 (no markdown, just raw code).
2. Start with <h1> and a 'Key Takeaways' <ul>.
3. Use <h2> for subheadings.
4. Include valid JSON-LD FAQ Schema Markup at the end.
Return ONLY the raw HTML code."""

try:
    # 1. Генериране на статията
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    date_str = datetime.date.today()
    filename = f"fake-stores-guide-{date_str}.html"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Готово: {filename}")

    # 2. АВТОМАТИЧНО ДОБАВЯНЕ НА ЛИНК В index.html
    with open("index.html", "r", encoding="utf-8") as f:
        index_html = f.read()
    
    # Създаваме HTML кода за новия линк
    new_link_html = f'\n<div style="margin: 15px 0; padding: 10px; border-left: 4px solid #007bff; background: #f8f9fa;">\n  🚀 <strong>New:</strong> <a href="{filename}" style="text-decoration: none; color: #007bff;">{topic_title}</a>\n</div>'
    
    # Търсим котвата и я заместваме с новия линк + самата котва (за следващия път)
    if '' in index_html:
        updated_index = index_html.replace('', new_link_html)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_index)
        print("БИНГО: Линкът е добавен в началната страница!")
    else:
        print("Внимание: Котвата не е намерена в index.html")

except Exception as e:
    print(f"Грешка: {e}")
