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
    
    # 🧠 ПОДОБРЕН ПРОМПТ: Даваме му "скелет" на съобщението
    prompt = (
        f"Generate a viral, high-energy Telegram hook for an article titled: '{title}'.\n"
        f"Requirements:\n"
        f"- Hook: 1 punchy opening sentence that grabs attention (NO starting with 'Forget').\n"
        f"- Value: 2 sentences explaining why this is a MUST-READ (the hidden secret or risk).\n"
        f"- Style: Use 4-5 dynamic emojis (e.g., 🚀, 🛡️, ⚠️, 🤖, 💥).\n"
        f"- Tone: Controversial, urgent, and professional.\n"
        f"- Output: Do not use hashtags. Write a full, engaging text, not clipped sentences."
    )
    
    import time
    import random
    
    # 3 опита за перфектен хук
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=200, # Увеличихме лимита
                    temperature=0.85
                )
            )
            
            hook = response.text.strip()
            
            # 🛡️ ВАЛИДАЦИЯ: Ако AI-то върне боклук или твърде кратък текст, опитай пак
            if len(hook) > 50: 
                return hook
            else:
                print(f"⚠️ Опит {attempt+1}: AI върна твърде кратък хук. Рестартирам...")
                
        except Exception as e:
            print(f"⚠️ Опит {attempt+1} се провали: {e}")
            time.sleep(2)
      
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
