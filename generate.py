import os, datetime
from google import genai

# Свързване чрез новия официален SDK
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

prompt = """Act as a Top-Tier SEO Expert. Write a comprehensive, 1000+ word guide on: 'How to check if a website is legit in 2026'. 
Requirements:
1. Format as strict HTML5 (no markdown, just raw code).
2. Start with <h1> and a 'Key Takeaways' <ul>.
3. Use <h2> for subheadings.
4. Include valid JSON-LD FAQ Schema Markup at the end.
Return ONLY the raw HTML code."""

try:
    # Използваме новата структура за извикване на AI
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=prompt
    )
    
    html_content = response.text.replace('```html', '').replace('```', '').strip()
    
    filename = f"legit-website-check-{datetime.date.today()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Готово: {filename}")
except Exception as e:
    print(f"Грешка: {e}")
