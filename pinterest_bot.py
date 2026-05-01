import os
import glob
import base64
import requests
from PIL import Image

# ==========================================
# ⚙️ 1. КОНФИГУРАЦИЯ НА ФАБРИКАТА
# ==========================================
# Взимаме токена от сейфа на GitHub
ACCESS_TOKEN = os.environ.get("PINTEREST_TOKEN") 
# ТУК ПОСТАВЯШ ID-ТО НА ДЪСКАТА, КОЕТО ВЗЕ ОТ СТЪПКА 2
BOARD_ID = "1101904302519172134" 

# Път до снимките (ако генераторът ти ги пази в друга папка, смени './' с името на папката, напр. './images')
IMAGES_FOLDER = "./" 
WEBSITE_BASE_URL = "https://checkandcalc.com/"

# ==========================================
# 🛠️ 2. ЛОГИКАТА НА РОБОТА
# ==========================================
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_latest_asset():
    """Намира най-новата снимка в папката на проекта."""
    list_of_files = glob.glob(f'{IMAGES_FOLDER}/*.jpg') + glob.glob(f'{IMAGES_FOLDER}/*.png')
    if not list_of_files:
        print("❌ Не са намерени снимки в папката!")
        exit(1)
    
    latest_file = max(list_of_files, key=os.path.getctime)
    
    # Генерираме заглавие и линк от името на файла
    filename = os.path.basename(latest_file).split('.')[0]
    title = filename.replace("-", " ").capitalize()
    link = f"{WEBSITE_BASE_URL}{filename}"
    
    return latest_file, title, link

def create_pinterest_image(img_path, title):
    """Превръща хоризонталната снимка във вертикален Pinterest формат (1000x1500)."""
    print(f"🎨 Обработвам дизайна за: {title}")
    bg = Image.new('RGB', (1000, 1500), color=(20, 20, 30))
    img = Image.open(img_path)
    
    w_percent = (1000 / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((1000, h_size), Image.Resampling.LANCZOS)
    
    y_offset = (1500 - h_size) // 2
    bg.paste(img, (0, y_offset))
    
    output_path = "pinterest_ready.jpg"
    bg.save(output_path)
    return output_path

def upload_to_pinterest(img_path, title, link):
    """Качва готовия Пин директно в профила ти."""
    print("🚀 Изпращане към сървърите на Pinterest...")
    
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    payload = {
        "board_id": BOARD_ID,
        "title": f"{title} | Check&Calc",
        "description": f"Discover more about {title} on our website! Follow Check&Calc for professional tools and insights. #tech #digitaltools #businessgrowth",
        "link": link,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": encoded_string
        }
    }
    
    response = requests.post("https://api.pinterest.com/v5/pins", headers=headers, json=payload)
    if response.status_code == 201:
        print("✅ УСПЕХ! Пинът е публикуван и работи за теб!")
    else:
        print(f"❌ Грешка при публикуване: {response.json()}")

# ==========================================
# 🚀 3. СТАРТ НА МАШИНАТА
# ==========================================
if __name__ == "__main__":
    img_path, title, link = get_latest_asset()
    ready_pin_path = create_pinterest_image(img_path, title)
    upload_to_pinterest(ready_pin_path, title, link)
    
    # Почистване на временния файл
    if os.path.exists(ready_pin_path):
        os.remove(ready_pin_path)
