import re
import os, datetime, random, json, requests, glob # Добавка
from PIL import Image # <--- ЕТО Я НОВАТА ДОБАВКА ТУК (Пресата за снимки)
from google import genai
from google.genai import types  # НОВО: Нужно ни е за контрол на разходите!

# ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
G_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") # Трябва да го добавиш в GitHub Secrets

# --- ХИРУРГ ЗА ВЪТРЕШНИ ЛИНКОВЕ (SEO ПАЯЖИНА) ---
def inject_surgical_links(html_content, current_filename):
    print("🕸️ Изграждане на SEO паяжина (Internal Links)...")
    
    # 🛡️ ЗАЩИТЕН ЩИТ: Никога не пипай системните файлове и архивите!
    system_files = ['index.html', 'about.html', 'privacy.html', 'disclosure.html', 'scam-checker.html', '404.html']
    if current_filename in system_files or current_filename.startswith('category-'):
        return html_content
    
    all_files = glob.glob('*.html')
    # Избираме линкове само от истинските статии
    valid_files = [f for f in all_files if f not in system_files and not f.startswith('category-') and f != current_filename]

    if len(valid_files) < 2:
        return html_content 

    import random
    import re
    chosen = random.sample(valid_files, 2)

    def build_ui_block(filename):
        title = filename.replace('.html', '').replace('-', ' ').title()
        return f"""
        <div style="margin: 30px 0; padding: 18px 24px; border-left: 4px solid #00ffcc; background-color: rgba(0, 255, 204, 0.05); border-radius: 0 8px 8px 0; font-family: inherit;">
            <span style="font-size: 1.1em; color: #00ffcc; margin-right: 10px;">💡 <strong>Read Next:</strong></span>
            <a href="{filename}" style="color: inherit; text-decoration: underline; font-weight: bold;">{title}</a>
        </div>
        """

    link1 = build_ui_block(chosen[0])
    link2 = build_ui_block(chosen[1])

    p_tags = [m.start() for m in re.finditer(r'</p>', html_content, re.IGNORECASE)]

    if len(p_tags) >= 6:
        pos2 = p_tags[4] + 4
        html_content = html_content[:pos2] + link2 + html_content[pos2:]
        pos1 = p_tags[1] + 4
        html_content = html_content[:pos1] + link1 + html_content[pos1:]
    elif len(p_tags) >= 3:
        pos1 = p_tags[1] + 4
        html_content = html_content[:pos1] + link1 + html_content[pos1:]

    return html_content

# --- ОБНОВЕНА ФУНКЦИЯ ЗА LINKEDIN (С ПОДДРЪЖКА НА СНИМКА) ---
def update_linkedin_database(article_title, article_url, article_summary, image_file=None):
    db_path = 'posts_database.json'
    if not os.path.exists(db_path):
        with open(db_path, 'w', encoding='utf-8') as f: json.dump([], f)
    with open(db_path, 'r', encoding='utf-8') as f:
        try: posts = json.load(f)
        except: posts = []
    new_id = max([p['id'] for p in posts], default=0) + 1
    new_entry = {
        "id": new_id, "title": article_title,
        "text": f"🚨 {article_summary}\n\nRead the full deep-dive here 👇\n#AI #Security #CheckAndCalc",
        "link": article_url, 
        "image_path": image_file, # <--- НОВО
        "published": False
    }
    posts.append(new_entry)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    print(f"✅ Добавено към LinkedIn опашката!")

