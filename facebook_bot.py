import os
import requests

# 1. Вземаме тайните ключове от сейфа на GitHub
PAGE_ID = os.environ.get("FB_PAGE_ID")
TOKEN = os.environ.get("FB_PAGE_TOKEN")

# 2. Тук ще се връзваме с нашия AI генератор, но за сега задаваме структурата на английски!
# Примерно генерирано съдържание от gemini-2.5-pro:
post_message = "Is the 'Digital Nomad' lifestyle a trap? 🌴💻 Discover the hidden costs of remote work and how to protect your financial future. Read our latest deep dive! 👇 #RemoteWork #Finance #CheckAndCalc"
article_link = "https://checkandcalc.com/digital-nomad-trap" # Тук ще подаваме новия линк

def post_to_facebook():
    # Защита: Ако все още чакаме токена, скриптът просто си почива и не дава грешка.
    if TOKEN == "WAITING_FOR_META_APPROVAL" or not TOKEN:
        print("🏭 Factory Status: Waiting for Meta Token. Infrastructure is ready to fire!")
        return

    # API крайна точка за публикуване на постове с линкове
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    payload = {
        'message': post_message,
        'link': article_link,
        'access_token': TOKEN
    }

    try:
        print("🚀 Executing post to Facebook...")
        response = requests.post(url, data=payload)
        response.raise_for_status() # Проверява за грешки от сървъра
        print(f"✅ Success! Post published to Facebook. Post ID: {response.json().get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error publishing to Facebook: {e}")
        if response.content:
            print(f"Meta error details: {response.json()}")

if __name__ == "__main__":
    post_to_facebook()
