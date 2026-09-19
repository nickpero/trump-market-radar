import html, re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import feedparser, requests
from bs4 import BeautifulSoup

@dataclass
class TrumpPost:
    post_id: str
    text: str
    published_at: str
    url: str = ""

def clean(v): return re.sub(r"\s+", " ", html.unescape(BeautifulSoup(v or "", "html.parser").get_text(" ", strip=True))).strip()

def fetch_posts(source_url: str, timeout=20):
    if not source_url: raise ValueError("TRUMP_SOURCE_URL is not configured")
    r = requests.get(source_url, timeout=timeout, headers={"User-Agent":"Trump-Market-Radar/1.0"})
    r.raise_for_status()
    if "json" in r.headers.get("content-type","").lower():
        payload=r.json(); items=payload.get("posts",payload) if isinstance(payload,dict) else payload
        return [TrumpPost(str(x.get("id") or x.get("url") or hash(x.get("text",""))), clean(x.get("text") or x.get("content") or ""), str(x.get("published_at") or x.get("created_at") or ""), str(x.get("url") or "")) for x in items]
    feed=feedparser.parse(r.content)
    out=[]
    for x in feed.entries:
        text=clean(getattr(x,"summary","") or getattr(x,"title",""))
        if text: out.append(TrumpPost(str(getattr(x,"id","") or getattr(x,"link","")), text, getattr(x,"published","") or datetime.now(timezone.utc).isoformat(), getattr(x,"link","")))
    return out
