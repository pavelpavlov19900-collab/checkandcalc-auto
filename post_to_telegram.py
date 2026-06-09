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
    
    # 🎯 НОВ, ПОДОБРЕН ПРОМПТ (Базиран на успешните постове от март)
    prompt = (
        f"You are a professional tech writer. Write a Telegram post for an article titled: '{title}'.\n"
        f"Format the post exactly like this:\n"
        f"🚀 NEW ARTICLE:\n\n"
        f"[Engaging hook: A relatable question or alarming fact about the topic in 1-2 sentences that creates curiosity.]\n\n"
        f"[Value: A brief sentence explaining why the reader should care or how it protects them.]\n\n"
        f"🔗 Read full article here:\n"
        f"{title}\n\n" # Тук ще сложим линка в самия Python скрипт
        f"Requirements:\n"
        f"- Do NOT use 'Insider Update' or 'Forget'.\n"
        f"- Use 2-3 relevant emojis maximum.\n"
        f"- Tone: Alert, helpful, professional, and punchy."
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
        return

    title = filename.replace("-", " ").replace(".html", "").title()
    url = f"https://checkandcalc.com/{filename}"
    
    # Генерираме тялото с AI
    summary = generate_telegram_summary(title)
    
    # 💎 ЖЕЛЯЗНА СТРУКТУРА (Точно както искаш)
    # Премахваме hardcoded "Unlock..." и използваме изцяло форматирането от AI
    # Или по-добре: форматираме го тук, за да е консистентно
    
    # Преди: message = f"⚡ *INSIDER UPDATE:*\n\n{summary}..."
    # СЕГА (твоят предпочитан дизайн):
    message = f"{summary.replace(title, '')}\n🔗 Read full article here:\n{url}"

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
