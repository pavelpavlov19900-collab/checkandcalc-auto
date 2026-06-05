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
    
    # 🧠 OUT-OF-THE-BOX ПРОМПТ (Ролева игра за маркетинг)
    prompt = (
        f"Act as a world-class digital marketer and cyber-security expert. "
        f"Write a viral, punchy, 2-sentence Telegram hook for this article title: '{title}'. "
        f"Rule 1: Start with an alarming, curiosity-inducing question or a shocking fact. "
        f"Rule 2: Offer the solution in the second sentence. "
        f"Rule 3: Use exactly 3 highly expressive and relevant emojis (like 🤯, 🕵️‍♂️, 🚨, 💸, etc.) placed naturally. "
        f"Rule 4: Do not use hashtags."
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=150,
                temperature=0.9, # Повишаваме креативността за по-разнообразни текстове
                # Правилният синтаксис за сваляне на предпазителите в новото SDK
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                ]
            )
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            raise ValueError("Моделът мълчи (Празна генерация).")
            
    except Exception as e:
        print(f"Грешка при Телеграм генерирането: {e}")
        # 🛡️ РЕЗЕРВЕН ПЛАН (само ако има критичен срив на Google)
        fallback_hook = f"Are you making this critical tech mistake? ⚠️ Read our latest breakdown: {title}. Lock down your digital life before it's too late. 🛡️"
        return fallback_hook

def send_telegram_msg():
    filename, full_path = get_latest_article()
    if not filename:
        print("No new articles to post.")
        return

    title = filename.replace("-", " ").replace(".html", "").capitalize()
    # Винаги сочи към главната директория, за да няма 404 грешки
    url = f"https://checkandcalc.com/{filename}"
    
    # Генерираме интелигентно описание с AI
    summary = generate_telegram_summary(title)
    message = f"🚀 **NEW ARTICLE:**\n\n{summary}\n\n🔗 **Read full article here:**\n{url}"

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        print(f"Successfully posted to Telegram: {title}")
    else:
        print(f"Error posting to Telegram: {response.text}")

if __name__ == "__main__":
    send_telegram_msg()
