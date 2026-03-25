import os
import tweepy
from google import genai
import time

# Конфигурация
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_API = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_KEY_SECRET")
X_ACCESS = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

def get_latest_article():
    # Проверяваме първо в 'posts', ако я няма - в основната папка ('.')
    search_path = "posts" if os.path.exists("posts") else "."
    print(f"Searching for articles in: {search_path}")
    
    # Вземаме всички .html файлове, но изключваме index.html и 404.html
    ignored_files = ["index.html", "404.html", "google_verification.html"]
    posts = [f for f in os.listdir(search_path) if f.endswith(".html") and f not in ignored_files]
    
    if not posts:
        print("No articles found yet.")
        return None, None
        
    # Сортираме по време на последна промяна (най-новата най-отгоре)
    posts.sort(key=lambda x: os.path.getmtime(os.path.join(search_path, x)), reverse=True)
    
    latest_file = posts[0]
    full_path = os.path.join(search_path, latest_file)
    return latest_file, full_path

def generate_tweet(title):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = f"Create a short, viral and engaging tweet for this article title: '{title}'. Include 2-3 hashtags and a call to action. Keep it under 240 characters. No emojis like 'robot'."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text.strip()

def post_tweet():
    filename, full_path = get_latest_article()
    if not filename:
        return

    # Изчистваме името на файла за заглавие
    title = filename.replace("-", " ").replace(".html", "").capitalize()
    
    # Генерираме URL адреса (коригиран за GitHub Pages структура)
    url_path = f"posts/{filename}" if "posts" in full_path else filename
    url = f"https://checkandcalc.com/{url_path}"
    
    print(f"Preparing tweet for: {title}")
    tweet_content = generate_tweet(title)
    full_tweet = f"{tweet_content}\n\nRead more: {url}"

    # Twitter Аутентикация
    client = tweepy.Client(
        consumer_key=X_API, consumer_secret=X_API_SECRET,
        access_token=X_ACCESS, access_token_secret=X_ACCESS_SECRET
    )
    
    client.create_tweet(text=full_tweet)
    print(f"Successfully posted to X: {title}")

if __name__ == "__main__":
    post_tweet()
