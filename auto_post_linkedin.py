import requests, json, os

# 🚨 ПОПРАВКАТА: Търсим ключа по неговото ИМЕ в GitHub Secrets!
ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
ORG_URN = 'urn:li:organization:112854903'

def upload_image(image_path, token):
    if not image_path or not os.path.exists(image_path): return None
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        reg_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
        reg_data = {"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], "owner": ORG_URN, "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]}
        
        r = requests.post(reg_url, headers=headers, json=reg_data).json()
        upload_url = r['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = r['value']['asset']

        with open(image_path, 'rb') as f:
            requests.post(upload_url, data=f, headers={'Authorization': f'Bearer {token}'})
        return asset
    except: return None

def post_to_linkedin():
    with open('posts_database.json', 'r', encoding='utf-8') as f: posts = json.load(f)
    post = next((p for p in posts if not p.get('published')), None)
    if not post: 
        print("Няма нови статии за публикуване.")
        return

    asset = upload_image(post.get('image_path'), ACCESS_TOKEN)
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}', 'X-Restli-Protocol-Version': '2.0.0', 'Content-Type': 'application/json'}
    
    media = {
        "status": "READY",
        "media": asset if asset else post['link'],
        "title": {"text": post['title']}
    }
    
    payload = {
        "author": ORG_URN, "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post['text']},
                "shareMediaCategory": "IMAGE" if asset else "ARTICLE",
                "media": [media]
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    res = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=payload)
    if res.status_code == 201:
        post['published'] = True
        with open('posts_database.json', 'w', encoding='utf-8') as f: json.dump(posts, f, indent=2, ensure_ascii=False)
        print("✅ Успех! Статията е публикувана в LinkedIn.")
    else:
        print(f"⚠️ Грешка при публикуване: {res.status_code} - {res.text}")

if __name__ == "__main__": post_to_linkedin()
