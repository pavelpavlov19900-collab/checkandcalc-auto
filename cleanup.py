import os
import re
import glob

def clean_topics():
    # 1. Вземаме списък с всички съществуващи статии
    existing_files = glob.glob('*.html')
    
    # 2. Четем всички теми от списъка
    with open('topics.txt', 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]

    remaining_topics = []
    removed_count = 0

    for t in topics:
        # ТОВА Е КРИТИЧНО: Логиката трябва да е 1:1 с тази в generate.py
        temp_slug = t.lower().replace(' ', '-')
        temp_slug = re.sub(r'[^a-z0-9-]', '', temp_slug)
        temp_slug = re.sub(r'-+', '-', temp_slug).strip('-') + ".html"
        
        # Проверяваме: Има ли файл с такова име?
        if temp_slug not in existing_files:
            # Файлът не съществува -> Темата не е написана -> Запазваме я
            remaining_topics.append(t)
        else:
            # Файлът съществува -> Темата вече е написана -> Махаме я от списъка
            removed_count += 1

    # 3. Записваме само "неизползваните" теми
    with open('topics.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(remaining_topics))
    
    print(f"✅ Почистването завърши! Премахнати са {removed_count} теми, за които вече имаш файлове.")
    print(f"Брой теми оставащи за писане: {len(remaining_topics)}")

if __name__ == "__main__":
    clean_topics()
