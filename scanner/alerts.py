import os
import requests
from .classifier import Classification
from .trump_source import TrumpPost

def format_alert(post: TrumpPost, result: Classification) -> str:
    assets = "\n".join("• " + x for x in result.assets)
    return "🚨 TRUMP MARKET RADAR\n\n🇺🇸 " + post.text + "\n\n🏷️ Category: " + result.category + "\n📊 Direction: " + result.direction + "\n🎯 Priority: " + result.priority + "\n\n👀 Assets to watch:\n" + assets + "\n\n🔎 " + result.reason

def send_telegram(message: str) -> None:
    r = requests.post("https://api.telegram.org/bot" + os.environ["TELEGRAM_BOT_TOKEN"] + "/sendMessage", json={"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": message}, timeout=20)
    r.raise_for_status()
