import os

favicon_tag = '<link rel="icon" type="image/png" href="https://checkandcalc.com/favicon.png" />'

# Минаваме през всички файлове
for filename in os.listdir('.'):
    if filename.endswith('.html') and filename != 'index.html':
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ако иконата я няма, я добавяме веднага след <head>
        if 'favicon.png' not in content:
            new_content = content.replace('<head>', f'<head>\n    {favicon_tag}')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Обновена статия: {filename}")

print("🚀 Всички стари активи вече имат брандинг!")
