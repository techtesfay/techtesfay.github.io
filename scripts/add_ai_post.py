#!/usr/bin/env python3
"""Interactively add a new post to ai-skills.json.

Prompts for a title, a body (multi-line, blank line to finish), and tags,
then prepends the new post to ai-skills.json (newest first) and prints a
ready-to-paste Facebook version. No dependencies — run with:

    python3 scripts/add_ai_post.py
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "ai-skills.json"


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "post"


def read_multiline(prompt):
    print(prompt)
    print("(Type your post, then an empty line to finish.)")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        if line == "" and not lines:
            continue
        lines.append(line)
    # Collapse the trailing blank line used to terminate input.
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"generated_at": None, "items": []}


def main():
    data = load_data()
    items = data.get("items", [])
    next_day = (items[0]["day"] + 1) if items else 1

    print(f"Adding Day {next_day} post to {DATA_FILE.name}\n")
    title = input("Title: ").strip()
    if not title:
        print("A title is required.", file=sys.stderr)
        sys.exit(1)

    body = read_multiline("\nBody (separate paragraphs with a blank line):")
    if not body:
        print("A body is required.", file=sys.stderr)
        sys.exit(1)

    tags_raw = input("\nTags (comma-separated, e.g. prompting, beginner): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    today = date.today().isoformat()
    post = {
        "id": f"{today}-{slugify(title)}",
        "day": next_day,
        "date": today,
        "title": title,
        "body": body,
        "tags": tags,
    }

    items.insert(0, post)  # newest first, matching ai-skills.html's render order
    data["items"] = items
    data["generated_at"] = datetime.now(timezone.utc).isoformat()

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"\nSaved Day {next_day}: {title}\n")

    fb_tags = " ".join("#" + re.sub(r"[^a-z0-9]", "", t, flags=re.IGNORECASE) for t in tags)
    fb_text = "\n\n".join(
        part for part in [
            f"Day {next_day}: {title}",
            body,
            fb_tags,
            "Follow the daily series: https://lelunar.me/ai-skills.html",
        ] if part
    )

    print("---- Copy this for Facebook ----\n")
    print(fb_text)
    print("\n---------------------------------")


if __name__ == "__main__":
    main()
