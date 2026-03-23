import os, datetime
import google.generativeai as genai

# Свързване с трезора
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

# Нашата БРУТАЛНА SEO команда
prompt = """Act as a Top-Tier SEO Expert. Write a comprehensive, 1500+ word guide on: '10 Red Flags of a Scam Website in 2026'. 
Target audience: People afraid of being scammed online. Tone: Authoritative, helpful, simple.
Requirements for maximum SEO:
1. Format as strict HTML5 (no markdown, no ```html tags, just raw code).
2. Start with an engaging <h1> and a 'Key Takeaways' <ul> section.
3. Use <h2> and <h3> tags logically with rich LSI keywords (fraud prevention, secure checkout, phishing links).
4. Include an FAQ section at the bottom.
5. CRITICAL: Include valid JSON-LD FAQ Schema Markup in a <script> tag at the end of the HTML for Google Rich Snippets.
Return ONLY the raw HTML code."""

try:
    response = model.generate_content(prompt)
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    filename = f"scam-red-flags-{datetime.date.today()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"SEO Статията е готова: {filename}")
except Exception as e:
    print(f"Грешка: {e}")