# --- TRIPLE REDUNDANCY FUNCTION: GOOGLE + POLLINATIONS + HUGGING FACE (Titanium Edition) ---
def generate_ai_image(client, prompt, project_id, filename):
    print(f"🎨 Задействане на Трислойния протокол за визия (Titanium Edition)...")
    
    image_prompt = f"Professional futuristic digital art, cyberpunk style, high contrast, representing: {prompt}"
    image_name = filename.replace('.html', '.png')
    
    import time
    import urllib.parse
    import requests
    import random
    import os
    from PIL import Image

    spoof_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    
    success_source = None

    # ==========================================================
    # СЛОЙ 1: GOOGLE IMAGEN (План А - Опит за качество)
    # ==========================================================
    print("🎯 СЛОЙ 1: Опит през Google Cloud Imagen...")
    google_attempts = [0, 5] 
    
    for i, wait_time in enumerate(google_attempts):
        try:
            if wait_time > 0:
                print(f"⏳ Изчакване {wait_time} сек (Опит {i+1}/2)...")
                time.sleep(wait_time)

            method_name = next((name for name in ['generate_images', 'generate_image'] if hasattr(client.models, name)), None)
            if not method_name: raise Exception("SDK метод не е намерен.")

            method = getattr(client.models, method_name)
            response = method(
                model='imagen-4.0-generate-001',
                prompt=image_prompt,
                config={'number_of_images': 1, 'aspect_ratio': '16:9'}
            )

            if hasattr(response, 'generated_images') and response.generated_images:
                image_obj = response.generated_images[0].image
            elif hasattr(response, 'images') and response.images:
                image_obj = response.images[0]
            elif isinstance(response, list) and len(response) > 0:
                image_obj = response[0]
            else:
                image_obj = response
                
            image_obj.save(image_name)
            success_source = "Google Imagen"
            print(f"✅ Успех чрез Слой 1 (Google Imagen)!")
            break 
        except Exception as e:
            print(f"⚠️ Слой 1 (Google) се провали: {e}")

    # ==========================================================
    # СЛОЙ 2: POLLINATIONS AI (План Б - Поправен от 402 Грешка)
    # ==========================================================
    if not success_source:
        print("🔄 СЛОЙ 2: Активиране на Резервния двигател (Pollinations)...")
        try:
            safe_prompt = urllib.parse.quote(image_prompt)
            fallback_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1200&height=675&seed={random.randint(1,100000)}"
            
            img_response = requests.get(fallback_url, headers=spoof_headers, stream=True, timeout=30)
            
            if img_response.status_code == 200:
                with open(image_name, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
                success_source = "Pollinations AI"
                print("✅ Успех чрез Слой 2 (Pollinations AI)!")
            else:
                raise Exception(f"Сървърът върна статус: {img_response.status_code}")
        except Exception as e:
            print(f"⚠️ Слой 2 (Pollinations) също се провали: {e}")

    # ==========================================================
    # СЛОЙ 3: HUGGING FACE STABLE DIFFUSION (Новият Авариен щит)
    # ==========================================================
    if not success_source:
        print("🚨 СЛОЙ 3: Активиране на Индустриалния щит (Hugging Face SDXL)...")
        try:
            hf_token = os.environ.get("HF_TOKEN", "") 
            
            hf_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
            hf_headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
            hf_payload = {"inputs": image_prompt}
            
            hf_response = requests.post(hf_url, headers=hf_headers, json=hf_payload, timeout=45)
            
            if hf_response.status_code == 200:
                with open(image_name, 'wb') as f:
                    f.write(hf_response.content)
                success_source = "Hugging Face SDXL"
                print("✅ Успех чрез Слой 3 (Hugging Face)!")
            else:
                raise Exception(f"Hugging Face върна статус: {hf_response.status_code}. (Може би липсва HF_TOKEN)")
        except Exception as e:
            print(f"⚠️ Слой 3 (Hugging Face) се провали: {e}")

    # ==========================================================
    # СЛОЙ 4: АБСОЛЮТЕН ФАЛБЕК (Защита от счупен сайт)
    # ==========================================================
    if not success_source:
        print("🛡️ СЛОЙ 4: Всичко се провали. Генериране на резервен градиент, за да не се счупи HTML-ът.")
        try:
            img = Image.new('RGB', (1200, 675), color = (15, 23, 42)) 
            img.save(image_name)
            success_source = "Local Fallback Placeholder"
            return image_name
        except:
            return None

    # ==========================================================
    # ФИНАЛ: Обработка 
    # ==========================================================
    if success_source and success_source != "Local Fallback Placeholder":
        try:
            with Image.open(image_name) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img = img.resize((1200, 675), Image.Resampling.LANCZOS)
                img.save(image_name, format="PNG", optimize=True)
            print(f"✅ Снимката е компресирана и готова: {image_name} (Източник: {success_source})")
            return image_name
        except Exception as e:
            print(f"⚠️ Грешка при компресията: {e}")
            return image_name 
            
    return image_name
try:
    # 1. ИЗБОР НА УНИКАЛНА ТЕМА
    if not os.path.exists('topics.txt'):
        print("Липсва topics.txt!")
        exit()

    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]

    existing_files = os.listdir('.')
    available = []
    
    for t in topics:
        temp_slug = t.lower().replace(' ', '-')
        temp_slug = re.sub(r'[^a-z0-9-]', '', temp_slug)
        temp_slug = re.sub(r'-+', '-', temp_slug).strip('-') + ".html"
        
        if temp_slug not in existing_files:
            available.append(t)

    if not available:
        print("Всички теми са изчерпани!")
        exit()

    topic_title = random.choice(available)
    clean_name = topic_title.lower().replace(' ', '-')
    clean_name = re.sub(r'[^a-z0-9-]', '', clean_name)
    filename = re.sub(r'-+', '-', clean_name).strip('-') + ".html"

   # 2. ГЕНЕРИРАНЕ (С УЛТРА-ЕВТИН FLASH + FALLBACK ЗАЩИТА + ГЕО + 400 ДУМИ)
    # 2. ГЕНЕРИРАНЕ НА СТАТИЯТА (THE GURU PROMPT)
    prompt_text = (
        f"You are a highly respected, 15-year veteran Cybersecurity Expert and IT System Administrator. "
        f"Write a massive, definitive, and highly practical guide in English about: {topic_title}. "
        f"\n\n--- CRITICAL PERSONA & TONE RULES --- "
        f"\n1. TONE: Speak directly to the reader like a mentor explaining a complex tech issue to a smart friend. Be conversational, punchy, and brutally honest. "
        f"\n2. BANNED AI-ISMS: You are FORBIDDEN from using robotic AI phrases like: 'In today's digital landscape', 'Delve into', 'It is important to note', 'Navigating the complexities', 'A tapestry of'. "
        f"\n3. READABILITY: Use simple, plain English. Explain technical terms with real-world analogies (e.g., 'A firewall is like a bouncer at a club'). Keep paragraphs under 4 sentences. "
        f"\n4. NO FLUFF: Zero empty talk. Every single sentence must provide undeniable value, a fact, or actionable advice. "
        f"\n\n--- STRICT STRUCTURAL RULES --- "
        f"\n1. START with the main title in <h1> tags. "
        f"\n2. IMMEDIATELY AFTER the <h1>, generate a <div class='ai-answer-box'><h2>Quick Answer (TL;DR)</h2><ul>...</ul></div> with 3 ultra-concise, factual bullet points summarizing the solution using <strong> tags. "
        f"\n3. Generate an engaging Introduction, EXACTLY 5 to 7 main sections using <h2> tags, and a Conclusion. "
        f"\n4. ADDED VALUE: Under at least two <h2> sections, include a '💡 Expert IT Tip:' formatted nicely, giving a secret industry workaround or specific tool recommendation. "
        f"\n5. DEPTH & LENGTH: You MUST write AT LEAST 350-450 WORDS under EACH <h2> section. Dive deep into the 'Why' and the 'How-to'. "
        f"\n6. NO REPETITION: Never repeat a concept or a paragraph. Once an idea is explained, move to the next logical step. "
        f"\n7. FORMAT STRICTLY IN HTML with <p>, <ul>, <li>, <strong> tags. NO MARKDOWN. "
        f"\n8. Do not stop mid-sentence. Ensure all HTML tags are perfectly closed. "
        f"\n\nIMPORTANT: After the final HTML tag, add exactly this separator '---LINKEDIN-HOOK---' "
        f"followed by a one-sentence provocative summary for a LinkedIn post."
    )
    # --- СТЪПКА 2: БРОНИРАНА СТРАТЕГИЯ С 10 ОПИТА ---
    import time
    response = None

    # Новата конфигурация: 1, 2, 3, 5, 15, 25, 30 минути с Flash, 
    # последвани от 45 и 50 минути с Pro. 
    # Времената са в секунди с добавен "Jitter" (асиметрия) за избягване на сървърни пикове.
    attempts_config = [
        ('gemini-2.5-flash', 0),       
        ('gemini-2.5-flash', 63),      
        ('gemini-2.5-flash', 127),     
        ('gemini-2.5-flash', 184),     
        ('gemini-2.5-flash', 311),     
        ('gemini-2.5-flash', 913),     
        ('gemini-2.5-flash', 1517),    
        ('gemini-2.5-flash', 1823),    
        ('gemini-2.5-pro', 2731),         
        ('gemini-2.5-pro', 3041)          
    ]

    for i, (model_name, wait_time) in enumerate(attempts_config):
        attempt_num = i + 1
        try:
            if wait_time > 0:
                print(f"⏳ Сървърът е претоварен. Изчакване {wait_time // 60} мин и {wait_time % 60} сек (Опит {attempt_num}/7)...")
                time.sleep(wait_time)

            print(f"Опит {attempt_num}: Генериране с {model_name}...")
            
            # Конфигурация: Flash пести ресурси, Pro използва максимална мощност
            if 'flash' in model_name:
                gen_config = types.GenerateContentConfig(max_output_tokens=6000, temperature=0.7)
            else:
                gen_config = types.GenerateContentConfig(max_output_tokens=6000)

            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=gen_config
            )
            
            # 🛑 QA ПАЗАЧ (CONTENT ENFORCER) 🛑
            if response and response.text:
                # 1. Броим думите в суровия отговор
                word_count = len(response.text.split())
                
                # 2. Ако са под 1200, направо "чупим" опита и го караме да пише пак
                if word_count < 1200:
                    raise ValueError(f"AI-то мързелува! Написа само {word_count} думи. Изискват се минимум 1200. Изхвърляме и опитваме отново.")
                
                # 3. Ако мине теста, обявяваме победа
                print(f"✅ АБСОЛЮТЕН УСПЕХ при опит {attempt_num} с модел {model_name}! (Обем: {word_count} думи 🏆)")
                break

        except Exception as e:
            print(f"⚠️ Опит {attempt_num} не успя поради грешка: {e}")
            if attempt_num == len(attempts_config):
                print("❌ Критичен срив: Всички 7 стратегически опита се провалиха. Google е напълно недостъпен.")
                exit()
    # --- КРАЙ НА БРОНИРАНАТА СТРАТЕГИЯ ---

