import requests
import json
import os

# 1. Вземаме токена от системните променливи (за сигурност)
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
ORG_ID = '112854903' 

def post_to_linkedin():
    # Зареждаме базата данни
    with open('posts_database.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)

    # Намираме първия непубликуван пост
    post_to_send = next((p for p in posts if not p['published']), None)

    if not post_to_send:
        print("Няма нови постове за публикуване.")
        return

    # Подготовка на данните
    url = 'https://api.linkedin.com/v2/ugcPosts'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }

    payload = {
        "author": f"urn:li:organization:{ORG_ID}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_to_send['text']},
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": post_to_send['link'],
                    "title": {"text": post_to_send['title']}
                }]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    # Изпращане
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f"✅ Успешно публикуван пост ID: {post_to_send['id']}")
        post_to_send['published'] = True
        # Запазваме обновената база данни
        with open('posts_database.json', 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_utf8=False)
    else:
        print(f"❌ Грешка: {response.json()}")

if __name__ == "__main__":
    post_to_linkedin()
