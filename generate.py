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
    # --- ГЕНЕРИРАНЕ ---
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=f"Write a 1000 word SEO article in English about: {topic_title}. Return ONLY the raw HTML body content (headings, paragraphs, lists). Do NOT include <html>, <head>, <style>, or <body> tags."
    )
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
# --- ПЕРФЕКТНИЯТ ДИЗАЙН (ШАБЛОН) ---
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_title}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #020617; color: #e2e8f0; line-height: 1.7; padding: 20px; margin: 0; }}
        .article-container {{ max-width: 800px; margin: 0 auto; background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }}
        h1 {{ color: #93c5fd; font-size: 2.2rem; margin-top: 0; margin-bottom: 25px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; line-height: 1.3; }}
        h2 {{ color: #bfdbfe; font-size: 1.6rem; margin-top: 35px; border-bottom: 1px dashed #1f2937; padding-bottom: 8px; }}
        h3 {{ color: #e0e7ff; font-size: 1.3rem; margin-top: 25px; }}
        a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }}
        a:hover {{ border-bottom: 1px solid #60a5fa; }}
        p {{ margin-bottom: 20px; font-size: 1.05rem; color: #cbd5e1; }}
        ul, ol {{ margin-bottom: 25px; color: #cbd5e1; font-size: 1.05rem; }}
        li {{ margin-bottom: 10px; }}
        strong {{ color: #f8fafc; }}
        .back-btn {{ display: inline-block; margin-top: 40px; padding: 12px 24px; background-color: #1e293b; color: #93c5fd; border-radius: 8px; border: 1px solid #334155; font-weight: bold; transition: all 0.2s; }}
        .back-btn:hover {{ background-color: #334155; color: #ffffff; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="article-container">
        {html_content}
        
        <div style="text-align: center;">
            <a href="index.html" class="back-btn">🚀 Back to Homepage</a>
        </div>
    </div>
</body>
</html>"""

    # Запазваме статията с новия луксозен дизайн
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)

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

# ==========================================
    # --- ЕДНОКРАТНА РЕНОВАЦИЯ НА СТАРИ СТАТИИ ---
    # ==========================================
    import re
    print("🛠️ Започвам реновация на старите статии...")
    
    # Сканираме всички файлове (all_files вече е заредено по-горе в кода ти)
    for file in all_files:
        with open(file, "r", encoding="utf-8") as f:
            old_content = f.read()
            
        # Проверяваме дали статията вече е с новия дизайн. Ако НЕ Е, я преправяме:
        if 'class="article-container"' not in old_content:
            print(f"👗 Обличам в нов костюм: {file}")
            
            # 1. Извличаме само полезния текст (махаме старите <html>, <head>, <body> тагове)
            meat = old_content
            if "<body" in meat.lower():
                meat = re.split(r'<body[^>]*>', meat, flags=re.IGNORECASE)[1]
                meat = re.split(r'</body>', meat, flags=re.IGNORECASE)[0]
            
            # Изчистваме всякакви остатъчни системни тагове от старото AI
            meat = re.sub(r'<!DOCTYPE.*?>', '', meat, flags=re.IGNORECASE)
            meat = re.sub(r'<html.*?>|</html>', '', meat, flags=re.IGNORECASE)
            meat = re.sub(r'<head.*?>.*?</head>', '', meat, flags=re.IGNORECASE | re.DOTALL)
            
            # 2. Генерираме красиво заглавие от името на файла
            nice_title = file.replace('.html', '').replace('-', ' ').title()
            
            # 3. Прилагаме новия шаблон
            new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{nice_title}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #020617; color: #e2e8f0; line-height: 1.7; padding: 20px; margin: 0; }}
        .article-container {{ max-width: 800px; margin: 0 auto; background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }}
        h1 {{ color: #93c5fd; font-size: 2.2rem; margin-top: 0; margin-bottom: 25px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; line-height: 1.3; }}
        h2 {{ color: #bfdbfe; font-size: 1.6rem; margin-top: 35px; border-bottom: 1px dashed #1f2937; padding-bottom: 8px; }}
        h3 {{ color: #e0e7ff; font-size: 1.3rem; margin-top: 25px; }}
        a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }}
        a:hover {{ border-bottom: 1px solid #60a5fa; }}
        p {{ margin-bottom: 20px; font-size: 1.05rem; color: #cbd5e1; }}
        ul, ol {{ margin-bottom: 25px; color: #cbd5e1; font-size: 1.05rem; }}
        li {{ margin-bottom: 10px; }}
        strong {{ color: #f8fafc; }}
        .back-btn {{ display: inline-block; margin-top: 40px; padding: 12px 24px; background-color: #1e293b; color: #93c5fd; border-radius: 8px; border: 1px solid #334155; font-weight: bold; transition: all 0.2s; }}
        .back-btn:hover {{ background-color: #334155; color: #ffffff; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="article-container">
        {meat.strip()}
        
        <div style="text-align: center;">
            <a href="index.html" class="back-btn">🚀 Back to Homepage</a>
        </div>
    </div>
</body>
</html>"""
            
            # 4. Записваме обновения файл върху стария
            with open(file, "w", encoding="utf-8") as f:
                f.write(new_html)
                
    print("✅ Всички стари статии са успешно реновирани и изглеждат перфектно!")
