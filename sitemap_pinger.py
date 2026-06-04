import requests
import datetime

# Конфигурация
SITEMAP_URL = "https://checkandcalc.com/sitemap.xml"

# Официални Endpoint-и за Ping
SEARCH_ENGINES = {
    "Google": f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
    "Bing": f"https://www.bing.com/ping?sitemap={SITEMAP_URL}"
}

def ping_search_engines():
    print(f"🌍 Стартиране на SEO Ping протокол ({datetime.date.today()})...")
    
    for engine, url in SEARCH_ENGINES.items():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ {engine} успешно получи новия Sitemap!")
            else:
                print(f"⚠️ {engine} върна статус: {response.status_code}")
        except Exception as e:
            print(f"❌ Грешка при свързване с {engine}: {e}")

if __name__ == "__main__":
    ping_search_engines()
