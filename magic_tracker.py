import os

# Това е точният ти код за Analytics, заедно със затварящия таг, който ще заместим
ga_code = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-LXJ2T5DJZH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-LXJ2T5DJZH');
    </script>
</head>"""

def apply_magic():
    updated = 0
    # Намираме всички HTML файлове в папката
    for filename in os.listdir('.'):
        if filename.endswith('.html'):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Предпазен клапан: Пропускаме файла, ако вече сме му сложили тракер
            if 'G-LXJ2T5DJZH' in content:
                continue

            # Ако няма тракер, намираме </head> и го заместваме с нашия код + </head>
            if '</head>' in content:
                new_content = content.replace('</head>', ga_code)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Тракерът е инжектиран в: {filename}")
                updated += 1
                
    print(f"\n🚀 Операцията приключи! Успешно ъпгрейднати {updated} стари активи.")

if __name__ == "__main__":
    apply_magic()
