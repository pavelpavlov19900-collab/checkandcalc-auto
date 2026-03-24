import os, datetime, random
from google import genai

# ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    # --- СТЪПКА 1: ИНТЕЛИГЕНТЕН ИЗБОР НА ТЕМА (БЕЗ ПОВТОРЕНИЯ) ---
    if not os.path.exists('topics.txt'):
        print("Грешка: Не намерих topics.txt!")
        exit()

    with open('topics.txt', 'r', encoding='utf-8') as f:
        all_topics = [line.strip() for line in f if line.strip()]

    existing_files = os.listdir('.')
    available_topics = []
    
    # Филтрираме кои теми вече сме написали
    for t in all_topics:
        # Правим тестов slug (име на файл), за да проверим дали съществува
        temp_slug = t.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '') + ".html"
        if temp_slug not in existing_files:
            available_topics.append(t)

    if not available_topics:
        print("✅ Всички теми от списъка са изчерпани! Поздравления!")
        exit()

    topic_title = random.choice(available_topics)
    # Генерираме чисто име на файла за SEO
    filename = topic_title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '') + ".html"

    print(f"🎬 Започвам работа по нова тема: {topic_title}")

    # --- СТЪПКА 2: ГЕНЕРИРАНЕ НА БРУТАЛНО SEO СЪДЪРЖАНИЕ ---
    seo_prompt = f"""
    Write a professional 1000-word SEO article in English about: {topic_title}.
    Structure: Use <h1> for title, multiple <h2> and <h3> subheadings. 
    Include bullet points and a strong Call to Action.
    Target 2026 security trends and naturally mention NordVPN benefits.
    Return ONLY raw HTML content (no ```html tags).
    """

    response = client.models.generate_content(
        model='gemini-2.0-flash', # Използвам Flash за скорост и цена, или остави твоя модел
        contents=seo_prompt
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"📄 Статията е запазена като {filename}")

    # --- СТЪПКА 3: ИНТЕГРАЦИЯ В INDEX.HTML ---
    target_file = "index.html" 
    with open(target_file, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    anchor = "<li></li>"
    if filename in index_content:
        print("⚠️ Линкът вече съществува в index.html.")
    elif anchor in index_content:
        new_entry = f'{anchor}\n    <li>🚀 <a href="{filename}">{topic_title}</a></li>'
        new_index = index_content.replace(anchor, new_entry)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_index)
        print(f"🔗 Линкът е добавен успешно в {target_file}")

    # --- СТЪПКА 4: АВТОМАТИЧЕН SITEMAP.XML ЗА GOOGLE ---
    sitemap_file = 'sitemap.xml'
    today = datetime.date.today().isoformat()
    new_url_entry = f"""  <url>
    <loc>[https://checkandcalc.com/](https://checkandcalc.com/){filename}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.80</priority>
  </url>\n</urlset>"""

    if os.path.exists(sitemap_file):
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            sitemap_content = f.read()
        
        if filename not in sitemap_content:
            updated_sitemap = sitemap_content.replace("</urlset>", new_url_entry)
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                f.write(updated_sitemap)
            print("🗺️ Sitemap.xml беше обновен за Google.")
    
    print("🎯 Операцията приключи успешно! Фабриката работи.")

except Exception as e:
    print(f"❌ Грешка в системата: {e}")
