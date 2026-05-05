import os
import requests
import random
import urllib.parse
import re

# 1. Вземаме тайните ключове
PAGE_ID = os.environ.get("FB_PAGE_ID")
TOKEN = os.environ.get("FB_PAGE_TOKEN") # Това е твоят System User Token
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
        print(f"⚠️ Грешка при четене на {filepath}: {e}")
        return None, None

def get_random_article():
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', '404.html']]
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            posted = f.read().splitlines()
    else:
        posted = []

    available = [f for f in all_files if f not in posted]
    valid_articles = []
    
    for file in available:
        img, hook = extract_article_data(file)
        if img:
            valid_articles.append((file, img, hook))
            
    if not valid_articles:
        print("🔄 Всички статии със снимки са публикувани! Рестартираме конвейера...")
        open(HISTORY_FILE, 'w').close()
        for file in all_files:
            img, hook = extract_article_data(file)
            if img:
                valid_articles.append((file, img, hook))

    if not valid_articles:
        print("❌ Фатална грешка: Няма нито една статия със снимка в хранилището!")
        return None, None, None

    chosen_file, chosen_img, chosen_hook = random.choice(valid_articles)
    
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(chosen_file + '\n')
        
    return chosen_file, chosen_img, chosen_hook

def post_to_facebook():
    if not TOKEN or TOKEN == "WAITING_FOR_META_APPROVAL":
        print("🏭 Factory Status: Missing Meta Token.")
        return

    # --- СТЪПКА 1: Взимаме "Бадж за Страницата" (Page Access Token) ---
    print("🔄 Стъпка 1: Обмяна на System User Token за Page Access Token...")
    token_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    try:
        token_response = requests.get(token_url)
        token_response.raise_for_status()
        page_access_token = token_response.json().get('access_token')
        print("✅ Успешно генериран Page Access Token!")
    except requests.exceptions.RequestException as e:
        print(f"❌ ГРЕШКА при обмяна на токена: {e}")
        if e.response is not None:
            print(f"Детайли от Meta: {e.response.json()}")
        return

    # --- СТЪПКА 2: Подготовка на съдържанието ---
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
    main_post_message = f"{hook_text}\n\n👇 Връзката към пълната статия е в първия коментар!"

    print(f"🔄 Избрана статия: {chosen_file}")
    print(f"📸 Открита снимка: {img_url}")
    
    # --- СТЪПКА 3: Публикуваме СНИМКАТА ---
    photo_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    photo_payload = {
        'url': img_url,
        'message': main_post_message,
        'access_token': page_access_token # Тук ВЕЧЕ използваме PAGE токена!
    }

    try:
        print("🚀 Публикуване на главния пост...")
        photo_response = requests.post(photo_url, data=photo_payload)
        photo_response.raise_for_status()
        
        response_data = photo_response.json()
        post_id = response_data.get('post_id') 
        if not post_id:
            post_id = response_data.get('id') 
            
        print(f"✅ УСПЕХ на главния пост! Post ID: {post_id}")
        
        # --- СТЪПКА 4: Пускаме линка в първия коментар ---
        print("💬 Добавяне на линка в първия коментар...")
        comment_url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
        comment_payload = {
            'message': f"🔗 Прочети цялата статия тук:\n{article_link}",
            'access_token': page_access_token # Използваме PAGE токена и тук!
        }
        
        comment_response = requests.post(comment_url, data=comment_payload)
        comment_response.raise_for_status()
        print("✅ УСПЕХ! Коментарът е добавен.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ГРЕШКА при комуникация с Meta: {e}")
        if e.response is not None:
            print(f"Детайли от сървъра: {e.response.json()}")

if __name__ == "__main__":
    post_to_facebook()
