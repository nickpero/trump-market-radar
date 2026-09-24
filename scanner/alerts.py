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
    assets = "\n".join("• " + x + " — " + ASSET_NAMES.get(x, x) for x in result.assets)
    return "🚨 TRUMP MARKET RADAR\n\n🇺🇸 " + post.text + "\n\n🏷️ Category: " + result.category + "\n📊 Direction: " + result.direction + "\n🎯 Priority: " + result.priority + "\n\n👀 Strumenti da monitorare:\n" + assets + "\n\n🔎 " + result.reason
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
