#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract ~10 WordPress posts (title, link, body) from a WXR/XML dump and save as JSON.

Usage:
  python extract_wp_posts.py --xml observations-dump.xml --out posts_sample.json --limit 10

Changes vs prior version:
- Uses WordPress wp:post_id as the stable `id` (no deterministic hash).
"""

import argparse
import json
import re
import sys
from html import unescape
from xml.etree import ElementTree as ET

WP_NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/"
}

def clean_text(html_str: str) -> str:
    """Convert basic HTML to readable plain text (no external deps)."""
    if not html_str:
        return ""
    s = unescape(html_str)

    # Preserve block breaks before stripping tags
    s = s.replace("</p>", "\n\n").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    s = re.sub(r"</li\s*>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"</h[1-6]\s*>", "\n\n", s, flags=re.IGNORECASE)

    # Remove all tags
    s = re.sub(r"<[^>]+>", "", s)

    # Normalize whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def extract_posts(xml_path: str, limit: int):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    channel = root.find("channel")
    if channel is None:
        raise ValueError("Invalid WXR: <channel> not found")

    items = channel.findall("item")
    out = []

    for it in items:
        # Filter published blog posts
        post_type_el = it.find("wp:post_type", WP_NS)
        status_el = it.find("wp:status", WP_NS)
        if post_type_el is None or status_el is None:
            continue
        if post_type_el.text != "post" or status_el.text != "publish":
            continue

        # Required fields
        post_id_el = it.find("wp:post_id", WP_NS)
        title_el = it.find("title")
        link_el = it.find("link")

        if post_id_el is None or not (post_id_el.text and post_id_el.text.strip()):
            # Skip if no stable WordPress post ID
            continue

        # Body from full content only
        body_el = it.find("content:encoded", WP_NS)

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""

        raw_body = body_el.text if (body_el is not None and body_el.text and body_el.text.strip()) else None

        body_text = clean_text(raw_body or "")

        # Enforce essentials present
        if not title or not link or not body_text:
            continue

        out.append({
            "id": post_id_el.text.strip(),   # <— use WordPress wp:post_id
            "title": title,
            "link": link,
            "body": body_text
        })

        if len(out) >= limit:
            break

    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", required=True, help="Path to WordPress WXR/XML file (e.g., observations-dump.xml)")
    ap.add_argument("--out", required=True, help="Output JSON path (e.g., posts_sample.json)")
    ap.add_argument("--limit", type=int, default=10, help="Number of posts to extract (default: 10)")
    args = ap.parse_args()

    try:
        posts = extract_posts(args.xml, args.limit)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not posts:
        print("No posts extracted. Check filters (post_type/status) and XML structure.", file=sys.stderr)
        sys.exit(2)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(posts)} posts → {args.out}")

if __name__ == "__main__":
    main()
