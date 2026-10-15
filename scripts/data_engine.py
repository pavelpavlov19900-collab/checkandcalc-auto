import json
import os
import requests
from datetime import datetime

# Извличаме ключа от тайните на GitHub
GOOGLE_API_KEY = os.environ.get("GOOGLE_SAFE_BROWSING_KEY", "")
REPORTS_DIR = "data/reports"

os.makedirs(REPORTS_DIR, exist_ok=True)

def get_domain_age_days(domain):
    """Извлича възрастта на домейна чрез модерния RDAP HTTP протокол"""
    try:
        url = f"https://rdap.org/domain/{domain}"
        headers = {"User-Agent": "CheckAndCalc-Security-Engine/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for event in data.get("events", []):
                if event.get("eventAction") == "registration":
                    date_str = event.get("eventDate")
                    creation_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    days_alive = (datetime.now() - creation_date).days
                    return days_alive
    except Exception as e:
        print(f"Грешка при RDAP за {domain}: {e}")
        
    return None

def check_safe_browsing(domain):
    """Реална проверка през Google Safe Browsing API"""
    if not GOOGLE_API_KEY:
        print("ВНИМАНИЕ: Липсва Google API ключ. Скриптът не намира тайната в GitHub.")
        return {"is_safe": True, "threat_type": "NONE"}

    url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_API_KEY}"
    
    payload = {
        "client": {
            "clientId": "checkandcalc-engine",
            "clientVersion": "1.0.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": domain}]
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "matches" in data and len(data["matches"]) > 0:
                threat = data["matches"][0]["threatType"]
                return {"is_safe": False, "threat_type": threat}
        else:
            print(f"Грешка от Google API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Мрежова грешка при връзка с Google: {e}")

    return {"is_safe": True, "threat_type": "NONE"}

def calculate_trust_score(days_alive, safe_browsing_data):
    """Изчислява крайния рейтинг на базата на събраните данни"""
    score = 100
    risk_factors = []
    
    if not safe_browsing_data["is_safe"]:
        score -= 80
        risk_factors.append(f"Засечена заплаха от Google: {safe_browsing_data['threat_type']}")
        
    if days_alive is None:
        score -= 40
        risk_factors.append("Скрита или невалидна RDAP информация")
    elif days_alive < 30:
        score -= 50
        risk_factors.append(f"Много нов домейн (само на {days_alive} дни)")
    elif days_alive < 180:
        score -= 20
        risk_factors.append(f"Сравнително нов домейн ({days_alive} дни)")
    else:
        risk_factors.append(f"Домейн с история ({days_alive} дни)")
        
    score = max(0, min(100, score))
    return score, risk_factors

def generate_report(domain):
    print(f"\nАнализиране на: {domain}...")
    
    days_alive = get_domain_age_days(domain)
    safe_data = check_safe_browsing(domain)
    score, risk_factors = calculate_trust_score(days_alive, safe_data)
    
    report = {
        "domain": domain,
        "trust_score": score,
        "analyzed_at": datetime.now().isoformat(),
        "metrics": {
            "days_alive": days_alive,
            "google_safe": safe_data["is_safe"]
        },
        "risk_factors": risk_factors
    }
    
    file_path = os.path.join(REPORTS_DIR, f"{domain.replace('.', '_')}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
        
    print(f"✓ Репорт: {file_path} (Скор: {score}/100)")

domains_to_test = [
    "amazon.com",
    "checkandcalc.com",
    "testsafebrowsing.appspot.com" # Официален тестов домейн на Google
]

if __name__ == "__main__":
    print("Стартиране на Data Engine (Real API Mode)...")
    for d in domains_to_test:
        generate_report(d)
