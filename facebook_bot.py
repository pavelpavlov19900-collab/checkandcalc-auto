import os
import requests

# 1. Вземаме тайните ключове от сейфа на GitHub
PAGE_ID = os.environ.get("FB_PAGE_ID")
TOKEN = os.environ.get("FB_PAGE_TOKEN") # В нашия случай това е System User Token-ът

# 2. Тук ще се връзваме с нашия AI генератор, но за сега задаваме структурата на английски!
# Примерно генерирано съдържание от gemini-2.5-pro:
post_message = "Is the 'Digital Nomad' lifestyle a trap? 🌴💻 Discover the hidden costs of remote work and how to protect your financial future. Read our latest deep dive! 👇 #RemoteWork #Finance #CheckAndCalc"
article_link = "https://checkandcalc.com/digital-nomad-trap" # Тук ще подаваме новия линк

def post_to_facebook():
    # Защита: Ако все още чакаме токена, скриптът просто си почива и не дава грешка.
    if TOKEN == "WAITING_FOR_META_APPROVAL" or not TOKEN:
        print("🏭 Factory Status: Waiting for Meta Token. Infrastructure is ready to fire!")
        return

    print("🔄 Стъпка 1: Обмяна на System User Token за Page Access Token...")
    
    # --- НОВОТО ПАРЧЕ КОД ЗА ОБМЯНА НА ТОКЕНА ---
    token_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}?fields=access_token&access_token={TOKEN}"
    try:
        token_response = requests.get(token_url)
        token_response.raise_for_status()
        token_data = token_response.json()
        page_access_token = token_data.get('access_token')
        print("✅ Успешно генериран Page Access Token!")
    except requests.exceptions.RequestException as e:
        print(f"❌ ГРЕШКА при взимане на Page Token: {e}")
        if 'token_response' in locals() and token_response.content:
            print(f"Детайли от Meta: {token_response.json()}")
        return # Спираме изпълнението, защото без този токен не можем да публикуваме
    # ---------------------------------------------

    # API крайна точка за публикуване на постове с линкове
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    payload = {
        'message': post_message,
        'link': article_link,
        'access_token': page_access_token # ВАЖНО: Тук вече подаваме токена за страницата!
    }

    try:
        print("🚀 Executing post to Facebook...")
        response = requests.post(url, data=payload)
        response.raise_for_status() # Проверява за грешки от сървъра
        print(f"✅ Success! Post published to Facebook. Post ID: {response.json().get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error publishing to Facebook: {e}")
        if 'response' in locals() and response.content:
            print(f"Meta error details: {response.json()}")

if __name__ == "__main__":
    post_to_facebook()
