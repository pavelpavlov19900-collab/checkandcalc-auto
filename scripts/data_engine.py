import json
import os
import requests
import whois
from datetime import datetime

# Конфигурация
GOOGLE_API_KEY = "DUMMY_KEY_TEST" # Тук ще сложим реалния ключ по-късно
REPORTS_DIR = "data/reports"

# Създаваме папката за репортите, ако не съществува
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_domain_age_days(domain):
    """Извлича реалната възраст на домейна чрез WHOIS"""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        # WHOIS понякога връща списък от дати, взимаме първата
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            days_alive = (datetime.now() - creation_date).days
            return days_alive
        return None
    except Exception as e:
        print(f"Грешка при WHOIS за {domain}: {e}")
        return None

def check_safe_browsing(domain):
    """
    Симулация на Google Safe Browsing API.
    Когато сложим истинския ключ, тук ще правим POST заявка към Google.
    За теста приемаме, че сайтовете са чисти, освен ако нямат 'scam' в името.
    """
    if GOOGLE_API_KEY == "DUMMY_KEY_TEST":
        # Mock логика за локални тестове
        if "scam" in domain or "fake" in domain:
            return {"is_safe": False, "threat_type": "SOCIAL_ENGINEERING"}
        return {"is_safe": True, "threat_type": "NONE"}
    
    # Тук ще бъде реалната логика по-късно
    pass

def calculate_trust_score(days_alive, safe_browsing_data):
    """Математическият алгоритъм за Trust Score (0-100)"""
    score = 100
    risk_factors = []
    
    # 1. Проверка за черни списъци (Критичен фактор)
    if not safe_browsing_data["is_safe"]:
        score -= 80
        risk_factors.append(f"Засечена заплаха: {safe_browsing_data['threat_type']}")
        
    # 2. Оценка по възраст (Фундаментален индикатор за измами)
    if days_alive is None:
        score -= 40
        risk_factors.append("Скрита или невалидна WHOIS информация")
    elif days_alive < 30:
        score -= 50
        risk_factors.append(f"Много нов домейн (само на {days_alive} дни)")
    elif days_alive < 180:
        score -= 20
        risk_factors.append(f"Сравнително нов домейн ({days_alive} дни)")
    else:
        risk_factors.append(f"Домейн с история ({days_alive} дни)")
        
    # Нормализиране до 0-100
    score = max(0, min(100, score))
    return score, risk_factors

def generate_report(domain):
    """Оркестрира процеса и записва JSON"""
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
        
    print(f"✓ Репортът е запазен: {file_path} (Скор: {score}/100)")

# Списък за тестване (Един сигурен, един нов/съмнителен, един симулиран опасен)
domains_to_test = [
    "amazon.com",         # Сигурен, стар
    "checkandcalc.com",   # Твоят домейн (за референция)
    "fakescamshop.com"    # Симулация за опасен
]

if __name__ == "__main__":
    print("Стартиране на Data Engine...")
    for d in domains_to_test:
        generate_report(d)
