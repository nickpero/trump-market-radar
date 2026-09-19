import argparse
import os
from scanner.alerts import format_alert, send_telegram
from scanner.classifier import classify
from scanner.trump_source import TrumpPost, fetch_posts
from scanner.state import load_ids, save_ids

FIXTURE = TrumpPost("fixture-001", "We are considering major tariffs on European imports. We will make a decision soon.", "2026-01-01T12:00:00Z")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", action="store_true")
    a = p.parse_args()
    seen = load_ids()
    posts = [FIXTURE] if a.fixture else fetch_posts(os.environ.get("TRUMP_SOURCE_URL", ""))
    new_ids = set(seen)
    for post in posts[:100]:
        if post.post_id in seen:
            continue
        result = classify(post.text)
        new_ids.add(post.post_id)
        if not result.relevant:
            continue
        message = format_alert(post, result)
        print(message)
        if not a.fixture and os.environ.get("TELEGRAM_BOT_TOKEN"):
            send_telegram(message)
    save_ids(new_ids)

if __name__ == "__main__":
    main()
