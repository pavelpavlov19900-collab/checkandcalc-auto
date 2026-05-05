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
    """Чете файла БЕЗ да го променя (Read-Only) и вади снимка и текст."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Търсим първата картинка в HTML-а
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if not img_match:
            return None, None # Няма снимка, пропускаме статията
            
        img_src = img_match.group(1)
        # Правим линка абсолютен, за да може Facebook да го изтегли
        if not img_src.startswith('http'):
            img_src = urllib.parse.urljoin(BASE_URL, img_src)
            
        # Търсим първия параграф за грабващ текст (Hook)
        p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        hook_text = ""
        if p_match:
            raw_text = p_match.group(1)
            # Изчистваме HTML таговете, за да остане чист текст
            hook_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            # Взимаме първите ~250 символа, за да заинтригуваме аудиторията
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
    
    # Филтрираме - търсим само статии със снимки
    valid_articles = []
    for file in available:
        img, hook = extract_article_data(file)
        if img:
            valid_articles.append((file, img, hook))
            
    if not valid_articles:
        print("🔄 Всички статии със снимки са публикувани! Рестартираме конвейера...")
        open(HISTORY_FILE, 'w').close() # Изчистваме историята
        for file in all_files:
            img, hook = extract_article_data(file)
            if img:
                valid_articles.append((file, img, hook))

    if not valid_articles:
        print("❌ Фатална грешка: Няма нито една статия със снимка в хранилището!")
        return None, None, None

    chosen_file, chosen_img, chosen_hook = random.choice(valid_articles)
    
    # Записваме в историята, че сме я публикували
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        f.write(chosen_file + '\n')
        
    return chosen_file, chosen_img, chosen_hook

def post_to_facebook():
    if not TOKEN or TOKEN == "WAITING_FOR_META_APPROVAL":
        print("🏭 Factory Status: Missing Meta Token.")
        return

    chosen_file, img_url, hook_text = get_random_article()
    
    if not chosen_file:
        return

    clean_title = chosen_file.replace('.html', '').replace('-', ' ').capitalize()
    
    # Ако статията няма параграф, слагаме резервен текст
    if not hook_text:
        hook_text = f"Ready to upgrade your financial knowledge? 🚀 Dive into our latest breakdown: {clean_title}."

    utm_tags = urllib.parse.urlencode({
        'utm_source': 'facebook',
        'utm_medium': 'social_bot',
        'utm_campaign': 'first_comment_strategy'
    })
    
    article_link = f"{BASE_URL}{chosen_file}?{utm_tags}"
    
    # Форматираме текста за основния пост (Снимка + Текст)
    main_post_message = f"{hook_text}\n\n👇 Връзката към пълната статия е в първия коментар!"

    print(f"🔄 Избрана статия: {chosen_file}")
    print(f"📸 Открита снимка: {img_url}")
    
    # СТЪПКА 1: Публикуваме СНИМКАТА
    photo_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    photo_payload = {
        'url': img_url,
        'message': main_post_message,
        'access_token': TOKEN
    }

    try:
        print("🚀 Публикуване на главния пост...")
        photo_response = requests.post(photo_url, data=photo_payload)
        photo_response.raise_for_status()
        
        # Meta API връща 'post_id' (ID на публикацията) и 'id' (ID на самата картинка)
        response_data = photo_response.json()
        post_id = response_data.get('post_id') 
        
        if not post_id:
            post_id = response_data.get('id') 
            
        print(f"✅ УСПЕХ на главния пост! Post ID: {post_id}")
        
        # СТЪПКА 2: Пускаме линка в първия коментар
        print("💬 Добавяне на линка в първия коментар...")
        comment_url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
        comment_payload = {
            'message': f"🔗 Прочети цялата статия тук:\n{article_link}",
            'access_token': TOKEN
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
