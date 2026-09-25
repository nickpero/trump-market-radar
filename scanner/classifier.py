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
    "FED_RATES": {"keywords": ["federal reserve", "fed chair", "fed chief", "interest rate", "interest rates", "interest-rate", "rate cut", "rate hike", "rate cuts", "rate hikes", "monetary policy", "fomc", "federal funds rate", "powell"], "assets": ["QQQ", "SPY", "TLT", "GLD"]},
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

TARIFF_ACTION_PATTERNS = [
    "impose tariff", "impose tariffs", "imposing tariff", "imposing tariffs",
    "raise tariff", "raise tariffs", "raising tariff", "raising tariffs",
    "increase tariff", "increase tariffs", "increasing tariff", "increasing tariffs",
    "new tariff", "new tariffs", "additional tariff", "additional tariffs",
    "higher tariff", "higher tariffs", "tariff will", "tariffs will",
    "tariff on", "tariffs on", "duty on", "duties on",
    "remove tariff", "remove tariffs", "lower tariff", "lower tariffs",
    "cut tariff", "cut tariffs", "reduce tariff", "reduce tariffs",
    "tariff exemption", "tariff exemptions", "tariff deadline", "tariff deal",
    "tariff agreement", "reciprocal tariff", "reciprocal tariffs",
]

CHINA_ACTION_PATTERNS = [
    "tariff", "tariffs", "duty", "duties", "trade deal", "trade agreement",
    "trade war", "sanction", "sanctions", "export control", "export controls",
    "import restriction", "import restrictions", "export restriction", "export restrictions",
    "chip restriction", "chip restrictions", "semiconductor", "semiconductors",
    "artificial intelligence", "ai chip", "ai chips", "technology ban",
    "investment restriction", "investment restrictions", "yuan", "renminbi",
    "currency", "taiwan", "taiwan strait", "military exercise", "military exercises",
    "blockade", "embargo", "decouple", "decoupling", "supply chain",
    "rare earth", "rare earths", "negotiation", "negotiations", "agreement",
    "deal", "ban", "restrict", "restriction", "restrictions",
]

MARKET_ACTION_TERMS = [
    "tariff", "tariffs", "duty", "duties", "sanction", "sanctions", "ban",
    "deal", "agreement", "ceasefire", "peace", "attack", "strike", "troops",
    "oil", "crude", "opec", "gasoline", "lng", "natural gas",
    "federal reserve", "fed chair", "fed chief", "interest rate", "interest rates",
    "rate cut", "rate hike", "rate cuts", "rate hikes", "monetary policy",
    "fomc", "federal funds rate", "powell",
    "rates", "china", "beijing", "bitcoin", "crypto", "ethereum",
    "military", "missile",
]

def classify(text: str) -> Classification:
    low = text.lower()

    if any(pattern in low for pattern in NON_MARKET_PATTERNS):
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "Non-market political endorsement")

    matches = []
    for category, rule in RULES.items():
        hits = [kw for kw in rule["keywords"] if kw in low]
        if hits:
            matches.append((category, hits, rule["assets"]))

    if not matches:
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No market keyword detected")

    # FED_RATES requires explicit monetary-policy context.
    # A standalone "fed" is deliberately NOT a trigger: it often appears
    # inside unrelated words such as "federal" or in media/source text.
    if "FED_RATES" in [m[0] for m in matches]:
        fed_context = any(term in low for term in [
            "federal reserve", "fed chair", "fed chief", "interest rate",
            "interest rates", "interest-rate", "rate cut", "rate hike",
            "rate cuts", "rate hikes", "monetary policy", "fomc",
            "federal funds rate", "powell"
        ])
        if not fed_context:
            matches = [m for m in matches if m[0] != "FED_RATES"]
            if not matches:
                return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No actionable market-impact language detected")

    # CHINA requires concrete economic, trade, technology, currency or security action.
    # A visit, ceremony, dinner, tour or generic mention of China is not enough.
    if "CHINA" in [m[0] for m in matches] and not any(p in low for p in CHINA_ACTION_PATTERNS):
        matches = [m for m in matches if m[0] != "CHINA"]

    if not matches:
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No actionable market-impact language detected")

    # A mention of tariffs is not enough; require concrete tariff action/change.
    if "TARIFFS" in [m[0] for m in matches] and not any(p in low for p in TARIFF_ACTION_PATTERNS):
        matches = [m for m in matches if m[0] != "TARIFFS"]

    if not matches:
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No actionable market-impact language detected")

    if not any(term in low for term in MARKET_ACTION_TERMS) and not any(p in low for p in TARIFF_ACTION_PATTERNS):
        return Classification(False, "OTHER", "UNKNOWN", "LOW", [], "No actionable market-impact language detected")

    category, hits, assets = max(matches, key=lambda x: len(x[1]))

    neg = any(x in low for x in ["tariff", "tariffs", "war", "attack", "sanction", "sanctions", "ban", "strike"])
    pos = any(x in low for x in ["deal", "agreement", "ceasefire", "peace", "cut", "lower", "reduction"])

    direction = "NEGATIVE" if neg and not pos else "POSITIVE" if pos and not neg else "MIXED"
    priority = "HIGH" if len(hits) >= 2 or any(x in low for x in ["war", "tariff", "tariffs", "ceasefire", "federal reserve", "interest rate", "rate cut", "rate hike", "fomc", "powell"]) else "MEDIUM"

    return Classification(True, category, direction, priority, assets, "Matched: " + ", ".join(hits))
