import os
import requests
import random

# 1. Вземаме тайните ключове
PAGE_ID = os.environ.get("FB_PAGE_ID")
TOKEN = os.environ.get("FB_PAGE_TOKEN")
BASE_URL = "https://checkandcalc.com/"
HISTORY_FILE = "posted_articles.txt"

def get_random_article():
    # Сканираме директорията за .html файлове (без системните)
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', '404.html']]
    
    # Четем историята на публикуваните
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            posted = f.read().splitlines()
    else:
        posted = []

    # Филтрираме само тези, които още не са пускани
    available = [f for f in all_files if f not in posted]
    
    if not available:
        print("🔄 Всички статии са публикувани! Рестартираме списъка...")
        available = all_files
        posted = []

    chosen = random.choice(available)
    
    # Записваме в историята
    with open(HISTORY_FILE, 'a') as f:
        f.write(chosen + '\n')
        
    return chosen

def post_to_facebook():
    if TOKEN == "WAITING_FOR_META_APPROVAL" or not TOKEN:
        print("🏭 Factory Status: Waiting for Meta Token.")
        return

    # --- ИЗБОР НА СТАТИЯ ---
    chosen_file = get_random_article()
    article_link = f"{BASE_URL}{chosen_file}"
    # Превръщаме името на файла в заглавие за поста (махаме .html и тиретата)
    clean_title = chosen_file.replace('.html', '').replace('-', ' ').capitalize()
    post_message = f"Check out our latest insights: {clean_title}! 🚀 Read more here 👇 #Finance #CheckAndCalc"

    print(f"🔄 Избрана статия: {chosen_file}")
    
    # --- ТВОЯТ ОРИГИНАЛЕН КОД ЗА ТОКЕНА ---
    print("🔄 Стъпка 1: Обмяна на System User Token за Page Access Token...")
    token_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    try:
        token_response = requests.get(token_url)
        token_response.raise_for_status()
        token_data = token_response.json()
        page_access_token = token_data.get('access_token')
        print("✅ Успешно генериран Page Access Token!")
    except requests.exceptions.RequestException as e:
        print(f"❌ ГРЕШКА при взимане на Page Token: {e}")
        return

    # API крайна точка
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    payload = {
        'message': post_message,
        'link': article_link,
        'access_token': page_access_token
    }

    try:
        print(f"🚀 Публикуване на: {article_link}")
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print(f"✅ Success! Post ID: {response.json().get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    post_to_facebook()
