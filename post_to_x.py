import os
import tweepy
from google import genai

# Конфигурация на ключовете от GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_API = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_KEY_SECRET")
X_ACCESS = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

def get_latest_article():
    # Намира последната създадена статия в папката 'posts'
    posts = [f for f in os.listdir("posts") if f.endswith(".html")]
    posts.sort(key=lambda x: os.path.getmtime(os.path.join("posts", x)), reverse=True)
    return posts[0] if posts else None

def generate_tweet(title):
    client = genai.Client(api_key=GEMINI_KEY)
    prompt = f"Create a short, viral and engaging tweet for this article title: '{title}'. Include 2-3 hashtags and a call to action. Keep it under 240 characters. No emojis like 'robot'."
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text.strip()

def post_tweet():
    article_file = get_latest_article()
    if not article_file:
        return

    # Взема заглавието от името на файла или съдържанието
    title = article_file.replace("-", " ").replace(".html", "").capitalize()
    url = f"https://checkandcalc.com/posts/{article_file}"
    
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
