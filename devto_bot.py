import os
import requests
import glob
import re

# Configuration
DEV_TO_TOKEN = os.environ.get('DEV_TO_TOKEN')
WEBSITE_URL = "https://checkandcalc.com"
HISTORY_FILE = "devto_history.txt"

print("🔍 Searching for the latest article...")

# Find the latest HTML file
html_files = glob.glob('*.html')
if not html_files:
    print("❌ No HTML files found.")
    exit(0)

latest_html = max(html_files, key=os.path.getmtime)
file_slug = latest_html.replace('.html', '')

# ANTI-DUPLICATE SHIELD: Check if we already published this
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        published_slugs = f.read().splitlines()
    if file_slug in published_slugs:
        print(f"⏩ Article '{file_slug}' has already been published to Dev.to. Skipping to protect the factory.")
        exit(0)

article_url = f"{WEBSITE_URL}/{latest_html}"
image_url = f"{WEBSITE_URL}/{file_slug}.png"

# Read the article content
with open(latest_html, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract title
title = file_slug.replace('-', ' ').title()
if '<title>' in content:
    title = content.split('<title>')[1].split('</title>')[0]

print(f"📄 Preparing to publish: {title}")

# --- ИНТЕЛИГЕНТНИЯТ ФИЛТЪР (Премахва шлюкавицата) ---
# 1. Изрязваме системните хедъри
content = re.sub(r'<head.*?>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
# 2. Изрязваме CSS дизайна (това, което се виждаше като код)
content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
# 3. Изрязваме скриптовете
content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)

# 4. Взимаме само съдържанието между <body> таговете (същината на статията)
body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
if body_match:
    content = body_match.group(1)

# --- ГАРАНТИРАНЕ НА СНИМКАТА ---
# Забиваме снимката най-отгоре в самата статия като Markdown
dev_content = f"![{title}]({image_url})\n\n" + content

# Добавяме SEO кредита
dev_content += f"<br><hr><p><em>🚀 Originally published at <a href='{article_url}'>checkandcalc.com</a>. Read more exclusive insights on our main site.</em></p>"

# API Payload
headers = {
    "api-key": DEV_TO_TOKEN,
    "Content-Type": "application/json"
}

payload = {
    "article": {
        "title": title,
        "body_markdown": dev_content,
        "published": True,
        "main_image": image_url, # Оставяме го и тук за всеки случай
        "canonical_url": article_url,
        "tags": ["ai", "tech", "seo", "automation"]
    }
}

print("🚀 Sending to Dev.to servers...")
response = requests.post("https://dev.to/api/articles", headers=headers, json=payload)

if response.status_code == 201:
    post_url = response.json().get('url')
    print(f"✅ Successfully published on Dev.to! Link: {post_url}")
    
    # Save to history so it never posts it again
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{file_slug}\n")
else:
    print(f"❌ Error publishing: {response.status_code}")
    print(response.text)
    exit(1)
