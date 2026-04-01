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

# --- НОВАТА, ОПТИМИЗИРАНА И БРОНИРАНА ФУНКЦИЯ ---
def generate_telegram_summary(title):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 🧠 OUT-OF-THE-BOX ПРОМПТ: Премахваме "опасните" думи от инструкцията.
    # Искаме точно структурата, която ти е носела успех: Въпрос -> Решение -> 2 Емоджита.
    prompt = f"Write a punchy, 2-sentence social media teaser for a tech blog post titled: '{title}'. Start with a relatable, engaging question to the reader. Use exactly 2 relevant emojis. Keep the tone helpful and focused on digital safety. No hashtags."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=150,
                temperature=0.7,
                # Сваляме предпазителите на макс
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE")
                ]
            )
        )
        
        if response and response.text:
            return response.text.strip()
        else:
            raise ValueError("Моделът мълчи.")
            
    except Exception as e:
        print(f"Грешка при Телеграм генерирането: {e}")
        # 🛡️ УЛТРА РЕЗЕРВЕН ПЛАН: Ако AI някога пак блокира много тежка хакерска тема, 
        # ние сами сглобяваме кука, която изглежда като истински генериран пост!
        fallback_hook = f"Think your digital assets are safe? ⚠️ Read our latest breakdown: {title}. Lock down your security now before it's too late. 🔒"
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
