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

    # --- СТЪПКА 3: ИНДУСТРИАЛЕН КАТАЛОГИЗАТОР ---
    target_file = "index.html"
    
    # Използваме този формат, за да не се скрие текстът в чата:
    start_marker = "<" + "!-- AUTO_GENERATED_LIST_START --" + ">"
    end_marker = "<" + "!-- AUTO_GENERATED_LIST_END --" + ">"
    
    # 1. Сканираме всички статии
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', 'about.html', 'disclosure.html', 'privacy.html']]
    all_files.sort(key=os.path.getmtime, reverse=True)
    
    # 2. Изграждаме списъка
    links_html = ""
    for file in all_files:
        pretty_title = file.replace('.html', '').replace('-', ' ').title()
        links_html += f'          <li>🚀 <a href="{file}" style="color:#93c5fd;text-decoration:none;">{pretty_title}</a></li>\n'

    # 3. Четем index.html
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 4. Проверяваме за маркерите
    if start_marker in content and end_marker in content:
        parts = content.split(start_marker)
        rest = parts[1].split(end_marker)
        
        # Сглобяваме всичко
        new_content = parts[0] + start_marker + "\n" + links_html + "          " + end_marker + rest[1]
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ УСПЕХ: Списъкът е обновен!")
    else:
        print("❌ ГРЕШКА: Маркерите липсват в index.html!")

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