# 1. Първо изчистваме целия отговор от Gemini и го записваме в raw_text
    raw_text = response.text.replace('```html', '').replace('```', '').strip()

    # 2. Разделяме на статия, LinkedIn кукичка и визуален промпт
    visual_description = f"Technology concept related to {topic_title}" # Резервен вариант
    
    if "---LINKEDIN-HOOK---" in raw_text:
        # Първо цепим статията от всичко останало
        parts = raw_text.split("---LINKEDIN-HOOK---")
        html_content = parts[0].strip()
        remaining_data = parts[1]
        
        # Сега проверяваме дали имаме визуален промпт в останалата част
        if "---VISUAL-PROMPT---" in remaining_data:
            linkedin_hook, visual_description = remaining_data.split("---VISUAL-PROMPT---")
            linkedin_hook = linkedin_hook.strip()
            visual_description = visual_description.strip()
        else:
            linkedin_hook = remaining_data.strip()
    else:
        # План Б: Ако Gemini забрави разделителите
        html_content = raw_text
        linkedin_hook = f"New security insights about {topic_title} are now live!"

    # --- ТУК Е МАГИЯТА: ГЕНЕРИРАНЕ НА СНИМКАТА ---
    # Извикваме новата функция, която сложихме по-горе
    image_name = generate_ai_image(client, visual_description, G_PROJECT, filename)
    
   # 3. 🛡️ ПРЕДПАЗИТЕЛ ЗА ЗАВЪРШЕНОСТ (Умен филтър срещу празни секции и двойни заключения)
    html_content = html_content.strip()
    
    # ХАК 1: Ако AI-то е прекъснало веднага след заглавие (няма текст под него), изрязваме заглавието, за да няма празни пространства
    last_h2_match = list(re.finditer(r'<h2>.*?</h2>', html_content, re.IGNORECASE))
    if last_h2_match:
        last_match = last_h2_match[-1]
        after_last_h2 = html_content[last_match.end():].strip()
        if len(after_last_h2) < 15: # Ако след заглавието има под 15 символа, значи е празно и увиснало
            html_content = html_content[:last_match.start()].strip()

    # ХАК 2: Проверяваме дали моделът вече сам си е генерирал секция за заключение
    has_conclusion = "conclusion" in html_content.lower()[-600:]

    # ХАК 3: Проверка и интелигентно затваряне на HTML структурата
    if not (html_content.endswith('</p>') or html_content.endswith('</ul>') or html_content.endswith('</li>') or html_content.endswith('</div>')):
        if has_conclusion:
            # Ако има заключение, но просто тагът е леко отрязан, го затваряме чисто
            if not html_content.endswith('>'):
                html_content += "</p>"
        else:
            # Ако статията наистина е прекъсната по средата и няма заключение, инжектираме неутрално, високопрофесионално такова
            html_content += "... and implement these analytical steps to ensure long-term optimization.</p><h2>Conclusion</h2><p>In conclusion, evaluating these technical data points and staying proactive is essential for achieving digital growth, minimizing hidden strategic overhead, and building a highly scalable structure.</p>"
    elif not has_conclusion:
        # Ако статията е затворена правилно, но моделът е забравил да напише Conclusion секция, я добавяме луксозно
        html_content += "\n<h2>Conclusion</h2><p>In summary, leveraging these actionable metrics and utilizing transparent structures allows you to mitigate operational risks, protect your digital assets, and drive data-centric efficiency forward.</p>"
    # 4. 🚀 Вземаме точната дата за SEO Schema Markup
    today_iso = datetime.date.today().isoformat()

    # --- МОДУЛ ЗА АВТОМАТИЧНА МОНЕТИЗАЦИЯ (CTA GENERATOR) - FINAL 2026 ---
    topic_lower = topic_title.lower()
    
    # Твоите активирани "Golden Tier" афилиейт линкове
    link_ai = "https://undetectable.ai?_by=checkandcalc"
    link_pictory = "https://pictory.ai?ref=pavel-pavlov83"
    link_surfshark = "https://get.surfshark.net/aff_c?offer_id=1249&aff_id=45762&source=https://checkandcalc.com/"
    link_security_hardware = random.choice(["https://shop.ledger.com/?r=4afdb272c797", "https://affil.trezor.io/SH12N"])

    # Интелигентна Profit логика (заменя старата if/elif/else структура)
    if any(k in topic_lower for k in ['ai', 'detector', 'writing', 'human', 'bypass', 'chatgpt', 'claude']):
        cta_text, cta_sub, cta_btn, cta_url = "🛡️ STOP BEING FLAGGED BY AI", "Humanize your text and bypass any AI detector instantly with Undetectable AI.", "BYPASS AI DETECTION NOW", link_ai
        
    elif any(k in topic_lower for k in ['youtube', 'video', 'content', 'channel', 'faceless', 'views', 'monetize']):
        cta_text, cta_sub, cta_btn, cta_url = "🎬 CREATE AI VIDEOS IN MINUTES", "Turn your scripts into professional videos automatically. Use code PAVEL20 for 20% OFF!", "START CREATING WITH PICTORY", link_pictory
        
    elif any(k in topic_lower for k in ['vpn', 'hacker', 'privacy', 'wifi', 'tracking', 'security', 'online', 'safe', 'scam', 'protection', 'identity', 'phishing', 'fake']):
        cta_text, cta_sub, cta_btn, cta_url = "🦈 SECURE YOUR DIGITAL LIFE", "Protect your identity and browse privately with Surfshark One - the all-in-one security suite.", "GET 60% OFF SURFSHARK NOW", link_surfshark
        
    else:
        # Резервен вариант за крипто/хардуерна сигурност
        cta_text, cta_sub, cta_btn, cta_url = "🔐 PROTECT YOUR ASSETS", "Secure your digital wealth with the world's most trusted hardware wallets.", "GET YOUR WALLET NOW", link_security_hardware
        
    # Сглобяваме самия бутон
    cta_box = f"""
    <div class="premium-cta">
        <div class="cta-tag">RECOMMENDED BY CHECK & CALC</div>
        <div class="cta-title">{cta_text}</div>
        <p class="cta-desc">{cta_sub}</p>
        <a href="{cta_url}" target="_blank" class="cta-button">{cta_btn}</a>
    </div>
    """

    # Магията: Инжектираме бутона точно по средата на статията (С БРОНИРАНА ЗАЩИТА)
    paragraphs = html_content.split('</p>')
    if len(paragraphs) > 2:
        mid = len(paragraphs) // 2
        # Възстановяваме скрития </p> таг, за да не чупим дизайна
        html_with_cta = '</p>'.join(paragraphs[:mid]) + '</p>\n' + cta_box + '\n' + '</p>'.join(paragraphs[mid:])
    else:
        # Резервен план: Ако AI-то някога пак се обърка, пазим текста и бутона в безопасност
        html_with_cta = cta_box + '<br><br>' + html_content
 # --- ТУК СЛАГАШ ХИРУРГА (На ред 290) ---
    html_with_cta = inject_surgical_links(html_with_cta, filename)
