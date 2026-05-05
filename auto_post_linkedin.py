import requests
import json
import os
import urllib.parse
import time

ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')
ORG_URN = 'urn:li:organization:112854903'
DB_FILE = 'posts_database.json'

def upload_image(image_path, token):
    print(f"🕵️‍♂️ Scanning for image file: '{image_path}'...")
    absolute_path = os.path.abspath(image_path) if image_path else None
    
    if not absolute_path or not os.path.exists(absolute_path):
        print(f"❌ WARNING: Image not found at path: {absolute_path}")
        return None
        
    try:
        print("🔄 Step 1: Registering image upload with LinkedIn API...")
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

        r_response = requests.post(reg_url, headers=headers, json=reg_data)
        r_response.raise_for_status()
        r = r_response.json()
        
        upload_url = r['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
        asset = r['value']['asset']

        print("🚀 Step 2: Uploading image binary data...")
        with open(absolute_path, 'rb') as f:
            upload_req = requests.post(upload_url, data=f, headers={'Authorization': f'Bearer {token}'})
            upload_req.raise_for_status()
            
        print("✅ Image uploaded successfully!")
        return asset

    except Exception as e: 
        print(f"❌ Error during LinkedIn image upload: {e}")
        return None

def post_to_linkedin():
    if not ACCESS_TOKEN:
        print("🏭 Factory Status: Missing LinkedIn Access Token.")
        return

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f: 
            posts = json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file '{DB_FILE}' not found.")
        return

    post = next((p for p in posts if not p.get('published')), None)
    
    if not post: 
        print("🔄 All articles have been published. Waiting for new content.")
        return

    asset = upload_image(post.get('image_path'), ACCESS_TOKEN)
    
    utm_tags = urllib.parse.urlencode({
        'utm_source': 'linkedin',
        'utm_medium': 'social_bot',
        'utm_campaign': 'first_comment_strategy'
    })
    link_with_utm = f"{post['link']}?{utm_tags}"
    
    # ---------------------------------------------------------
    # THE FIX: Pure value text in the main body.
    # ---------------------------------------------------------
    base_text = post.get('text', f"Explore our latest insights on {post['title']}")
    # Clean up any leftover down-pointing emojis from old logic
    base_text = base_text.replace("👇", "").strip() 
    
    commentary = f"{base_text}\n\n👇 The link to the full guide is in the first comment!"

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}', 
        'X-Restli-Protocol-Version': '2.0.0', 
        'Content-Type': 'application/json'
    }
    
    if asset:
        media_content = {
            "status": "READY",
            "media": asset,  
            "title": {"text": post['title']}
        }
        share_category = "IMAGE"
    else:
        # Fallback to article link if image upload fails
        media_content = {
            "status": "READY",
            "originalUrl": link_with_utm,
            "title": {"text": post['title']}
        }
        share_category = "ARTICLE"
        commentary = base_text # Revert text if we are forced to post the link directly
    
    payload = {
        "author": ORG_URN, 
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": commentary}, 
                "shareMediaCategory": share_category,
                "media": [media_content] if asset or share_category == "ARTICLE" else []
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    print(f"🚀 Publishing main post for: {post['title']}")
    res = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=payload)
    
    if res.status_code == 201:
        # LinkedIn returns the Post URN in the 'X-RestLi-Id' header
        post_urn = res.headers.get('X-RestLi-Id')
        print(f"✅ Main post SUCCESS! Post URN: {post_urn}")
        
        # ---------------------------------------------------------
        # FIRST COMMENT STRATEGY EXECUTION
        # ---------------------------------------------------------
        if post_urn and asset:
            print("⏳ Waiting 7 seconds for LinkedIn to process the post...")
            time.sleep(7) # <--- ЕТО ТУК ЗАБАВЯМЕ БОТА
            
            print("💬 Adding the link in the first comment...")
            comment_url = f"https://api.linkedin.com/v2/socialActions/{post_urn}/comments"
            comment_payload = {
                "actor": ORG_URN,
                "message": {
                    "text": f"🔗 Read the full guide here:\n{link_with_utm}"
                }
            }
            comment_res = requests.post(comment_url, headers=headers, json=comment_payload)
            if comment_res.status_code == 201:
                print("✅ SUCCESS! Comment added.")
            else:
                print(f"⚠️ Warning: Failed to add comment. Code: {comment_res.status_code} - {comment_res.text}")

        # Update database state
        post['published'] = True
        with open(DB_FILE, 'w', encoding='utf-8') as f: 
            json.dump(posts, f, indent=2, ensure_ascii=False)
            
        print("🏭 Pipeline cycle completed successfully.")
    else:
        print(f"❌ Error during publishing: {res.status_code} - {res.text}")

if __name__ == "__main__": 
    post_to_linkedin()
