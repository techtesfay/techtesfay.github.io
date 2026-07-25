#!/usr/bin/env python3
"""Pull headlines from a curated set of free RSS feeds into news.json.

No API keys, no paid services — just RSS. Run on a schedule by
.github/workflows/news.yml, or manually: python3 scripts/fetch_news.py
"""

import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

FEEDS = [
    {"name": "The Hacker News", "category": "cybersecurity", "url": "https://feeds.feedburner.com/TheHackersNews"},
    {"name": "Krebs on Security", "category": "cybersecurity", "url": "https://krebsonsecurity.com/feed/"},
    {"name": "SANS Internet Storm Center", "category": "cybersecurity", "url": "https://isc.sans.edu/rssfeed.xml"},
    {"name": "Dark Reading", "category": "cybersecurity", "url": "https://www.darkreading.com/rss.xml"},
    {"name": "The Record", "category": "cybersecurity", "url": "https://therecord.media/feed"},
    {"name": "arXiv cs.CR", "category": "research", "url": "https://rss.arxiv.org/rss/cs.CR"},
    {"name": "arXiv cs.AI", "category": "research", "url": "https://rss.arxiv.org/rss/cs.AI"},
    {"name": "MIT Technology Review", "category": "ai", "url": "https://www.technologyreview.com/feed/"},
    {"name": "OpenAI News", "category": "ai", "url": "https://openai.com/news/rss.xml"},
]

PER_FEED_LIMIT = 8
TOTAL_LIMIT = 40
TIMEOUT = 15
TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text):
    if not text:
        return ""
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(raw):
    if not raw:
        return None
    raw = raw.strip()
    try:
        return parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.replace(tzinfo=dt.tzinfo or timezone.utc)
        except ValueError:
            continue
    return None


def fetch_feed(feed):
    req = urllib.request.Request(feed["url"], headers={"User-Agent": "Mozilla/5.0 (compatible; techtesfay-news-bot/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"WARN: failed to fetch {feed['name']}: {exc}", file=sys.stderr)
        return []

    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        print(f"WARN: failed to parse {feed['name']}: {exc}", file=sys.stderr)
        return []

    ns = {"dc": "http://purl.org/dc/elements/1.1/", "atom": "http://www.w3.org/2005/Atom"}
    items = []

    for item in root.findall(".//item")[:PER_FEED_LIMIT]:
        title = strip_html(item.findtext("title", ""))
        link = (item.findtext("link", "") or "").strip()
        raw_date = item.findtext("pubDate") or item.findtext("dc:date", namespaces=ns) or ""
        date = parse_date(raw_date)
        summary = strip_html(item.findtext("description", ""))[:220]
        if not title or not link:
            continue
        items.append({
            "title": title,
            "link": link,
            "source": feed["name"],
            "category": feed["category"],
            "published": date.astimezone(timezone.utc).isoformat() if date else None,
            "summary": summary,
        })

    # Atom-style feeds (e.g. blogspot) as a fallback
    if not items:
        for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:PER_FEED_LIMIT]:
            title = strip_html(entry.findtext("{http://www.w3.org/2005/Atom}title", ""))
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href") if link_el is not None else ""
            raw_date = entry.findtext("{http://www.w3.org/2005/Atom}published") or entry.findtext("{http://www.w3.org/2005/Atom}updated") or ""
            date = parse_date(raw_date)
            if not title or not link:
                continue
            items.append({
                "title": title,
                "link": link,
                "source": feed["name"],
                "category": feed["category"],
                "published": date.astimezone(timezone.utc).isoformat() if date else None,
                "summary": "",
            })

    return items


def main():
    all_items = []
    for feed in FEEDS:
        all_items.extend(fetch_feed(feed))

    all_items.sort(key=lambda x: x["published"] or "", reverse=True)
    all_items = all_items[:TOTAL_LIMIT]

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [f["name"] for f in FEEDS],
        "items": all_items,
    }

    with open("news.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {len(all_items)} items from {len(FEEDS)} feeds to news.json")


if __name__ == "__main__":
    main()
