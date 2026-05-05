import os
import requests
import glob
import re

# Configuration
DEV_TO_TOKEN = os.environ.get('DEV_TO_TOKEN')
WEBSITE_URL = "https://checkandcalc.com"
HISTORY_FILE = "devto_history.txt"

print("🔍 Searching for the latest unpublished article WITH an image...")

# Намираме всички HTML файлове
html_files = glob.glob('*.html')
if not html_files:
    print("❌ No HTML files found.")
    exit(0)

# Подреждаме ги от най-новите към най-старите
html_files.sort(key=os.path.getmtime, reverse=True)

# Зареждаме списъка с вече публикувани статии
published_slugs = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        published_slugs = f.read().splitlines()

target_html = None
file_slug = None

# ТЪРСАЧЪТ С КАЧЕСТВЕН КОНТРОЛ
for html_file in html_files:
    slug = html_file.replace('.html', '')
    image_file = f"{slug}.png"
    
    # 1. Проверка дали вече е качена
    if slug in published_slugs:
        print(f"⏩ '{slug}' is already published. Checking next...")
        continue
        
    # 2. ПРОВЕРКА ЗА СНИМКА (Новият качествен контрол)
    if not os.path.exists(image_file):
        print(f"⚠️ '{slug}' doesn't have an image ({image_file}). Skipping to maintain premium quality!")
        continue
        
    # Ако мине и двете проверки, това е нашата статия!
    target_html = html_file
    file_slug = slug
    break

# Ако всички са публикувани или нямат снимки
if not target_html:
    print("✅ All eligible high-quality articles have been published. Waiting for new content.")
    exit(0)

article_url = f"{WEBSITE_URL}/{target_html}"
image_url = f"{WEBSITE_URL}/{file_slug}.png"

# Четем статията
with open(target_html, 'r', encoding='utf-8') as f:
    content = f.read()

# Извличаме заглавието
title = file_slug.replace('-', ' ').title()
if '<title>' in content:
    title = content.split('<title>')[1].split('</title>')[0]

print(f"📄 Preparing to publish: {title}")

# --- ИНТЕЛИГЕНТНИЯТ ФИЛТЪР (Премахва шлюкавицата на 100%) ---
content = re.sub(r'<head.*?>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
if body_match:
    content = body_match.group(1)

# --- ФОРМАТИРАНЕ ЗА DEV.TO ---
# Забиваме снимката най-отгоре, за да се вижда перфектно
dev_content = f"![{title}]({image_url})\n\n" + content

# SEO Кредит
dev_content += f"<br><hr><p><em>🚀 Originally published at <a href='{article_url}'>checkandcalc.com</a>. Read more exclusive insights on our main site.</em></p>"

# API Данни
headers = {
    "api-key": DEV_TO_TOKEN,
    "Content-Type": "application/json"
}

payload = {
    "article": {
        "title": title,
        "body_markdown": dev_content,
        "published": True,
        "main_image": image_url,
        "canonical_url": article_url,
        "tags": ["ai", "tech", "seo", "automation"]
    }
}

print("🚀 Sending to Dev.to servers...")
response = requests.post("https://dev.to/api/articles", headers=headers, json=payload)

if response.status_code == 201:
    post_url = response.json().get('url')
    print(f"✅ Successfully published on Dev.to! Link: {post_url}")
    
    # Записваме в дневника
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{file_slug}\n")
else:
    print(f"❌ Error publishing: {response.status_code}")
    print(response.text)
    exit(1)
