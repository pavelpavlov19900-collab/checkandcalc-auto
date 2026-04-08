import re
import os, datetime, random, json, requests # Добавка
from google import genai
from google.genai import types  # НОВО: Нужно ни е за контрол на разходите!

# ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
G_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT") # Трябва да го добавиш в GitHub Secrets

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

# --- НОВА ФУНКЦИЯ ЗА ГЕНЕРИРАНЕ НА СНИМКА (С ГРЕШКОУСТОЙЧИВОСТ) ---
def generate_ai_image(client, prompt, project_id, filename):
    print(f"🎨 Опит за генериране на визия...")
    image_prompt = f"Professional futuristic digital art, cyberpunk style, high contrast, representing: {prompt}"
    
    try:
        # АВТОМАТИЧНО РАЗУЗНАВАНЕ:
        method_name = None
        for name in ['generate_images', 'generate_image']:
            if hasattr(client.models, name):
                method_name = name
                break
        
        if not method_name:
            print("⚠️ SDK грешка: Не намерих метод за снимки.")
            return None

        method = getattr(client.models, method_name)

        # 🚀 ПОПРАВКАТА: Преминаваме към най-новото поколение - Imagen 4!
        response = method(
            model='imagen-4.0-generate-001', # <--- ТУК Е МАГИЯТА
            prompt=image_prompt,
            config={
                'number_of_images': 1,
                'aspect_ratio': '16:9'
            }
        )

        image_name = filename.replace('.html', '.png')
        
        # Интелигентно извличане
        if hasattr(response, 'generated_images') and response.generated_images:
            image_obj = response.generated_images[0].image
        elif hasattr(response, 'images') and response.images:
            image_obj = response.images[0]
        elif isinstance(response, list) and len(response) > 0:
            image_obj = response[0]
        else:
            image_obj = response
            
        image_obj.save(image_name)
        print(f"✅ Снимката е готова: {image_name}")
        return image_name

    except Exception as e:
        print(f"⚠️ Снимката не успя: {e}")
        return None
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
    prompt_text = (
        f"Write a massive, highly detailed SEO article in English about: {topic_title}. "
        f"CRITICAL RULES: 1. Use a unique writing style adapted to the topic. NEVER start two articles with the same phrasing. "
        f"2. START with the main title in <h1> tags. "
        f"3. IMMEDIATELY AFTER the <h1>, generate a <div class='ai-answer-box'><h2>Quick Answer (TL;DR)</h2><ul>...</ul></div> with 3-5 ultra-concise, highly factual bullet points summarizing the core answer using <strong> tags for key tools/entities. "
        f"4. Follow with an engaging Introduction, EXACTLY 5 to 7 main sections using <h2> tags, and a Conclusion. "
        f"5. You MUST write AT LEAST 400 WORDS under EACH <h2> section. "
        f"6. FORMAT STRICTLY IN HTML with <p>, <ul>, <li>, <strong> tags. "
        f"7. ABSOLUTELY NO MARKDOWN. "
        f"8. Include a dedicated <h2> section about tools or solutions. "
        f"9. MANDATORY: You must finish the article with a formal Conclusion and ensure all HTML tags are perfectly closed. Do not stop mid-sentence. "
        f"Return ONLY the raw HTML body content starting with <h1>."
        f"IMPORTANT: After the final HTML tag, add exactly this separator '---LINKEDIN-HOOK---' "
        f"followed by a one-sentence provocative summary for a LinkedIn post." # <--- ТОВА Е НОВОТО
    )
    # --- СТАРТ НА ПОПРАВКАТА ---
    import time
    response = None

    for attempt in range(2):
        try:
            if attempt == 0:
                print("Опит 1: Генериране с бюджетния gemini-2.5-flash...")
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_text,
                    config=types.GenerateContentConfig(max_output_tokens=6000, temperature=0.7)
                )
            else:
                print("Опит 2 (Последен): Резервен план с Pro...")
                response = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=prompt_text,
                    config=types.GenerateContentConfig(max_output_tokens=6000)
                )
            
            # Ако горният код зареди текст, излизаме от цикъла (break)
            if response and response.text:
                break

        except Exception as e:
            if attempt == 0:
                print(f"Първият опит не успя ({e}). Изчакване 40 сек преди резервния план...")
                time.sleep(40)
            else:
                print(f"Критична грешка и при втория опит: {e}")

    if not response or not response.text:
        print("Критична грешка: Моделите са претоварени. Опитайте пак по-късно.")
        exit()
    # --- КРАЙ НА ПОПРАВКАТА ---

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
    
    # 3. 🛡️ ПРЕДПАЗИТЕЛ ЗА ЗАВЪРШЕНОСТ (Важно: Подравнен вляво, за да важи за всичко!)
    if not (html_content.endswith('</p>') or html_content.endswith('</ul>') or html_content.endswith('</li>')):
        html_content += "... and implement these strategies to ensure long-term success.</p><h2>Conclusion</h2><p>In summary, staying ahead of these trends is the key to business longevity and security. By following this guide, you maximize your growth and ensure a stable digital future.</p>"

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

  # Ако имаме снимка, създаваме HTML таг, ако не - празен текст
    img_tag = f'<img src="{image_name}" class="article-banner" alt="{topic_title}">' if image_name else ""
    
   # --- ПЕРФЕКТНИЯТ ДИЗАЙН (ШАБЛОН) С УНИВЕРСАЛНА КУКА ---
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_title}</title>
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
      "headline": "{topic_title}",
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
        
        <div style="text-align: center;">
            <a href="index.html" class="back-btn">🚀 Back to Homepage</a>
        </div>
    </div>
