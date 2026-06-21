#!/usr/bin/env python3
"""Fetch today's YouTube videos from AI channels via RSS."""
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

CHANNELS = {
    "Y Combinator": "UCxIJaCMEptJjxmmQgGFsnCg",
    "Lenny's Podcast": "UC6t1O76G0jYXOAoYCm153dA",
    "Peter Yang": "UC7bn50F_ujOrD6UerbAtlXw",
    "Nate Herk": "UC2ojq-nuP8ceeHqiroeKhBA",
    "Greg Isenberg": "UCPjNBjflYl0-HQtUvOx0Ibw",
    "Aakash Gupta": "UCpvbYcuKFwa9YTo8q5L8QXA",
    "Every": "UCiJEYFVVhn_oKbAdIAWdNpg",
    "Silicon Valley Girl": "UCOgUsZMGaAly94NDsiwEFww",
    "a16z": "UC9cn0TuPq4dnbTY-CBsm8XA",
    "Sequoia Capital": "UCWrF0oN6unbXrWsTN7RctTw"
}

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'yt': 'http://www.youtube.com/xml/schemas/2015',
    'media': 'http://search.yahoo.com/mrss/'
}

def fetch_rss(channel_id, retries=3):
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    last_err = None
    for attempt in range(retries):
        if attempt > 0:
            time.sleep(2 ** attempt)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.read()
        except Exception as e:
            last_err = e
    raise last_err

def parse_feed(name, xml_data, today, yesterday, beijing_tz):
    root = ET.fromstring(xml_data)
    videos = []
    for entry in root.findall('atom:entry', NS):
        title_el = entry.find('atom:title', NS)
        link_el = entry.find('atom:link', NS)
        published_el = entry.find('atom:published', NS)
        if title_el is None or published_el is None:
            continue
        pub = datetime.fromisoformat(published_el.text.replace('Z', '+00:00'))
        pub_date = pub.astimezone(beijing_tz).date()
        if pub_date in [today, yesterday]:
            videos.append({
                "channel": name,
                "title": title_el.text,
                "url": link_el.get('href', '') if link_el is not None else '',
                "published": pub.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M')
            })
    return videos

def main():
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).date()
    yesterday = today - timedelta(days=1)

    results = []
    for name, channel_id in CHANNELS.items():
        try:
            xml_data = fetch_rss(channel_id)
            videos = parse_feed(name, xml_data, today, yesterday, beijing_tz)
            results.extend(videos)
        except Exception:
            continue

    sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

main()
