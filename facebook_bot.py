import os
import requests
import random
import urllib.parse
import re

# 1. Вземаме тайните ключове
PAGE_ID = os.environ.get("FB_PAGE_ID")
TOKEN = os.environ.get("FB_PAGE_TOKEN") 
BASE_URL = "https://checkandcalc.com/"
HISTORY_FILE = "posted_articles.txt"

def extract_article_data(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not img_match:
            return None, None 
            
        img_src = img_match.group(1)
        if not img_src.startswith('http'):
            img_src = urllib.parse.urljoin(BASE_URL, img_src)
            
        p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        hook_text = ""
        if p_match:
            raw_text = p_match.group(1)
            hook_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            if len(hook_text) > 250:
                hook_text = hook_text[:247] + "..."
                
        return img_src, hook_text
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return None, None

def get_random_article():
    # 🛡️ ЗАЩИТА: Игнорираме системни файлове, архиви и стари страници
    ignored = ['index.html', '404.html', 'about.html', 'privacy.html', 'disclosure.html', 'scam-checker.html', 'google_verification.html']
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ignored and not f.startswith('category-')]
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            posted = f.read().splitlines()
    else:
        posted = []

    available = [f for f in all_files if f not in posted]
    valid_articles = []
    
    for file in available:
        img_url, hook = extract_article_data(file)
       
        # THE STRICT FILTER: Check for placeholders or broken links
        # ---------------------------------------------------------
        if img_url:
            if 'placeholder' in img_url.lower():
                print(f"⏭️ Skipping {file}: Found placeholder image tag.")
                continue
            
            # Извличаме името на файла от URL-а
            img_filename = os.path.basename(urllib.parse.urlparse(img_url).path)
            
            # Проверка дали файлът съществува в текущата папка
            if os.path.exists(img_filename):
                valid_articles.append((file, img_url, hook))
            else:
                # Ако няма файл, ползваме favicon.png като фалбек
                fallback_img = "https://checkandcalc.com/favicon.png"
                print(f"⚠️ Снимката {img_filename} не е намерена локално. Използвам фалбек за {file}.")
                valid_articles.append((file, fallback_img, hook))
            
    if not valid_articles:
        print("🔄 All articles with VALID images have been posted! Restarting the pipeline...")
        open(HISTORY_FILE, 'w').close()
        return None, None, None

    chosen_file, chosen_img, chosen_hook = random.choice(valid_articles)
    
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(chosen_file + '\n')
        
    return chosen_file, chosen_img, chosen_hook

def post_to_facebook():
    if not TOKEN or TOKEN == "WAITING_FOR_META_APPROVAL":
        print("🏭 Factory Status: Missing Meta Token.")
        return

    print("🔄 Step 1: Exchanging System User Token for Page Access Token...")
    token_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    try:
        token_response = requests.get(token_url)
        token_response.raise_for_status()
        page_access_token = token_response.json().get('access_token')
        print("✅ Page Access Token generated successfully!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Token exchange failed: {e}")
        return

    chosen_file, img_url, hook_text = get_random_article()
    if not chosen_file:
        return

    clean_title = chosen_file.replace('.html', '').replace('-', ' ').capitalize()
    if not hook_text:
        hook_text = f"Ready to upgrade your financial knowledge? 🚀 Dive into our latest breakdown: {clean_title}."

    utm_tags = urllib.parse.urlencode({
        'utm_source': 'facebook',
        'utm_medium': 'social_bot',
        'utm_campaign': 'first_comment_strategy'
    })
    
    article_link = f"{BASE_URL}{chosen_file}?{utm_tags}"
    
    # ---------------------------------------------------------
    # ПРОМЕНЕНО: Изцяло на английски с висококонвертиращ призив
    # ---------------------------------------------------------
    main_post_message = f"{hook_text}\n\n👇 The link to the full article is in the first comment!"

    # ---------------------------------------------------------
    # ЖЕЛЯЗНА ПОПРАВКА: Директен RAW линк от GitHub
    # ---------------------------------------------------------
    print(f"🔄 Selected article: {chosen_file}")
    
    # Използваме директен RAW линк към GitHub, за да няма 404 грешки
    img_filename = os.path.basename(urllib.parse.urlparse(img_url).path)
    raw_img_url = f"https://raw.githubusercontent.com/pavelpavlov19900-collab/checkandcalc-auto/main/{img_filename}"
    
    print(f"📸 Image final link: {raw_img_url}")
    
    photo_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    photo_payload = {
        'url': raw_img_url,
        'message': main_post_message,
        'access_token': page_access_token,
        'published': 'true'
    }

    try:
        print("🚀 Publishing the main post...")
        photo_response = requests.post(photo_url, params=photo_payload)
        photo_response.raise_for_status()
        
        response_data = photo_response.json()
        post_id = response_data.get('post_id') or response_data.get('id')
            
        print(f"✅ Main post SUCCESS! Post ID: {post_id}")
        
        # ---------------------------------------------------------
        # ПРОМЕНЕНО: Коментарът е на перфектен английски
        # ---------------------------------------------------------
        print("💬 Adding the link in the first comment...")
        comment_url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
        comment_payload = {
            'message': f"🔗 Read the full guide here:\n{article_link}",
            'access_token': page_access_token 
        }
        
        comment_response = requests.post(comment_url, data=comment_payload)
        comment_response.raise_for_status()
        print("✅ SUCCESS! Comment added.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Meta API Error: {e}")
        if e.response is not None:
            print(f"Server details: {e.response.json()}")

if __name__ == "__main__":
    post_to_facebook()
