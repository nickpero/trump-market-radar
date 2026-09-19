import argparse
import os
import time
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
    posts = posts[:100]

    # On the first live run, do not replay the entire historical feed into Telegram.
    # We seed the baseline and inspect only the newest post.
    bootstrap = not seen
    candidates = posts[:1] if bootstrap else posts

    new_ids = set(seen)
    alerts_sent = 0
    max_alerts_per_run = 3

    for post in candidates:
        if post.post_id in seen:
            continue

        new_ids.add(post.post_id)
        result = classify(post.text)

        if not result.relevant:
            continue

        message = format_alert(post, result)
        print(message)

        if not a.fixture and os.environ.get("TELEGRAM_BOT_TOKEN") and alerts_sent < max_alerts_per_run:
            send_telegram(message)
            alerts_sent += 1
            time.sleep(1.2)

    # During bootstrap, mark the entire current feed as seen so old posts
    # are never replayed on the next scheduled run.
    if bootstrap:
        new_ids.update(post.post_id for post in posts)

    save_ids(new_ids)

if __name__ == "__main__":
    main()
