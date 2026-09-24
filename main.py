import argparse
import os
import time
from scanner.alerts import format_alert, send_telegram
from scanner.classifier import classify
from scanner.trump_source import TrumpPost, fetch_posts
from scanner.state import canonical_post_id, load_ids, save_ids

FIXTURE = TrumpPost("fixture-001", "We are considering major tariffs on European imports. We will make a decision soon.", "2026-01-01T12:00:00Z")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fixture", action="store_true")
    p.add_argument("--send-fixture", action="store_true")
    a = p.parse_args()

    seen = load_ids()
    posts = [FIXTURE] if a.fixture else fetch_posts(os.environ.get("TRUMP_SOURCE_URL", ""))
    posts = posts[:100]

    bootstrap = not seen
    candidates = posts[:1] if bootstrap else posts

    new_ids = set(seen)
    alerts_sent = 0
    max_alerts_per_run = 3

    for post in candidates:
        event_id = canonical_post_id(post.post_id, post.text)
        if post.post_id in seen or event_id in seen:
            continue

        new_ids.add(post.post_id)
        new_ids.add(event_id)
        result = classify(post.text)

        if not result.relevant:
            continue

        message = format_alert(post, result)
        print(message)

        if (not a.fixture or a.send_fixture) and os.environ.get("TELEGRAM_BOT_TOKEN") and alerts_sent < max_alerts_per_run:
            send_telegram(message)
            alerts_sent += 1
            time.sleep(1.2)

    if bootstrap:
        for post in posts:
            new_ids.add(post.post_id)
            new_ids.add(canonical_post_id(post.post_id, post.text))

    save_ids(new_ids)

if __name__ == "__main__":
    main()
