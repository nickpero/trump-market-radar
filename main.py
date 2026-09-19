import argparse, os
from scanner.alerts import format_alert, send_telegram
from scanner.classifier import classify
from scanner.trump_source import TrumpPost, fetch_posts

FIXTURE = TrumpPost("fixture-001", "We are considering major tariffs on European imports. We will make a decision soon.", "2026-01-01T12:00:00Z")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", action="store_true")
    a = p.parse_args()
    posts = [FIXTURE] if a.fixture else fetch_posts(os.environ.get("TRUMP_SOURCE_URL", ""))
    for post in posts[:10]:
        result = classify(post.text)
        if not result.relevant: continue
        message = format_alert(post, result)
        print(message)
        if not a.fixture and os.environ.get("TELEGRAM_BOT_TOKEN"): send_telegram(message)

if __name__ == "__main__": main()
