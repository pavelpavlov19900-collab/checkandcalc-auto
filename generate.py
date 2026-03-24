import os, datetime, random
from google import genai

# ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    # 1. ИЗБОР НА УНИКАЛНА ТЕМА
    if not os.path.exists('topics.txt'):
        print("Липсва topics.txt!")
        exit()

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]

    existing_files = os.listdir('.')
    available = []
    for t in topics:
        slug = t.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '') + ".html"
        if slug not in existing_files:
            available.append(t)

    if not available:
        print("Всички теми са изчерпани!")
        exit()

    topic_title = random.choice(available)
    filename = topic_title.lower().replace(' ', '-').replace(':', '').replace('?', '').replace('!', '') + ".html"

    # 2. ГЕНЕРИРАНЕ (С ТВОЯ МОДЕЛ)
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=f"Write a 1000 word SEO article in English about: {topic_title}. Return ONLY raw HTML."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 3. ДОБАВЯНЕ В INDEX.HTML
    target_file = "index.html"
    with open(target_file, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    anchor = "<li></li>"
    if anchor in index_content and filename not in index_content:
        new_entry = f'{anchor}\n    <li>🚀 <a href="{filename}">{topic_title}</a></li>'
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(index_content.replace(anchor, new_entry))

    # 4. ОБНОВЯВАНЕ НА SITEMAP.XML
    sitemap_file = 'sitemap.xml'
    today = datetime.date.today().isoformat()
    new_url = f"""  <url>
    <loc>https://checkandcalc.com/{filename}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.80</priority>
  </url>\n</urlset>"""

    if os.path.exists(sitemap_file):
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            s_content = f.read()
        if filename not in s_content:
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                f.write(s_content.replace("</urlset>", new_url))

    print(f"Готово! Нова статия: {topic_title}")

except Exception as e:
    print(f"Грешка: {e}")
