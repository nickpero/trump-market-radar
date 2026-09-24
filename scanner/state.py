import hashlib
import json
import re
from pathlib import Path

STATE_FILE = Path("data/state.json")

def load_ids():
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text()).get("seen_ids", []))
    except Exception:
        return set()

def save_ids(ids):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"seen_ids": list(ids)[-500:]}, indent=2))

def canonical_post_id(post_id: str, text: str) -> str:
    # Treat reposts/RTs of the same statement as one event.
    # URLs, RT markers and formatting differences should not create duplicates.
    normalized = text.lower()
    normalized = re.sub(r"\bhttps?://\S+", " ", normalized)
    normalized = re.sub(r"\brt\s*@?\s*realdonaldtrump\b[:\s]*", " ", normalized)
    normalized = re.sub(r"\brt\s*:\s*", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return "content-" + digest
