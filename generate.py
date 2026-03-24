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

   # --- СТЪПКА 3: ИНТЕЛЕКТУАЛНО СОРТИРАНЕ ПО КАТЕГОРИИ ---
    target_file = "index.html"
    
    # Използваме този формат, за да виждаш буквите в чата:
    s_start = "<" + "!-- SCAM_LIST_START --" + ">"
    s_end   = "<" + "!-- SCAM_LIST_END --" + ">"
    
    a_start = "<" + "!-- AI_LIST_START --" + ">"
    a_end   = "<" + "!-- AI_LIST_END --" + ">"
    
    y_start = "<" + "!-- YT_LIST_START --" + ">"
    y_end   = "<" + "!-- YT_LIST_END --" + ">"
    
    # 1. Сканираме всички генерирани статии
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', 'about.html', 'disclosure.html', 'privacy.html']]
    all_files.sort(key=os.path.getmtime, reverse=True)

    # Кошове за линковете
    scam_links, ai_links, yt_links = "", "", ""
    
    # Ключови думи за разпознаване
    ai_keywords = ['ai', 'detector', 'chatgpt', 'writing', 'human', 'deepfake']
    yt_keywords = ['youtube', 'earnings', 'money', 'views', 'rpm', 'adsense', 'cpm', 'tube']

    for file in all_files:
        pretty_title = file.replace('.html', '').replace('-', ' ').title()
        link_tag = f'          <li>🚀 <a href="{file}" style="color:#93c5fd;text-decoration:none;">{pretty_title}</a></li>\n'
        
        file_lower = file.lower()
        if any(k in file_lower for k in yt_keywords):
            yt_links += link_tag
        elif any(k in file_lower for k in ai_keywords):
            ai_links += link_tag
        else:
            scam_links += link_tag

    # 2. Четем index.html
    with open(target_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Функция за замяна
    def update_block(content, start, end, links):
        if start in content and end in content:
            parts = content.split(start)
            rest = parts[1].split(end)
            return parts[0] + start + "\n" + links + "          " + end + rest[1]
        return content

    # Обновяваме трите секции
    html_content = update_block(html_content, s_start, s_end, scam_links)
    html_content = update_block(html_content, a_start, a_end, ai_links)
    html_content = update_block(html_content, y_start, y_end, yt_links)

    # 4. Запазваме финалния резултат
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("🎯 Системата подреди всички статии по категории!")

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
