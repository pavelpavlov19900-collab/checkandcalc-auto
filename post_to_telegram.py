import os
import requests
from google import genai
from google.genai import types # НОВО: Добавено за контрол на разходите

# Конфигурация от GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "@checkandcalc_alerts"
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def get_latest_article():
    search_path = "posts" if os.path.exists("posts") else "."
    
    # 🛡️ ЗАЩИТА: Игнорираме всички системни файлове
    ignored_files = ["index.html", "404.html", "about.html", "privacy.html", "disclosure.html", "scam-checker.html", "google_verification.html"]
    
    # 🕵️‍♂️ УМЕН ФИЛТЪР: Вземаме само файлове, които завършват на .html, не са в игнорираните и НЕ започват с "category-"
    posts = [f for f in os.listdir(search_path) 
             if f.endswith(".html") 
             and f not in ignored_files 
             and not f.startswith("category-")]
    
    if not posts:
        return None, None
        
    posts.sort(key=lambda x: os.path.getmtime(os.path.join(search_path, x)), reverse=True)
    latest_file = posts[0]
    full_path = os.path.join(search_path, latest_file)
    return latest_file, full_path

# --- НОВАТА, ОПТИМИЗИРАНА И БРОНИРАНА ФУНКЦИЯ ---
def generate_telegram_summary(title):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 🧠 OUT-OF-THE-BOX ПРОМПТ (Брутална копирайтинг психология)
    prompt = (
        f"Act as a controversial tech-insider who leaks highly guarded secrets. "
        f"Write an ultra-engaging, viral, 3-sentence Telegram teaser for an article titled: '{title}'. "
        f"RULE 1: First sentence triggers massive curiosity (e.g., 'Forget what they told you...'). "
        f"RULE 2: Second sentence highlights the hidden risk or massive benefit. "
        f"RULE 3: Final sentence forces them to click. "
        f"RULE 4: Use exactly 3 emojis. NO hashtags."
    )
    
    # 🛡️ БРОНИРАН ЛУП (3 ОПИТА) + FLASH МОДЕЛ + ТОКЕН ЛИМИТ
    import time
    import random
    attempts_config = [0, 3, 7] # Първо пробва веднага, после чака 3 сек, после 7 сек.
    
    for attempt, wait_time in enumerate(attempts_config):
        try:
            if wait_time > 0:
                print(f"⏳ Опит {attempt + 1}/3: Изчакване на API-то {wait_time} секунди...")
                time.sleep(wait_time)
                
            # Използваме най-бързия, евтин и надежден модел за кратки текстове
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=100, # 💰 РЕЖЕМ РАЗХОДИТЕ: Строг лимит до 100 токена!
                    temperature=0.9
                )
            )
            
            if response and response.text:
                return response.text.strip()
                
        except Exception as e:
            print(f"⚠️ Опит {attempt + 1} се провали: {e}")
            
    # 🛡️ ФИНАЛЕН РЕЗЕРВЕН ПЛАН (Ако Google е тотално паднал)
    print("❌ Всички 3 опита до Gemini се провалиха. Активиране на офлайн кукички.")
    fallbacks = [
        f"🚨 The tech industry doesn't want you thinking about this... Read the truth about: {title} 👇",
        f"🤯 Most people get this entirely wrong. Discover the real story behind: {title} 👇",
        f"⚠️ Critical update. If you use the internet, you need to read this breakdown: {title} 👇"
    ]
    return random.choice(fallbacks)

def send_telegram_msg():
    filename, full_path = get_latest_article()
    if not filename:
        print("No new articles to post.")
        return

    title = filename.replace("-", " ").replace(".html", "").title()
    # Винаги сочи към главната директория, за да няма 404 грешки
    url = f"https://checkandcalc.com/{filename}"
    
    # Генерираме интелигентно описание с AI
    summary = generate_telegram_summary(title)
    
    # 💎 ПРЕМИУМ ФОРМАТИРАНЕ НА СЪОБЩЕНИЕТО (Новият дизайн)
    message = f"⚡ *INSIDER UPDATE:*\n\n{summary}\n\n👉 *Unlock the full guide here:*\n{url}"

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        print(f"✅ Successfully posted HIGH-ENGAGEMENT hook to Telegram: {title}")
    else:
        print(f"Error posting to Telegram: {response.text}")

if __name__ == "__main__":
    send_telegram_msg()
