import os
import requests
import random  # ФИКСИРАНО: Вече няма да има NameError
import time    # ФИКСИРАНО: Изнесено на правилното място
from google import genai
from google.genai import types

# Конфигурация от GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "@checkandcalc_alerts"
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def get_latest_article():
    search_path = "posts" if os.path.exists("posts") else "."
    
    # 🛡️ ЗАЩИТА: Игнорираме всички системни файлове
    ignored_files = ["index.html", "404.html", "about.html", "privacy.html", "disclosure.html", "scam-checker.html", "google_verification.html"]
    
    # 🕵️‍♂️ УМЕН ФИЛТЪР: Вземаме само файлове, които завършват на .html
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

def generate_telegram_summary(title):
    """
    Генерира ЕДИНСТВЕНО ангажиращия текст (кукичката).
    Конструкцията на поста се поема изцяло от Python за максимална стабилност.
    """
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Изчистен и директен промпт без объркващи символи и структури
    prompt = (
        f"You are an expert copywriter and tech journalist. Write a compelling, high-engagement hook for a Telegram post based on this article title: '{title}'.\n\n"
        f"Requirements:\n"
        f"1. Write 1-2 sentences highlighting a hidden problem, danger, or mind-blowing fact related to the topic to grab instant attention.\n"
        f"2. Follow immediately with 1 sentence explaining the direct value the reader gets by checking this out.\n"
        f"3. Do NOT include any intro greetings, headers (like '🚀 NEW ARTICLE'), or meta-explanations.\n"
        f"4. Do NOT use the word 'Forget'.\n"
        f"5. Include 2-3 highly relevant emojis.\n\n"
        f"Output only the hook text:"
    )
    
    max_attempts = 5  # 5 опита са напълно достатъчни за новия промпт
    
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=150, 
                    temperature=0.85
                )
            )
            
            hook = response.text.strip()
            print(f"DEBUG [Опит {attempt+1}]: AI върна: '{hook}'")
            
            # Валидация: Тъй като искаме само чист текст, проверяваме за минимална дължина
            if len(hook) > 30 and "🚀" not in hook[0:15]: 
                return hook
            else:
                print(f"⚠️ Опит {attempt+1}: Филтърът отхвърли резултата (невалидна структура или твърде кратък).")
                time.sleep(2)
                
        except Exception as e:
            print(f"⚠️ Опит {attempt+1} се провали с грешка: {e}")
            time.sleep(3)
      
    # 🛡️ СТАБИЛЕН ОФЛАЙН РЕЗЕРВЕН ПЛАН
    print("❌ Всички опити до Gemini се провалиха или върнаха грешен формат. Активиране на офлайн кукички.")
    fallbacks = [
        "🚨 The tech industry doesn't want you thinking about this... Here is the realistic breakdown you need to see.",
        "🤯 Most people get this entirely wrong. Discover the real data and analysis behind this topic right now.",
        "⚠️ Critical update. If you want to optimize your results and avoid common traps, you cannot ignore this."
    ]
    return random.choice(fallbacks)

def send_telegram_msg():
    filename, full_path = get_latest_article()
    if not filename:
        print("Няма открити нови статии за публикуване.")
        return

    title = filename.replace("-", " ").replace(".html", "").title()
    url = f"https://checkandcalc.com/{filename}"
    
    # Генерираме само психологическата кукичка чрез AI или fallback
    hook_text = generate_telegram_summary(title)
    
    # 💎 ЖЕЛЯЗНА И КРАСИВА СТРУКТУРА (Сглобена безопасно в Python)
    message = (
        f"🚀 *NEW ARTICLE: {title}*\n\n"
        f"{hook_text}\n\n"
        f"🔗 *Read full article here:*\n"
        f"{url}"
    )

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