# ВАКСИНА: Премахваме двойните кавички, за да не чупят HTML-а и JSON-LD
    safe_topic_title = topic_title.replace('"', "'")
    
    # Ако имаме снимка, създаваме HTML таг с БЕЗОПАСНОТО заглавие, ако не - празен текст
    img_tag = f'<img src="{image_name}" class="article-banner" alt="{safe_topic_title}">' if image_name else ""

    # 👇 НОВО: Определяме коя снимка да се показва в LinkedIn/Facebook/Telegram
    og_image_url = f"https://checkandcalc.com/{image_name}" if image_name else "https://checkandcalc.com/favicon.png"
    
   # --- ПЕРФЕКТНИЯТ ДИЗАЙН (ШАБЛОН) С УНИВЕРСАЛНА КУКА ---
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_topic_title}</title>
    <meta property="og:title" content="{safe_topic_title}" />
    <meta property="og:type" content="article" />
    <meta property="og:image" content="{og_image_url}" />
    <link rel="icon" type="image/png" href="https://checkandcalc.com/favicon.png" />
    <link rel="canonical" href="https://checkandcalc.com/{filename}" />
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "mainEntityOfPage": {{
        "@type": "WebPage",
        "@id": "https://checkandcalc.com/{filename}"
      }},
      "headline": "{safe_topic_title}",
      "datePublished": "{today_iso}",
      "dateModified": "{today_iso}",
      "author": {{
        "@type": "Organization",
        "name": "Check & Calc AI Security",
        "url": "https://checkandcalc.com/"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "Check & Calc",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://checkandcalc.com/favicon.ico"
        }}
      }}
    }}
    </script>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #020617; color: #e2e8f0; line-height: 1.7; padding: 20px; margin: 0; }}
        .article-container {{ max-width: 800px; margin: 0 auto; background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }}
        /* ДОБАВИ ТОВА ТУК 👇 */
        .article-banner {{ 
            width: 100%; 
            height: auto; 
            border-radius: 12px; 
            margin-bottom: 30px; 
            border: 1px solid #1f2937; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); 
        }}
        /* ------------------ */
        h1 {{ color: #93c5fd; font-size: 2.2rem; margin-top: 0; margin-bottom: 25px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; line-height: 1.3; }}
        h2 {{ color: #bfdbfe; font-size: 1.6rem; margin-top: 35px; border-bottom: 1px dashed #1f2937; padding-bottom: 8px; }}
        h3 {{ color: #e0e7ff; font-size: 1.3rem; margin-top: 25px; }}
        a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }}
        a:hover {{ border-bottom: 1px solid #60a5fa; }}
        p {{ margin-bottom: 20px; font-size: 1.05rem; color: #cbd5e1; }}
        ul, ol {{ margin-bottom: 25px; color: #cbd5e1; font-size: 1.05rem; }}
        li {{ margin-bottom: 10px; }}
        strong {{ color: #f8fafc; }}
        
        /* 🤖 AI & GEO Оптимизиран блок за ChatGPT/Gemini */
        .ai-answer-box {{ background: rgba(16, 185, 129, 0.05); border-left: 4px solid #10b981; padding: 20px 25px; margin-bottom: 35px; border-radius: 0 8px 8px 0; border-top: 1px solid #1f2937; border-right: 1px solid #1f2937; border-bottom: 1px solid #1f2937; }}
        .ai-answer-box h2 {{ color: #10b981; font-size: 1.2rem; margin-top: 0; border-bottom: none; padding-bottom: 0; text-transform: uppercase; letter-spacing: 1px; }}
        .ai-answer-box ul {{ margin-bottom: 0; }}
        .ai-answer-box li {{ color: #f8fafc; font-weight: 500; font-size: 1rem; }}
        
        /* 💸 МАШИНАТА ЗА ПРОДАЖБИ (Premium Affiliate Button) */
        .premium-cta {{ margin: 40px 0; padding: 30px; background: #1e293b; border-left: 5px solid #3b82f6; border-radius: 8px; text-align: center; border-right: 1px solid #334155; border-top: 1px solid #334155; border-bottom: 1px solid #334155; }}
        .cta-tag {{ font-size: 0.7rem; font-weight: 800; color: #60a5fa; letter-spacing: 2px; margin-bottom: 10px; }}
        .cta-title {{ font-size: 1.5rem; font-weight: 900; color: #f8fafc; margin-bottom: 10px; }}
        .cta-desc {{ font-size: 1rem; color: #94a3b8; margin-bottom: 25px; line-height: 1.4; }}
        .cta-button {{ display: inline-block; background: #2563eb; color: #ffffff !important; padding: 14px 28px; border-radius: 6px; font-weight: bold; text-decoration: none; transition: 0.3s; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3); }}
        .cta-button:hover {{ background: #1d4ed8; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4); }}
        
        /* Premium Telegram Box - Universal Hook */
        .premium-hook {{
            margin: 50px 0;
            padding: 30px;
            background: linear-gradient(145deg, #111827, #1e293b);
            border: 1px solid #3b82f6;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.1);
        }}
        .hook-title {{ color: #38bdf8; font-size: 1.4rem; font-weight: 800; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }}
        .hook-text {{ color: #94a3b8; font-size: 1rem; margin-bottom: 25px; }}
        .tg-btn-premium {{
            display: inline-block;
            background: #3b82f6;
            color: #ffffff !important;
            padding: 15px 35px;
            border-radius: 12px;
            font-weight: 900;
            font-size: 1.1rem;
            text-transform: uppercase;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }}
        .tg-btn-premium:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(59, 130, 246, 0.6); background: #2563eb; }}
        
        .back-btn {{ display: inline-block; margin-top: 40px; padding: 12px 24px; background-color: #1e293b; color: #93c5fd; border-radius: 8px; border: 1px solid #334155; font-weight: bold; transition: all 0.2s; }}
        .back-btn:hover {{ background-color: #334155; color: #ffffff; cursor: pointer; }}
    </style>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-LXJ2T5DJZH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-LXJ2T5DJZH');
    </script>
</head>
<body>
    <div class="article-container">
       {img_tag}  {html_with_cta}
        
        <div class="premium-hook">
            <div class="hook-title">🕵️ ACCESS THE INSIDER FEED</div>
            <p class="hook-text">
                Don't wait for the headlines. Our <strong>Private Telegram Channel</strong> delivers real-time AI security updates and digital wealth strategies before they go viral. Stay protected. Stay ahead.
            </p>
            <a href="https://t.me/checkandcalc_alerts" target="_blank" class="tg-btn-premium">⚡ JOIN THE 1% NOW</a>
        </div>
        
       <div style="margin-top: 50px; padding: 30px; background: #0f172a; border-radius: 16px; border: 1px solid #1f2937; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
            <h3 style="color: #cbd5e1; font-size: 1.25rem; margin-top: 0; margin-bottom: 12px;">🧰 Try Our Free Tools & Calculators</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 25px;">No sign-up required. Instantly check risks, analyze AI text, or calculate your digital finances.</p>
            
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px;">
                <a href="index.html#scam" style="background: #020617; color: #e5e7eb; border: 1px solid #1f2937; padding: 10px 18px; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;" onmouseover="this.style.background='#22c55e'; this.style.color='#020617'; this.style.borderColor='#16a34a';" onmouseout="this.style.background='#020617'; this.style.color='#e5e7eb'; this.style.borderColor='#1f2937';">🛡️ SafeSiteCheck</a>
                <a href="index.html#ai" style="background: #020617; color: #e5e7eb; border: 1px solid #1f2937; padding: 10px 18px; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;" onmouseover="this.style.background='#22c55e'; this.style.color='#020617'; this.style.borderColor='#16a34a';" onmouseout="this.style.background='#020617'; this.style.color='#e5e7eb'; this.style.borderColor='#1f2937';">🧠 HumanScore</a>
                <a href="index.html#yt" style="background: #020617; color: #e5e7eb; border: 1px solid #1f2937; padding: 10px 18px; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;" onmouseover="this.style.background='#22c55e'; this.style.color='#020617'; this.style.borderColor='#16a34a';" onmouseout="this.style.background='#020617'; this.style.color='#e5e7eb'; this.style.borderColor='#1f2937';">📺 TubeEarnings</a>
                <a href="index.html#subdrain" style="background: #020617; color: #e5e7eb; border: 1px solid #1f2937; padding: 10px 18px; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;" onmouseover="this.style.background='#22c55e'; this.style.color='#020617'; this.style.borderColor='#16a34a';" onmouseout="this.style.background='#020617'; this.style.color='#e5e7eb'; this.style.borderColor='#1f2937';">💳 SubDrain</a>
                <a href="index.html#breachcost" style="background: #020617; color: #e5e7eb; border: 1px solid #1f2937; padding: 10px 18px; border-radius: 999px; text-decoration: none; font-weight: 600; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s;" onmouseover="this.style.background='#22c55e'; this.style.color='#020617'; this.style.borderColor='#16a34a';" onmouseout="this.style.background='#020617'; this.style.color='#e5e7eb'; this.style.borderColor='#1f2937';">⚠️ BreachCost</a>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="index.html" class="back-btn">🚀 Back to Homepage</a>
        </div>
    </div>
</body>
</html>"""

    # Запазваме статията с новия луксозен дизайн
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)

   # --- СТЪПКА 3: "УМНИЯТ" АРХИВАТОР (HUB & SPOKE SEO) ---
    print("🏗️ Изграждане на SEO Hub & Spoke архитектура...")
    
    # 1. Вземаме всички статии и ги сортираме от най-новата към най-старата
    # (Игнорираме системните файлове и архивите)
    all_files = [f for f in glob.glob('*.html') if f not in ['index.html', 'about.html', 'disclosure.html', 'privacy.html', 'scam-checker.html', '404.html'] and not f.startswith('category-')]
    
    import subprocess
    def get_git_date(filepath):
        try:
            d = subprocess.check_output(['git', 'log', '--diff-filter=A', '--format=%cs', '-1', '--', filepath]).decode('utf-8').strip()
            return d if d else "9999-99-99" # Новите файлове получават бъдеща дата, за да са най-отгоре
        except:
            return "9999-99-99"

    all_files.sort(key=get_git_date, reverse=True)
    
    # 2. Ключови думи за разпределяне по категории
    ai_keywords = ['ai', 'detector', 'chatgpt', 'writing', 'human', 'deepfake', 'quillbot', 'claude', 'turnitin', 'gptzero', 'prompt']
    yt_keywords = ['youtube', 'earnings', 'money', 'views', 'rpm', 'adsense', 'cpm', 'tube', 'shorts', 'monetize', 'vlog', 'faceless']
    
    categories = {"ai": [], "youtube": [], "security": []}
    
    for file in all_files:
        pretty_title = file.replace('.html', '').replace('-', ' ').title()
        
        # --- ИСТИНСКА ДАТА (Четене от Git историята) ---
        import subprocess
        try:
            # Търсим кога файлът е добавен за първи път (Added) в Git
            git_date = subprocess.check_output(['git', 'log', '--diff-filter=A', '--format=%cs', '-1', '--', file]).decode('utf-8').strip()
            if git_date:
                import datetime
                # Преобразуваме формата (от 2026-06-02 към Jun 02, 2026)
                date_str = datetime.datetime.strptime(git_date, '%Y-%m-%d').strftime("%b %d, %Y")
            else:
                # Ако файлът е съвсем нов и още не е в Git, слагаме днешна дата
                date_str = datetime.date.today().strftime("%b %d, %Y")
        except Exception as e:
            # Спасителен вариант
            date_str = datetime.date.today().strftime("%b %d, %Y")
        # -----------------------------------------------
            
        link_html = f'<li style="margin-bottom: 15px;"><span style="color:#64748b; font-size:0.85em; margin-right: 15px;">{date_str}</span><a href="{file}" style="color:#60a5fa; font-weight:bold; text-decoration:none;">{pretty_title}</a></li>\n'
        
        file_lower = file.lower()
        if any(k in file_lower for k in ai_keywords):
            categories["ai"].append(link_html)
        elif any(k in file_lower for k in yt_keywords):
            categories["youtube"].append(link_html)
        else:
            categories["security"].append(link_html)

# 3. Обновяване на INDEX.HTML (С изолирана и бронирана логика)
    latest_15 = all_files[:15]
    latest_links_html = ""
    for file in latest_15:
        pretty_title = file.replace('.html', '').replace('-', ' ').title()
        latest_links_html += f'<li style="margin-bottom: 12px; font-size: 1.05rem;">🚀 <a href="{file}" style="color:#93c5fd; text-decoration:none; transition: color 0.2s;">{pretty_title}</a></li>\n'
    
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            index_content = f.read()
        
        # 1. ДЕФИНИРАНЕ НА ТВЪРДИ МАРКЕРИ (Със защита от чат парсъри)
        start_marker = "<" + "!-- ARTICLES_START --" + ">"
        end_marker = "<" + "!-- ARTICLES_END --" + ">"
        
        import re

        # 2. ПРЕДПАЗЕН ЩИТ: Ако маркерите ги няма, системата ги инжектира автоматично
        if start_marker not in index_content or end_marker not in index_content:
            print("⚠️ Маркерите липсват! Инжектирам ги интелигентно в секцията Latest Insights...")
            # Търси точно <ul> тага след заглавието
            pattern = r'(<h3[^>]*>🔥 Latest Insights</h3>\s*<ul[^>]*>)'
            replacement = f'\\1\n{start_marker}\n{end_marker}\n'
            index_content = re.sub(pattern, replacement, index_content, count=1)

        # 3. ХИРУРГИЧЕСКА ПОДМЯНА (100% успеваемост)
        if start_marker in index_content and end_marker in index_content:
            # Използваме Regex (re.DOTALL хваща и новите редове), за да подменим ВСИЧКО между двата маркера
            pattern_replace = f'({start_marker}).*?({end_marker})'
            new_content = f'\\1\n{latest_links_html}\\2'
            new_index = re.sub(pattern_replace, new_content, index_content, flags=re.DOTALL)
            
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_index)
            print("✅ Началната страница е обновена успешно (Бронирана архитектура).")
        else:
            print("❌ КРИТИЧНО: Не успяхме да намерим къде да поставим маркерите. SEO модулът е пропуснат, за да не се счупи сайта.")
            
    except Exception as e:
        print(f"⚠️ Системна грешка при обновяване на index.html: {e}")
            
    # 4. Автоматично генериране на СИЛОЗИ (Категорийни страници)
    for cat_name, cat_links in categories.items():
        cat_filename = f"category-{cat_name}.html"
        cat_title = cat_name.upper() + " ARCHIVE"
        
        archive_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cat_title} - Check & Calc</title>
    <link rel="canonical" href="https://checkandcalc.com/{cat_filename}" />
    <link rel="icon" type="image/png" href="https://checkandcalc.com/favicon.png" />
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #020617; color: #e2e8f0; line-height: 1.7; padding: 20px; margin: 0; }}
        .archive-container {{ max-width: 800px; margin: 0 auto; background: #0f172a; padding: 40px; border-radius: 16px; border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); }}
        a {{ color: #60a5fa; text-decoration: none; transition: color 0.2s; }}
        a:hover {{ color: #93c5fd; }}
        ul {{ list-style-type: none; padding: 0; margin-top: 30px; }}
        li {{ border-bottom: 1px dashed #1e293b; padding-bottom: 10px; }}
        h1 {{ color: #93c5fd; border-bottom: 1px solid #1f2937; padding-bottom: 15px; margin-top: 20px; }}
        .back-btn {{ display: inline-block; padding: 10px 20px; background-color: #1e293b; color: #93c5fd; border-radius: 8px; border: 1px solid #334155; font-weight: bold; transition: all 0.2s; }}
        .back-btn:hover {{ background-color: #334155; color: #ffffff; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="archive-container">
        <a href="index.html" class="back-btn">← Back to Homepage</a>
        <h1>📂 {cat_title} ({len(cat_links)} Articles)</h1>
        <ul>
            {"".join(cat_links)}
        </ul>
    </div>
</body>
</html>"""
        with open(cat_filename, "w", encoding="utf-8") as f:
            f.write(archive_html)
            
    print("🎯 Системата изгради интелигентните SEO архиви!")
    
                # --- ТУК СЛАГАШ ТОВА ---
    update_linkedin_database(
        article_title=topic_title,
        article_url=f"https://checkandcalc.com/{filename}",
        article_summary=linkedin_hook,
        image_file=image_name  # <--- Ето това е финалната връзка!
    )
    # -----------------------

    print(f"Готово! Нова статия: {topic_title}")

except Exception as e:
    print(f"Грешка: {e}")
