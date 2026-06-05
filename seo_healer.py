import os
import re

def heal_seo_data():
    print("🤖 Стартиране на SEO Auto-Healer протокол...")
    print("🔍 Сканиране на фабриката за счупени JSON-LD структури...\n")
    
    files_fixed = 0
    files_scanned = 0
    
    # Регулярен израз (Regex), който действа като лазерен скалпел.
    # Той намира редове като: "headline": "Някакъв "Текст" тук",
    # Разделя ги на 3 части: Префикс | Съдържание | Суфикс
    pattern = re.compile(r'^(\s*"(?:headline|description)"\s*:\s*")(.*)("[,]?[ \t]*\n?)$')

    # Сканираме всички файлове в текущата папка
    for filename in os.listdir('.'):
        if not filename.endswith('.html'):
            continue
            
        files_scanned += 1
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_json_block = False
        file_changed = False
        new_lines = []

        for line in lines:
            # Откриваме влизане в SEO зоната
            if '<script type="application/ld+json">' in line:
                in_json_block = True
                new_lines.append(line)
                continue
            
            # Откриваме излизане от SEO зоната
            if in_json_block and '</script>' in line:
                in_json_block = False
                new_lines.append(line)
                continue

            # Ако сме вътре в SEO зоната, търсим заглавия и описания
            if in_json_block:
                match = pattern.match(line)
                if match:
                    prefix = match.group(1)   # напр. ->   "headline": "
                    content = match.group(2)  # напр. -> The "Subscription Maze": Guide
                    suffix = match.group(3)   # напр. -> ",
                    
                    # Ако в съдържанието има вътрешни двойни кавички, ги лекуваме
                    if '"' in content:
                        safe_content = content.replace('"', "'")
                        fixed_line = f"{prefix}{safe_content}{suffix}"
                        new_lines.append(fixed_line)
                        file_changed = True
                        continue
            
            # Ако редът е здрав или сме извън JSON блока, го запазваме какъвто е
            new_lines.append(line)

        # Ако сме направили хирургическа намеса, презаписваме файла
        if file_changed:
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✅ Излекуван файл: {filename}")
            files_fixed += 1

    print(f"\n🎯 Операцията приключи.")
    print(f"📂 Сканирани файлове: {files_scanned}")
    print(f"🔧 Поправени файлове: {files_fixed}")

if __name__ == "__main__":
    heal_seo_data()
