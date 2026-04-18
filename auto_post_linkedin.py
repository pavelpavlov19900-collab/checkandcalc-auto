import requests, json, os

ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
ORG_URN = 'urn:li:organization:112854903'

def upload_image(image_path, token):
    # --- ШПИОНИНЪТ ---
    print(f"🕵️‍♂️ Търся файла '{image_path}'. Ето какво виждам в текущата папка:")
    print(os.listdir('.')) 

    # --- РАДАРЪТ ---
    absolute_path = os.path.abspath(image_path) if image_path else None
    
    if not absolute_path or not os.path.exists(absolute_path):
        print(f"❌ ВНИМАНИЕ: Снимката не е намерена тук: {absolute_path}")
        return None
        
    try:
        # --- НОВИЯТ ОФИЦИАЛЕН ПЛИК (ЗАДАДЕН ОТ LINKEDIN) ---
        headers = {
            'Authorization': f'Bearer {token}', 
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        reg_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'
        
        reg_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], 
                "owner": ORG_URN, 
                "serviceRelationships": [
                    {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
                ]
            }
        }
        # ----------------------------------------------------

        r_response = requests.post(reg_url, headers=headers, json=reg_data)
        r = r_response.json()
        
        if 'value' not in r:
            print(f"❌ LinkedIn ОТХВЪРЛИ снимката! Техният отговор е: {r}")
            return None
            
        upload_url = r['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = r['value']['asset']

        with open(absolute_path, 'rb') as f:
            requests.post(upload_url, data=f, headers={'Authorization': f'Bearer {token}'})
        return asset

    except Exception as e: 
        print(f"Грешка при качване на снимката в LinkedIn: {e}")
        return None

def post_to_linkedin():
    with open('posts_database.json', 'r', encoding='utf-8') as f: posts = json.load(f)
    post = next((p for p in posts if not p.get('published')), None)
    if not post: 
        print("Няма нови статии за публикуване.")
        return

    asset = upload_image(post.get('image_path'), ACCESS_TOKEN)
    # 🔗 ПОПРАВКА ЗА ЛИНКА: Ако е пост със снимка, линкът трябва да е в текста
    commentary = post['text']
    link_with_utm = f"{post['link']}?utm_source=linkedin&utm_medium=social&utm_campaign=ai_bot"
    
    if asset:
        # Вмъкваме линка веднага след емоджито 👇 или го добавяме накрая
        if "👇" in commentary:
            commentary = commentary.replace("👇", f"👇\n{link_with_utm}")
        else:
            commentary += f"\n\n🔗 {link_with_utm}"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}', 'X-Restli-Protocol-Version': '2.0.0', 'Content-Type': 'application/json'}
    
    # 🚨 НОВАТА ЛОГИКА: Интелигентно превключване между Снимка и Линк
    if asset:
        media_content = {
            "status": "READY",
            "media": asset,  # За снимки LinkedIn иска това поле
            "title": {"text": post['title']}
        }
        share_category = "IMAGE"
    else:
        media_content = {
            "status": "READY",
            "originalUrl": f"{post['link']}?utm_source=linkedin&utm_medium=social&utm_campaign=ai_bot",
            "title": {"text": post['title']}
        }
        share_category = "ARTICLE"
    
    payload = {
        "author": ORG_URN, "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": commentary}, # ТУК използваме новата променлива
                "shareMediaCategory": share_category,
                "media": [media_content]
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
