import json
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
