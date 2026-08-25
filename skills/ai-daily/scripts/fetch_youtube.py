#!/usr/bin/env python3
"""Fetch current-window videos from the configured AI YouTube channels."""
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta


CHANNELS = {
    "Y Combinator": "UCcefcZRL2oaA_uBNeo5UOWg",
    "Lenny's Podcast": "UC6t1O76G0jYXOAoYCm153dA",
    "Peter Yang": "UC7bn50F_ujOrD6UerbAtlXw",
    "Nate Herk": "UC2ojq-nuP8ceeHqiroeKhBA",
    "Greg Isenberg": "UCPjNBjflYl0-HQtUvOx0Ibw",
    "Aakash Gupta": "UCpvbYcuKFwa9YTo8q5L8QXA",
    "Every": "UCjIMtrzxYc0lblGhmOgC_CA",
    "Silicon Valley Girl": "UCiq1FIgtEK7LRAOB1JXTPig",
    "a16z": "UC9cn0TuPq4dnbTY-CBsm8XA",
    "Sequoia Capital": "UCWrF0oN6unbXrWsTN7RctTw",
}

# HTML fallback handles are deliberately kept separate from channel IDs. RSS
# has occasionally returned 404/500 for valid channels, while the public
# /@handle/videos page remained available.
CHANNEL_HANDLES = {
    "Y Combinator": "ycombinator",
    "Lenny's Podcast": "lennyspodcast",
    "Peter Yang": "PeterYang",
    "Nate Herk": "nateherk",
    "Greg Isenberg": "gregisenberg",
    "Aakash Gupta": "aakashgupta",
    "Every": "EveryInc",
    "Silicon Valley Girl": "siliconvalleygirl",
    "a16z": "a16z",
    "Sequoia Capital": "sequoiacapital",
}

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'yt': 'http://www.youtube.com/xml/schemas/2015',
    'media': 'http://search.yahoo.com/mrss/',
}


def fetch_url(url, retries=3, timeout=15):
    last_error = None
    for attempt in range(retries):
        if attempt > 0:
            time.sleep(2 ** attempt)
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as error:
            last_error = error
    raise last_error


def fetch_rss(channel_id, retries=3):
    return fetch_url(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        retries=retries,
        timeout=10,
    )


def parse_feed(name, xml_data, today, yesterday, beijing_tz):
    root = ET.fromstring(xml_data)
    videos = []
    for entry in root.findall('atom:entry', NS):
        title_el = entry.find('atom:title', NS)
        link_el = entry.find('atom:link', NS)
        published_el = entry.find('atom:published', NS)
        if title_el is None or published_el is None or not published_el.text:
            continue
        published = datetime.fromisoformat(published_el.text.replace('Z', '+00:00'))
        published_date = published.astimezone(beijing_tz).date()
        if published_date not in (today, yesterday):
            continue
        url = link_el.get('href', '') if link_el is not None else ''
        if not title_el.text or not url:
            continue
        videos.append({
            "channel": name,
            "title": title_el.text,
            "url": url,
            "published": published.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M'),
        })
    return videos


def parse_video_page(video_id, body, today, yesterday, beijing_tz, channel):
    date_patterns = (
        r'<meta[^>]+itemprop="datePublished"[^>]+content="([^"]+)"',
        r'<meta[^>]+itemprop="uploadDate"[^>]+content="([^"]+)"',
        r'"publishDate":"([^"]+)"',
        r'"uploadDate":"([^"]+)"',
    )
    published = None
    for pattern in date_patterns:
        match = re.search(pattern, body, flags=re.I)
        if match:
            try:
                published = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
                break
            except ValueError:
                continue
    if published is None:
        return None

    published = published if published.tzinfo else published.replace(tzinfo=timezone.utc)
    if published.astimezone(beijing_tz).date() not in (today, yesterday):
        return None

    title_match = re.search(r'<meta[^>]+name="title"[^>]+content="([^"]+)"', body, flags=re.I)
    if not title_match:
        title_match = re.search(r'<title>(.*?)</title>', body, flags=re.I | re.S)
    title = html.unescape(title_match.group(1)).strip() if title_match else ''
    title = re.sub(r'\s+-\s+YouTube\s*$', '', title).strip()
    if not title:
        return None

    localized = published.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M')
    return {
        'channel': channel,
        'title': title,
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'published': localized,
    }


def fetch_html_fallback(name, handle, today, yesterday, beijing_tz):
    listing_url = f'https://www.youtube.com/@{handle}/videos?hl=en'
    listing = fetch_url(listing_url, timeout=20).decode('utf-8', errors='ignore')
    video_ids = list(dict.fromkeys(re.findall(r'"videoId":"([\w-]{11})"', listing)))[:15]
    if not video_ids:
        raise ValueError('channel page contained no video IDs')

    def fetch_one(video_id):
        body = fetch_url(
            f'https://www.youtube.com/watch?v={video_id}&hl=en',
            timeout=20,
        ).decode('utf-8', errors='ignore')
        return parse_video_page(video_id, body, today, yesterday, beijing_tz, name)

    videos = []
    verified_pages = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_one, video_id) for video_id in video_ids]
        for future in as_completed(futures):
            try:
                video = future.result()
                verified_pages += 1
            except Exception:
                continue
            if video:
                videos.append(video)

    if not videos:
        # A reachable page with verifiable video metadata but no current-window
        # videos is a valid empty result; only fail when no video page could be
        # verified at all.
        if verified_pages:
            return []
        raise ValueError('video pages contained no publish metadata')
    videos.sort(key=lambda item: item['published'], reverse=True)
    return videos


def describe_error(error):
    detail = str(error).strip().replace('\n', ' ')
    if len(detail) > 180:
        detail = detail[:177] + '...'
    return f'{type(error).__name__}: {detail}' if detail else type(error).__name__


def main():
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).date()
    yesterday = today - timedelta(days=1)

    results = []
    failed_channels = []
    for name, channel_id in CHANNELS.items():
        try:
            xml_data = fetch_rss(channel_id)
            videos = parse_feed(name, xml_data, today, yesterday, beijing_tz)
            results.extend(videos)
            print(f'[OK] YouTube/{name} ({len(videos)} videos; RSS)', file=sys.stderr)
            continue
        except Exception as rss_error:
            handle = CHANNEL_HANDLES.get(name)
            try:
                videos = fetch_html_fallback(name, handle, today, yesterday, beijing_tz)
                results.extend(videos)
                print(
                    f'[OK] YouTube/{name} ({len(videos)} videos; HTML fallback after '
                    f'RSS {describe_error(rss_error)})',
                    file=sys.stderr,
                )
                continue
            except Exception as html_error:
                failed_channels.append(name)
                print(
                    f'[FAIL] YouTube/{name}: RSS {describe_error(rss_error)}; '
                    f'HTML fallback {describe_error(html_error)}',
                    file=sys.stderr,
                )

    sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

    if len(failed_channels) == len(CHANNELS):
        print(
            f'[FAIL] YouTube: all {len(CHANNELS)} channel feeds and fallbacks failed',
            file=sys.stderr,
        )
        return 2
    if failed_channels:
        print(
            f'[WARN] YouTube: {len(failed_channels)}/{len(CHANNELS)} channels failed '
            'after RSS and HTML fallback',
            file=sys.stderr,
        )
    else:
        print(
            f'[OK] YouTube ({len(results)} videos; all {len(CHANNELS)} channels reachable)',
            file=sys.stderr,
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
