import re
import os, datetime, random
from google import genai
from google.genai import types  # НОВО: Нужно ни е за контрол на разходите!

# ИНИЦИАЛИЗАЦИЯ
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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

    # 2. ГЕНЕРИРАНЕ (С УЛТРА-ЕВТИН FLASH + FALLBACK ЗАЩИТА)
    prompt_text = f"Write a 1000 word SEO article in English about: {topic_title}. Return ONLY the raw HTML body content (headings, paragraphs, lists). Do NOT include <html>, <head>, <style>, or <body> tags."
    
    try:
        print("Опит 1: Генериране с бюджетния gemini-2.5-flash...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                max_output_tokens=2000, # ТАВАН НА РАЗХОДИТЕ: Спира модела след ~1500 думи
                temperature=0.7
            )
        )
    except Exception as e:
        print(f"Flash върна грешка ({e}). Включваме резервния план с Pro...")
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                max_output_tokens=2000
            )
        )
        
    if not response or not response.text:
        print("Критична грешка: Моделите не върнаха текст. Проверете темата за забранени думи.")
        exit()

    html_content = response.text.replace('```html', '').replace('```', '').strip()
    # 🚀 НОВО: Взимаме точната дата за SEO Schema Markup
    today_iso = datetime.date.today().isoformat()
    # --- МОДУЛ ЗА АВТОМАТИЧНА МОНЕТИЗАЦИЯ (CTA GENERATOR) ---
    topic_lower = topic_title.lower()
    
    # Твоите линкове (директно от "дигиталния ни склад")
    link_ai = "https://undetectable.ai?_by=checkandcalc"
    link_security = random.choice(["https://shop.ledger.com/?r=4afdb272c797", "https://affil.trezor.io/SH12N"])
    link_youtube = "https://try.elevenlabs.io/jtoxn4vv4klp"

    # Логика за избор на продукт според темата
    if any(k in topic_lower for k in ['ai', 'detector', 'writing', 'human', 'bypass']):
        cta_text, cta_sub, cta_btn, cta_url = "🛡️ STOP BEING FLAGGED BY AI", "Humanize your text and bypass any AI detector instantly with Undetectable AI.", "BYPASS AI DETECTION NOW", link_ai
    elif any(k in topic_lower for k in ['scam', 'crypto', 'safety', 'wallet', 'fake', 'phishing']):
        cta_text, cta_sub, cta_btn, cta_url = "🔐 PROTECT YOUR DIGITAL WEALTH", "Don't leave your crypto on exchanges. Secure your assets with the world's most trusted hardware wallets.", "GET YOUR HARDWARE WALLET", link_security
    else:
        cta_text, cta_sub, cta_btn, cta_url = "🎙️ START YOUR FACELESS CHANNEL", "Create professional AI voiceovers in seconds. The #1 tool for YouTube automation.", "GET ELEVENLABS FOR FREE", link_youtube

    # Сглобяваме самия бутон
    cta_box = f"""
    <div class="premium-cta">
        <div class="cta-tag">RECOMMENDED BY CHECK & CALC</div>
        <div class="cta-title">{cta_text}</div>
        <p class="cta-desc">{cta_sub}</p>
        <a href="{cta_url}" target="_blank" class="cta-button">{cta_btn}</a>
    </div>
    """

    # Магията: Инжектираме бутона точно по средата на статията
    paragraphs = html_content.split('</p>')
    mid = len(paragraphs) // 2
    html_with_cta = '</p>'.join(paragraphs[:mid]) + cta_box + '</p>'.join(paragraphs[mid:])

    # --- ОТТУК НАТАТЪК КОДЪТ ТИ ЗА ДИЗАЙНА ОСТАВА СЪЩИЯТ ---
    
   # --- ПЕРФЕКТНИЯТ ДИЗАЙН (ШАБЛОН) С УНИВЕРСАЛНА КУКА ---
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic_title}</title>
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
        h1 {{ color: #93c5fd; font-size: 2.2rem; margin-top: 0; margin-bottom: 25px; border-bottom: 1px solid #1f2937; padding-bottom: 15px; line-height: 1.3; }}
        h2 {{ color: #bfdbfe; font-size: 1.6rem; margin-top: 35px; border-bottom: 1px dashed #1f2937; padding-bottom: 8px; }}
        h3 {{ color: #e0e7ff; font-size: 1.3rem; margin-top: 25px; }}
        a {{ color: #60a5fa; text-decoration: none; border-bottom: 1px solid transparent; transition: border-color 0.2s; }}
        a:hover {{ border-bottom: 1px solid #60a5fa; }}
        p {{ margin-bottom: 20px; font-size: 1.05rem; color: #cbd5e1; }}
        ul, ol {{ margin-bottom: 25px; color: #cbd5e1; font-size: 1.05rem; }}
        li {{ margin-bottom: 10px; }}
        strong {{ color: #f8fafc; }}
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
        {html_with_cta}
        
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

    print(f"Готово! Нова статия: {topic_title}")

except Exception as e:
    print(f"Грешка: {e}")
