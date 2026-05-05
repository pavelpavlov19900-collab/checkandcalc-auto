import os
import requests
import glob
import re

# --- КОНФИГУРАЦИЯ ---
DEV_TO_TOKEN = os.environ.get('DEV_TO_TOKEN')
WEBSITE_URL = "https://checkandcalc.com"
HISTORY_FILE = "devto_history.txt"

print("🚀 Старт на линията за премиум публикуване...")

# 1. ТЪРСЕНЕ И КАТЕГОРИЗАЦИЯ
html_files = glob.glob('*.html')
html_files.sort(key=os.path.getmtime, reverse=True) # От най-новите

published_slugs = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        published_slugs = f.read().splitlines()

target_html = None
file_slug = None
found_image_path = None

# 2. СТРОГ КАЧЕСТВЕН КОНТРОЛ (Само със снимка и непубликувани)
for html_file in html_files:
    slug = html_file.replace('.html', '')
    # Търсим всякакво разширение за снимка (png, jpg, jpeg)
    possible_images = glob.glob(f"{slug}.*")
    image_file = next((img for img in possible_images if img.lower().endswith(('.png', '.jpg', '.jpeg'))), None)

    if slug in published_slugs:
        continue
        
    if not image_file:
        print(f"⚠️ Пропускаме '{slug}' - липсва файл със снимка.")
        continue
        
    target_html = html_file
    file_slug = slug
    found_image_path = image_file
    break

if not target_html:
    print("✅ Всички статии със снимки са качени. Почивка за системата.")
    exit(0)

article_url = f"{WEBSITE_URL}/{target_html}"
image_url = f"{WEBSITE_URL}/{found_image_path}"

# 3. ЕКСТРАКЦИЯ НА СЪДЪРЖАНИЕТО
with open(target_html, 'r', encoding='utf-8') as f:
    content = f.read()

# Взимаме заглавието от <title> тага
title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
title = title_match.group(1) if title_match else file_slug.replace('-', ' ').title()

print(f"📄 Подготовка на: {title}")

# --- ИНТЕЛЕКТУАЛНО ПРЕЧИСТВАНЕ (Край на шлюкавицата и черните кутии) ---

# А. Махаме <head>, <style>, <script> изцяло
content = re.sub(r'<(head|style|script).*?>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)

# Б. Взимаме само чистия <body>
body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
content = body_match.group(1) if body_match else content

# В. ПРЕМАХВАМЕ ВСИЧКИ СНИМКИ ОТ ТЯЛОТО (Остава само главната в хедъра)
content = re.sub(r'<img.*?>', '', content, flags=re.IGNORECASE | re.DOTALL)

# Г. МАХАМЕ ЧЕРНИТЕ БАНЕРИ (Премахваме всички отстъпи в началото на редовете)
# Това убива Markdown логиката за "Code Block"
content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])

# Д. МАХАМЕ UI ЕЛЕМЕНТИ (Бутони "Back", Телеграм кутии и др.)
content = re.sub(r'<div[^>]*>\s*<a href="index\.html".*?</a>\s*</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
content = re.sub(r'<div class="premium-hook".*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)

# 4. ФИНАЛНО ФОРМАТИРАНЕ ЗА DEV.TO
# Тук не слагаме снимка в тялото, защото я подаваме като 'main_image' по-долу
dev_content = content 
dev_content += f"\n\n---\n\n> 🚀 **Originally published at [checkandcalc.com]({article_url})**. Explore our tools for financial independence."

# 5. ИЗПРАЩАНЕ КЪМ API
headers = {"api-key": DEV_TO_TOKEN, "Content-Type": "application/json"}

payload = {
    "article": {
        "title": title,
        "body_markdown": dev_content,
        "published": True,
        "main_image": image_url, # ТОВА Е ЕДИНСТВЕНАТА СНИМКА (най-отгоре)
        "canonical_url": article_url,
        "tags": ["tech", "automation", "productivity", "seo"]
    }
}

response = requests.post("https://dev.to/api/articles", headers=headers, json=payload)

if response.status_code == 201:
    print(f"✅ Успех! Статията е на живо: {response.json().get('url')}")
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{file_slug}\n")
else:
    print(f"❌ Грешка {response.status_code}: {response.text}")
