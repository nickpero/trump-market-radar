import os
import time
import requests
from .classifier import Classification
from .trump_source import TrumpPost

ASSET_NAMES = {
    "SPY": "SPDR S&P 500 ETF Trust",
    "QQQ": "Invesco QQQ Trust (Nasdaq-100)",
    "DIA": "SPDR Dow Jones Industrial Average ETF Trust",
    "IWM": "iShares Russell 2000 ETF",
    "GLD": "SPDR Gold Shares",
    "USO": "United States Oil Fund",
    "XLE": "Energy Select Sector SPDR Fund",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "EUR/USD": "Euro / U.S. Dollar",
    "USD/JPY": "U.S. Dollar / Japanese Yen",
    "BTC": "Bitcoin",
}

def format_alert(post: TrumpPost, result: Classification) -> str:
    instrument_lines = []
    for symbol in result.assets:
        name = ASSET_NAMES.get(symbol, symbol)
        instrument_lines.append(
            f"• {symbol} — {name}\n  Direction: {result.direction}\n  Motivo: {result.reason}"
        )
    instruments = "\n".join(instrument_lines)

    if result.direction == "POSITIVE":
        operation = (
            "🟢 POSSIBILE OPERAZIONE DA VALUTARE\n"
            f"Esposizione rialzista su {result.assets[0]} — {ASSET_NAMES.get(result.assets[0], result.assets[0])}\n"
            f"Direzione: POSITIVA\nMotivo: {result.reason}\n"
            "Confermare prima con prezzo/volume e reazione effettiva del mercato."
        )
    elif result.direction == "NEGATIVE":
        operation = (
            "🔴 POSSIBILE OPERAZIONE DA VALUTARE\n"
            f"Esposizione ribassista su {result.assets[0]} — {ASSET_NAMES.get(result.assets[0], result.assets[0])}\n"
            f"Direzione: NEGATIVA\nMotivo: {result.reason}\n"
            "Confermare prima con prezzo/volume e reazione effettiva del mercato."
        )
    else:
        operation = (
            "🟡 POSSIBILE OPERAZIONE\n"
            "NESSUNA OPERAZIONE DIREZIONALE AL MOMENTO\n"
            f"Motivo: la direzione del catalyst è MIXED ({result.reason})."
        )

    return (
        "🚨 TRUMP MARKET RADAR\n\n"
        "🇺🇸 " + post.text
        + "\n\n🏷️ Category: " + result.category
        + "\n📊 Direction: " + result.direction
        + "\n🎯 Priority: " + result.priority
        + "\n\n👀 STRUMENTI DA MONITORARE\n"
        + instruments
        + "\n\n" + operation
        + "\n\n🔎 Catalyst: " + result.reason
    )
def send_telegram(message: str) -> None:
    url = "https://api.telegram.org/bot" + os.environ["TELEGRAM_BOT_TOKEN"] + "/sendMessage"
    payload = {"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": message}
    for attempt in range(3):
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code != 429:
            r.raise_for_status()
            return
        try:
            retry_after = int(r.json().get("parameters", {}).get("retry_after", 5))
        except (ValueError, TypeError):
            retry_after = 5
        time.sleep(min(retry_after + 1, 30))
    r.raise_for_status()
