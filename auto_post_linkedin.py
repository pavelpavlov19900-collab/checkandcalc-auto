import requests, json, os

ACCESS_TOKEN = os.environ.get('AQUcW3nHGRClRKWhz3fMjyJRnPiQ2p1FUcgRB8EYaeAE0WB2LEM8_0JeuIQYg7hvy7dAGP_aYoBUBCDPEDxb_RgMRJe1JdBFyaTu7m6PVGdvG8gUXJOnUFKkMf8JnLrh5I-sLdCpmJHxA8SG4zW2-PZTwd1XwXunI4xZ4gu_jlDARA0cAUkmEaTKyPGeTFPfFLnawJoIZDrsSpcyc-zm0kCvsvnlsj58QTMQvnXo5ATK_PTNK2ZEaIQtcZ1adWzdYidhFQ3CLqExvFAmgftO7HVz0uEfLL0eXafH6r6YMVjNI5Q-g1sZSTb5lrbgvKbset-6MaiH-3YHV6_eVANt_iZp-PFK1g')
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
    post = next((p for p in posts if not p['published']), None)
    if not post: return

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
        print("✅ Успех!")

if __name__ == "__main__": post_to_linkedin()
