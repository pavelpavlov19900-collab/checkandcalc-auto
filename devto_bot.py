import os
import requests
import glob
import re
import time
import random

# --- CONFIGURATION ---
DEV_TO_TOKEN = os.environ.get('DEV_TO_TOKEN')
WEBSITE_URL = "https://checkandcalc.com"
HISTORY_FILE = "devto_history.txt"
SERIES_NAME = "Financial Independence & Security 101" # The Dev.to Series Hack

print("🚀 Starting Premium Dev.to Publishing Pipeline...")

# 1. SEARCH AND CATEGORIZATION
html_files = glob.glob('*.html')
html_files.sort(key=os.path.getmtime, reverse=True) 

published_slugs = []
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        published_slugs = f.read().splitlines()

target_html = None
file_slug = None
found_image_path = None

# 2. STRICT QUALITY CONTROL
for html_file in html_files:
    slug = html_file.replace('.html', '')
    possible_images = glob.glob(f"{slug}.*")
    image_file = next((img for img in possible_images if img.lower().endswith(('.png', '.jpg', '.jpeg'))), None)

    if slug in published_slugs:
        continue
        
    if not image_file:
        print(f"⚠️ Skipping '{slug}': No image file found.")
        continue
        
    target_html = html_file
    file_slug = slug
    found_image_path = image_file
    break

if not target_html:
    print("✅ All eligible articles have been published. Pipeline resting.")
    exit(0)

article_url = f"{WEBSITE_URL}/{target_html}"
image_url = f"{WEBSITE_URL}/{found_image_path}"

# 3. CONTENT EXTRACTION
with open(target_html, 'r', encoding='utf-8') as f:
    content = f.read()

title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
title = title_match.group(1) if title_match else file_slug.replace('-', ' ').title()

print(f"📄 Preparing article: {title}")

# --- INTELLECTUAL PURIFICATION & MARKDOWN CONVERSION ---
# A. Remove invisible elements completely
content = re.sub(r'<(head|style|script).*?>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)

# B. Extract body
body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
content = body_match.group(1) if body_match else content

# C. Remove images (Main image is handled via API)
content = re.sub(r'<img.*?>', '', content, flags=re.IGNORECASE | re.DOTALL)
content = re.sub(r'<div[^>]*>\s*<a href="index\.html".*?</a>\s*</div>', '', content, flags=re.DOTALL | re.IGNORECASE)

# D. SMART MARKDOWN TRANSLATOR (Keeps structure for Dev.to)
content = re.sub(r'<h[1-2][^>]*>(.*?)</h[1-2]>', r'## \1\n\n', content, flags=re.IGNORECASE)
content = re.sub(r'<h[3-6][^>]*>(.*?)</h[3-6]>', r'### \1\n\n', content, flags=re.IGNORECASE)
content = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE)
content = re.sub(r'<strong[^>]*>(.*?)</strong>|<b[^>]*>(.*?)</b>', r'**\1\2**', content, flags=re.IGNORECASE)
content = re.sub(r'<li[^>]*>(.*?)</li>', r'* \1\n', content, flags=re.IGNORECASE)
content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.IGNORECASE)
content = re.sub(r'<[^>]+>', '', content) # Strip remaining raw tags
content = "\n".join([line.strip() for line in content.splitlines() if line.strip()])

# 4. DEV.TO FOOTER FORMATTING
dev_content = content 
dev_content += f"\n\n---\n\n> 🚀 **Originally published at [Check & Calc]({article_url})**. Explore our tools for financial independence."

# 5. DYNAMIC TAG ROTATION
all_tags = ["tech", "cybersecurity", "finance", "automation", "privacy", "crypto", "money", "productivity", "web3", "ai"]
selected_tags = random.sample(all_tags, 4)

# 6. API TRANSMISSION WITH RETRY LOGIC (ANTI-503 ARMOR)
headers = {"api-key": DEV_TO_TOKEN, "Content-Type": "application/json"}
payload = {
    "article": {
        "title": title,
        "body_markdown": dev_content,
        "published": True,
        "main_image": image_url, 
        "canonical_url": article_url,
        "tags": selected_tags,
        "series": SERIES_NAME 
    }
}

max_retries = 3
for attempt in range(max_retries):
    print(f"🔄 Publishing attempt {attempt + 1}/{max_retries}...")
    response = requests.post("https://dev.to/api/articles", headers=headers, json=payload)

    if response.status_code == 201:
        print(f"✅ SUCCESS! Article is live: {response.json().get('url')}")
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{file_slug}\n")
        break
    elif response.status_code >= 500:
        print(f"⚠️ Dev.to Server Error ({response.status_code}). Retrying in 30 seconds...")
        time.sleep(30)
    else:
        print(f"❌ Fatal Error {response.status_code}: {response.text}")
        break
else:
    print("❌ Failed to publish after maximum retries due to Dev.to server issues.")
