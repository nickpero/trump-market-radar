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
    "ENERGY": {"keywords": ["oil", "crude", "opec", "energy", "gasoline", "lng", "natural gas"], "assets": ["USO", "XLE", "GLD"]},
    "FED_RATES": {"keywords": ["fed", "federal reserve", "interest rate", "interest rates", "rates", "powell"], "assets": ["QQQ", "SPY", "TLT", "GLD"]},
    "CHINA": {"keywords": ["china", "chinese", "beijing"], "assets": ["QQQ", "SPY", "GLD", "EUR/USD"]},
    "GEOPOLITICS": {"keywords": ["iran", "israel", "ukraine", "russia", "war", "ceasefire", "nato", "military", "missile", "troops"], "assets": ["SPY", "GLD", "USO", "TLT"]},
    "CRYPTO": {"keywords": ["bitcoin", "crypto", "cryptocurrency", "btc", "ethereum"], "assets": ["BTC"]},
}

NON_MARKET_PATTERNS = [
    "complete and total endorsement",
    "endorsement to be the next",
    "endorsement for re-election",
    "will never let you down",
]

MARKET_ACTION_TERMS = [
    "tariff", "tariffs", "duty", "duties", "sanction", "sanctions", "ban",
    "deal", "agreement", "ceasefire", "peace", "attack", "strike", "troops",
    "oil", "crude", "opec", "gasoline", "lng", "natural gas",
    "fed", "federal reserve", "interest rate", "interest rates", "powell",
    "rates", "china", "beijing", "bitcoin", "crypto", "ethereum",
    "military", "missile",
]

def classify(text: str) -> Classification:
    low = text.lower()

    if any(pattern in low for pattern in NON_MARKET_PATTERNS):
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "Non-market political endorsement")

    # Generic references to geopolitical places are not enough by themselves.
    matches = []
    for category, rule in RULES.items():
        hits = [kw for kw in rule["keywords"] if kw in low]
        if hits:
            matches.append((category, hits, rule["assets"]))

    if not matches:
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No market keyword detected")

    # Require explicit market-impact/action language. This suppresses posts that
    # merely mention countries or political themes in passing.
    if not any(term in low for term in MARKET_ACTION_TERMS):
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No actionable market-impact language detected")

    category, hits, assets = max(matches, key=lambda x: len(x[1]))

    neg = any(x in low for x in ["tariff", "tariffs", "war", "attack", "sanction", "sanctions", "ban", "strike"])
    pos = any(x in low for x in ["deal", "agreement", "ceasefire", "peace", "cut", "lower", "reduction"])

    direction = "NEGATIVE" if neg and not pos else "POSITIVE" if pos and not neg else "MIXED"
    priority = "HIGH" if len(hits) >= 2 or any(x in low for x in ["war", "tariff", "tariffs", "ceasefire", "fed", "interest rate"]) else "MEDIUM"

    return Classification(True, category, direction, priority, assets, "Matched: " + ", ".join(hits))
