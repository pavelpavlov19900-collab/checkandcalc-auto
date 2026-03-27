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
    ignored_files = ["index.html", "404.html", "google_verification.html"]
    posts = [f for f in os.listdir(search_path) if f.endswith(".html") and f not in ignored_files]
    
    if not posts:
        return None, None
        
    posts.sort(key=lambda x: os.path.getmtime(os.path.join(search_path, x)), reverse=True)
    latest_file = posts[0]
    full_path = os.path.join(search_path, latest_file)
    return latest_file, full_path

# --- НОВАТА, ОПТИМИЗИРАНА ФУНКЦИЯ ---
def generate_telegram_summary(title):
    client = genai.Client(api_key=GEMINI_KEY)
    
    # Моделът е gemini-2.5-pro за най-добро качество на туитове/социални постове
    prompt = f"Create a very short, punchy Telegram post for this article: '{title}'. Use 2 relevant emojis, include a hook, and keep it under 3 sentences. No hashtags."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=150 # Финансова защита: Струва максимум $0.001
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Грешка при Телеграм генерирането: {e}")
        # Резервен спасителен текст, ако AI-ът е временно недостъпен
        return f"🚨 New Insider Intel Unlocked: {title}. Don't miss out!"

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