</body>
</html>"""

    # Запазваме статията с новия луксозен дизайн
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_template)

   # --- СТЪПКА 3: ИНТЕЛЕКТУАЛНО СОРТИРАНЕ ПО КАТЕГОРИИ ---
    target_file = "index.html"
    
    # Използваме този формат, за да виждаш буквите в чата:
    s_start = "<" + "!-- SCAM_LIST_START --" + ">"
    s_end   = "<" + "!-- SCAM_LIST_END --" + ">"
    
    a_start = "<" + "!-- AI_LIST_START --" + ">"
    a_end   = "<" + "!-- AI_LIST_END --" + ">"
    
    y_start = "<" + "!-- YT_LIST_START --" + ">"
    y_end   = "<" + "!-- YT_LIST_END --" + ">"
    
    # 1. Сканираме всички генерирани статии
    all_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', 'about.html', 'disclosure.html', 'privacy.html']]
    all_files.sort(key=os.path.getmtime, reverse=True)

    # Кошове за линковете
    scam_links, ai_links, yt_links = "", "", ""
    
   # Ключови думи за разпознаване
    ai_keywords = ['ai', 'detector', 'chatgpt', 'writing', 'human', 'deepfake', 'quillbot', 'claude', 'turnitin', 'gptzero']
    yt_keywords = ['youtube', 'earnings', 'money', 'views', 'rpm', 'adsense', 'cpm', 'tube', 'shorts', 'monetize']

    for file in all_files:
        pretty_title = file.replace('.html', '').replace('-', ' ').title()
        link_tag = f'          <li>🚀 <a href="{file}" style="color:#93c5fd;text-decoration:none;">{pretty_title}</a></li>\n'
        
        file_lower = file.lower()
        if any(k in file_lower for k in yt_keywords):
            yt_links += link_tag
        elif any(k in file_lower for k in ai_keywords):
            ai_links += link_tag
        else:
            scam_links += link_tag

    # 2. Четем index.html
    with open(target_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. Функция за замяна
    def update_block(content, start, end, links):
        if start in content and end in content:
            parts = content.split(start)
            rest = parts[1].split(end)
            return parts[0] + start + "\n" + links + "          " + end + rest[1]
        return content

    # Обновяваме трите секции
    html_content = update_block(html_content, s_start, s_end, scam_links)
    html_content = update_block(html_content, a_start, a_end, ai_links)
    html_content = update_block(html_content, y_start, y_end, yt_links)

    # 4. Запазваме финалния резултат
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("🎯 Системата подреди всички статии по категории!")

    # 4. ОБНОВЯВАНЕ НА SITEMAP.XML
    sitemap_file = 'sitemap.xml'
    today = datetime.date.today().isoformat()
    new_url = f"""  <url>
    <loc>https://checkandcalc.com/{filename}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.80</priority>
  </url>\n</urlset>"""

    if os.path.exists(sitemap_file):
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            s_content = f.read()
        if filename not in s_content:
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                f.write(s_content.replace("</urlset>", new_url))

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
