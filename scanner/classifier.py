from dataclasses import dataclass

@dataclass
class Classification:
    relevant: bool
    category: str
    direction: str
    priority: str
    assets: list[str]
    reason: str

RULES = {
    "TARIFFS": {"keywords": ["tariff", "tariffs", "duty", "duties", "trade war", "import tax"], "assets": ["SPY", "QQQ", "EUR/USD", "GLD"]},
    "ENERGY": {"keywords": ["oil", "crude", "opec", "energy", "gasoline"], "assets": ["USO", "XLE", "GLD"]},
    "FED_RATES": {"keywords": ["fed", "federal reserve", "interest rate", "rates", "powell"], "assets": ["QQQ", "SPY", "TLT", "GLD"]},
    "CHINA": {"keywords": ["china", "chinese", "beijing"], "assets": ["QQQ", "SPY", "GLD", "EUR/USD"]},
    "GEOPOLITICS": {"keywords": ["iran", "israel", "ukraine", "russia", "war", "ceasefire", "nato"], "assets": ["SPY", "GLD", "USO", "TLT"]},
    "CRYPTO": {"keywords": ["bitcoin", "crypto", "cryptocurrency", "btc", "ethereum"], "assets": ["BTC"]},
}

def classify(text: str) -> Classification:
    low = text.lower()
    matches = []
    for category, rule in RULES.items():
        hits = [kw for kw in rule["keywords"] if kw in low]
        if hits: matches.append((category, hits, rule["assets"]))
    if not matches: return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No market keyword detected")
    category, hits, assets = max(matches, key=lambda x: len(x[1]))
    neg = any(x in low for x in ["tariff", "war", "attack", "sanction", "ban"])
    pos = any(x in low for x in ["deal", "agreement", "ceasefire", "peace", "cut", "lower"])
    direction = "NEGATIVE" if neg and not pos else "POSITIVE" if pos and not neg else "MIXED"
    priority = "HIGH" if len(hits) >= 2 or any(x in low for x in ["war", "tariff", "ceasefire", "fed"]) else "MEDIUM"
    return Classification(True, category, direction, priority, assets, "Matched: " + ", ".join(hits))
