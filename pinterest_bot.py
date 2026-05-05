import os
import glob
import base64
import requests
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# ⚙️ 1. КОНФИГУРАЦИЯ НА ФАБРИКАТА
# ==========================================
ACCESS_TOKEN = os.environ.get("PINTEREST_TOKEN") 
BOARD_ID = "1101904302519172134" 

IMAGES_FOLDER = "./" 
WEBSITE_BASE_URL = "https://checkandcalc.com/"
HISTORY_FILE = "pinterest_history.txt"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# ==========================================
# 🧠 2. ИНТЕЛИГЕНТНИ АСИСТЕНТИ
# ==========================================
def extract_seo_description(html_path):
    """(Иновация 2) Чете HTML файла и извлича първия параграф за перфектно SEO."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Търси мета описанието или първия параграф
        p_match = re.search(r'<p>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
        if p_match:
            # Изчистваме евентуални вътрешни HTML тагове (напр. <strong>, <a>)
            clean_text = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
            # Pinterest има лимит на описанието от 500 символа
            return clean_text[:450] + "..." if len(clean_text) > 450 else clean_text
    except Exception as e:
        print(f"⚠️ Грешка при четене на SEO: {e}")
    
    return "Check out our latest tools and comprehensive guides on achieving financial success!"

def download_premium_font():
    """Сваля професионален шрифт в движение, за да не се налага да качваш нищо в GitHub."""
    font_path = "Roboto-Bold.ttf"
    if not os.path.exists(font_path):
        print("📥 Изтегляне на премиум шрифт...")
        url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        response = requests.get(url)
        with open(font_path, 'wb') as f:
            f.write(response.content)
    return font_path

# ==========================================
# 🐉 3. ЛОГИКАТА НА "HYDRA" (Мултипликатор)
# ==========================================
def get_next_hydra_asset():
    """Намира следващата статия въз основа на това коя версия липсва."""
    published_records = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            published_records = f.read().splitlines()

    html_files = glob.glob('*.html')
    html_files.sort(key=os.path.getmtime, reverse=True) # От най-новите към най-старите

    # HYDRA ЛОГИКА: Търсим липсваща версия последователно. 
    # Първо покриваме всички с V1, после всички с V2, после V3.
    for target_version in ["v1", "v2", "v3"]:
        for html_file in html_files:
            slug = html_file.replace('.html', '')
            history_key = f"{slug}_{target_version}"
            
            if history_key not in published_records:
                # Търсим снимката
                possible_images = glob.glob(f"{IMAGES_FOLDER}{slug}.*")
                image_file = next((img for img in possible_images if img.lower().endswith(('.png', '.jpg', '.jpeg'))), None)
                
                if image_file:
                    title = slug.replace("-", " ").title()
                    link = f"{WEBSITE_BASE_URL}{html_file}"
                    seo_desc = extract_seo_description(html_file)
                    return image_file, title, link, seo_desc, history_key, target_version
                    
    return None, None, None, None, None, None

def create_scroll_stopper_image(img_path, title, version):
    """(Иновация 1) Генерира спиращ дъха дизайн с текст върху снимката, без да пипа оригинала."""
    print(f"🎨 Генериране на дизайн ({version}) за: {title}")
    
    # Избираме стила въз основа на версията (Разнообразие за алгоритъма)
    themes = {
        "v1": {"bg": (15, 23, 42), "text": (255, 255, 255), "prefix": ""}, # Тъмносин Slate
        "v2": {"bg": (6, 78, 59), "text": (255, 255, 255), "prefix": "Did you know?\n"}, # Изумрудено зелено
        "v3": {"bg": (88, 28, 135), "text": (255, 255, 255), "prefix": "New Calculator:\n"} # Кралско лилаво
    }
    theme = themes[version]
    
    # 1. Създаваме платното
    bg = Image.new('RGB', (1000, 1500), color=theme["bg"])
    img = Image.open(img_path)
    
    # 2. Оразмеряваме и центрираме оригиналната снимка
    w_percent = (1000 / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((1000, h_size), Image.Resampling.LANCZOS)
    y_offset = (1500 - h_size) // 2
    bg.paste(img, (0, y_offset))
    
    # 3. ДОБАВЯМЕ ТИПОГРАФИЯТА (Scroll-Stopper)
    draw = ImageDraw.Draw(bg)
    try:
        font_path = download_premium_font()
        title_font = ImageFont.truetype(font_path, 65)
        footer_font = ImageFont.truetype(font_path, 40)
    except:
        title_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # Форматираме заглавието
    full_title_text = f"{theme['prefix']}{title}"
    wrapped_title = textwrap.wrap(full_title_text, width=28)
    
    # Рисуваме заглавието в горната част (над снимката)
    text_y = 100
    for line in wrapped_title:
        # Изчисляваме ширината на текста, за да го центрираме
        left, top, right, bottom = draw.textbbox((0, 0), line, font=title_font)
        text_w = right - left
        text_x = (1000 - text_w) / 2
        draw.text((text_x, text_y), line, font=title_font, fill=theme["text"])
        text_y += bottom - top + 15
        
    # Рисуваме водния знак в долната част
    footer_text = "📍 checkandcalc.com"
    left, top, right, bottom = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_w = right - left
    draw.text(((1000 - footer_w) / 2, 1350), footer_text, font=footer_font, fill=(200, 200, 200))

    output_path = "pinterest_ready_temp.jpg"
    bg.save(output_path, quality=95)
    return output_path

# ==========================================
# 🚀 4. ИЗПРАЩАНЕ КЪМ PINTEREST
# ==========================================
def upload_to_pinterest(img_path, title, link, seo_desc, history_key):
    """Качва готовия Пин."""
    print("🚀 Изпращане към Pinterest API...")
    
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    payload = {
        "board_id": BOARD_ID,
        "title": f"{title[:90]} | Tools", # Pinterest title limit is 100
        "description": f"{seo_desc}\n\n#finance #business #automation #tools",
        "link": link,
        "media_source": {
            "source_type": "image_base64",
            "content_type": "image/jpeg",
            "data": encoded_string
        }
    }
    
    response = requests.post("https://api.pinterest.com/v5/pins", headers=headers, json=payload)
    if response.status_code == 201:
        print(f"✅ УСПЕХ! Пинът е жив: {link}")
        with open(HISTORY_FILE, 'a') as f:
            f.write(f"{history_key}\n")
    else:
        print(f"❌ Грешка при публикуване: {response.text}")

# ==========================================
# 🟢 СТАРТ НА МАШИНАТА
# ==========================================
if __name__ == "__main__":
    img_path, title, link, seo_desc, history_key, target_version = get_next_hydra_asset()
    
    if not img_path:
        print("✅ Фабриката е изчерпала всички 3 версии на всички статии. Чакаме нов код.")
        exit(0)
        
    ready_pin_path = create_scroll_stopper_image(img_path, title, target_version)
    upload_to_pinterest(ready_pin_path, title, link, seo_desc, history_key)
    
    if os.path.exists(ready_pin_path):
        os.remove(ready_pin_path)
        print("🧹 Следите са заличени. Архитектурата е в пълна безопасност.")
