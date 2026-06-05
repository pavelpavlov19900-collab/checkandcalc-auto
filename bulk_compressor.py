import os
from PIL import Image

def bulk_compress_images(size_limit_mb=1.0):
    print(f"🔍 Стартиране на Скенера за тежки снимки (над {size_limit_mb} MB)...")
    size_limit_bytes = size_limit_mb * 1024 * 1024
    
    compressed_count = 0
    total_saved_bytes = 0
    
    # Обхождаме всички файлове в папката
    for filename in os.listdir('.'):
        # Търсим само изображения
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            file_size = os.path.getsize(filename)
            
            # Ако файлът е по-тежък от лимита (1 MB)
            if file_size > size_limit_bytes:
                print(f"\n⚠️ Открит тежък файл: {filename} ({file_size / (1024*1024):.2f} MB)")
                
                try:
                    with Image.open(filename) as img:
                        # Конвертираме в RGB, ако е необходимо (за съвместимост)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            
                        # Мачкаме до нашия SEO стандарт 1200x675
                        img = img.resize((1200, 675), Image.Resampling.LANCZOS)
                        
                        # Презаписваме файла (като PNG, за да запазим перфектно качество при малък размер)
                        img.save(filename, format="PNG", optimize=True)
                        
                    new_size = os.path.getsize(filename)
                    saved = file_size - new_size
                    total_saved_bytes += saved
                    compressed_count += 1
                    
                    print(f"   ✅ Компресиран до: {new_size / (1024*1024):.2f} MB (Спестени: {saved / (1024*1024):.2f} MB)")
                except Exception as e:
                    print(f"   ❌ Грешка при обработка на {filename}: {e}")
                    
    print("\n🎯 Операцията приключи.")
    print(f"🖼️ Обработени снимки: {compressed_count}")
    print(f"💾 Общо спестено дисково пространство за сайта: {total_saved_bytes / (1024*1024):.2f} MB")

if __name__ == "__main__":
    # Стартираме скенера за всички файлове над 1 MB
    bulk_compress_images(1.0)
