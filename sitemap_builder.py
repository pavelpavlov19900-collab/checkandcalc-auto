import glob
import os
import re
from datetime import datetime

# Конфигурация
WEBSITE_URL = "https://checkandcalc.com"
SITEMAP_FILE = "sitemap.xml"

def build_sitemap():
    print(f"🛰️ Стартиране на интелигентна SEO ревизия...")
    
    # XML Хедър
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # 1. СТАТИЧНИ АКТИВИ (Основни инструменти)
    main_pages = [
        {"path": "/", "freq": "daily", "prio": "1.0"},
        {"path": "/scam-checker", "freq": "weekly", "prio": "0.9"},
        {"path": "/ai-detector", "freq": "weekly", "prio": "0.9"},
        {"path": "/youtube-money-calculator", "freq": "weekly", "prio": "0.9"}
    ]
    
    for page in main_pages:
        xml += f'  <url>\n'
        xml += f'    <loc>{WEBSITE_URL}{page["path"]}</loc>\n'
        xml += f'    <changefreq>{page["freq"]}</changefreq>\n'
        xml += f'    <priority>{page["prio"]}</priority>\n'
        xml += f'  </url>\n'

    # 2. ДИНАМИЧНИ АКТИВИ (Всички статии)
    html_files = glob.glob('*.html')
    file_data = []

    for file in html_files:
        # Пропускаме системни файлове
        if file in ['index.html', '404.html', 'google-verification.html', 'about.html', 'disclosure.html', 'privacy.html']:
            continue
            
        # ИСТИНСКАТА МАГИЯ: Четем датата директно от сърцевината на статията
        date_str = None
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Търсим реда "dateModified": "2026-05-xx"
                match = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"', content)
                if match:
                    date_str = match.group(1)
        except Exception as e:
            print(f"Грешка при четене на {file}: {e}")
        
        # Резервен вариант, ако статията е много стара и няма Schema
        if not date_str:
            mod_time = os.path.getmtime(file)
            date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
            
        file_data.append({'file': file, 'date': date_str})

    # Сортираме статиите от най-новите към най-старите базирано на истинската им дата
    file_data.sort(key=lambda x: x['date'], reverse=True)

    count = 0
    for item in file_data:
        xml += f'  <url>\n'
        xml += f'    <loc>{WEBSITE_URL}/{item["file"]}</loc>\n'
        xml += f'    <lastmod>{item["date"]}</lastmod>\n'
        xml += f'    <priority>0.80</priority>\n'
        xml += f'  </url>\n'
        count += 1

    xml += '</urlset>'

    # Записване на обновения файл
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml)
    
    print(f"✅ Готово! Sitemap е обновен с ИСТИНСКИТЕ исторически дати. Общо {count + len(main_pages)} адреса.")

if __name__ == "__main__":
    build_sitemap()
