import glob
import os
from datetime import datetime

# Конфигурация
WEBSITE_URL = "https://checkandcalc.com"
SITEMAP_FILE = "sitemap.xml"

def build_sitemap():
    print(f"🛰️ Стартиране на пълна SEO ревизия...")
    
    # XML Хедър
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # 1. СТАТИЧНИ АКТИВИ (Основни инструменти)
    # Тези винаги имат най-висок приоритет
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
    # Сканираме папката за абсолютно всичко генерирано до момента
    html_files = glob.glob('*.html')
    # Сортираме ги по дата, за да е подредено
    html_files.sort(key=os.path.getmtime, reverse=True)

    count = 0
    for file in html_files:
        # Пропускаме системни и вече добавени файлове
        if file in ['index.html', '404.html', 'google-verification.html']:
            continue
            
        mod_time = os.path.getmtime(file)
        date_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d')
        
        xml += f'  <url>\n'
        xml += f'    <loc>{WEBSITE_URL}/{file}</loc>\n'
        xml += f'    <lastmod>{date_str}</lastmod>\n'
        xml += f'    <priority>0.80</priority>\n'
        xml += f'  </url>\n'
        count += 1

    xml += '</urlset>'

    # Записване на обновения файл
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml)
    
    print(f"✅ Готово! Sitemap е обновен начисто с общо {count + len(main_pages)} адреса.")

if __name__ == "__main__":
    build_sitemap()
