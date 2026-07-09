#!/usr/bin/env python3
"""Fetch today's AI news from official blogs and independent sources.

Strategy per source:
  Anthropic   — sitemap.xml (has lastmod dates) + article page og meta
  Claude Blog — blog listing page (slugs) + article page JSON-LD date + og meta
  OpenAI      — RSS feed
  The AI Valley — RSS feed
  Every.to    — 6 newsletter RSS feeds
  smol.ai     — RSS feed

Returns JSON array to stdout. Each item:
  title, url, source, category, date, summary

Categories: "Official Update" | "Independent News"
Date window: yesterday + today (Beijing time, UTC+8).

stderr shows per-source status for debugging.
"""
import html
import json
import re
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; AI-Daily/1.0)'}

BEIJING_TZ = timezone(timedelta(hours=8))


# ── Utilities ─────────────────────────────────────────────────────────────────

def fetch(url, timeout=12, retries=3):
    last_err = None
    for attempt in range(retries):
        if attempt > 0:
            time.sleep(2 ** attempt)  # 2s, 4s
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last_err = e
    raise last_err

def strip_html(text):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def truncate(text, max_len=220):
    return text[:max_len].rstrip() + '...' if len(text) > max_len else text

def parse_date(date_str):
    """Parse ISO 8601 (Atom) or RFC 2822 (RSS pubDate) into aware datetime."""
    if not date_str:
        return None
    s = date_str.strip()
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return dt if dt.tzinfo else dt.replace(tzinfo=BEIJING_TZ)
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=BEIJING_TZ)
    except Exception:
        pass
    for fmt in ('%b %d, %Y', '%B %d, %Y', '%b %d %Y', '%B %d %Y'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=BEIJING_TZ)
        except ValueError:
            pass
    return None

def in_window(dt, today, yesterday):
    if dt is None:
        return False
    return dt.astimezone(BEIJING_TZ).date() in (today, yesterday)

def format_date(dt):
    return dt.astimezone(BEIJING_TZ).strftime('%b %d, %Y')

def get_meta(body, prop):
    """Extract og/twitter meta content regardless of attribute order."""
    p1 = re.search(rf'<meta[^>]+property="{prop}"[^>]+content="([^"]*)"', body)
    p2 = re.search(rf'<meta[^>]+content="([^"]*)"[^>]+property="{prop}"', body)
    m = p1 or p2
    return html.unescape(m.group(1)).strip() if m else ''

def parse_anthropic_page_date(body):
    """Extract the article's real publish date from an Anthropic article page."""
    for pattern in (
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'"publishedAt"\s*:\s*"([^"]+)"',
        r'"publishDate"\s*:\s*"([^"]+)"',
        r'<meta[^>]+property="article:published_time"[^>]+content="([^"]*)"',
        r'<meta[^>]+content="([^"]*)"[^>]+property="article:published_time"',
    ):
        match = re.search(pattern, body)
        if match:
            dt = parse_date(html.unescape(match.group(1)))
            if dt:
                return dt

    title_match = re.search(r'<h1\b[^>]*>.*?</h1>', body, flags=re.S)
    if title_match:
        tail = body[title_match.end():title_match.end() + 1200]
        date_match = re.search(
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\b',
            strip_html(tail),
        )
        if date_match:
            return parse_date(date_match.group(0))

    return None


# ── RSS / Atom parser ─────────────────────────────────────────────────────────

def parse_rss_or_atom(xml_bytes, source_name, category, today, yesterday):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f'[XML ERROR] {source_name}: {e}', file=sys.stderr)
        return []

    tag = root.tag.lower()
    articles = []

    if 'rss' in tag or root.find('channel') is not None:
        # RSS 2.0
        channel = root.find('channel')
        if channel is None:
            channel = root
        for item in channel.findall('item'):
            title = strip_html(item.findtext('title', ''))
            link  = (item.findtext('link', '') or '').strip()
            pub   = parse_date(item.findtext('pubDate') or item.findtext('dc:date'))
            desc  = strip_html(item.findtext('description', ''))
            if not title or not link or not in_window(pub, today, yesterday):
                continue
            articles.append({
                "title": title, "url": link, "source": source_name,
                "category": category, "date": format_date(pub),
                "summary": truncate(desc),
            })
    else:
        # Atom
        ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
        for entry in root.findall(f'{ns}entry'):
            title_el = entry.find(f'{ns}title')
            link_el  = entry.find(f'{ns}link')
            pub_el   = entry.find(f'{ns}published') or entry.find(f'{ns}updated')
            sum_el   = entry.find(f'{ns}summary') or entry.find(f'{ns}content')
            title = strip_html(title_el.text if title_el is not None else '')
            link  = (link_el.get('href', '') if link_el is not None else '').strip()
            pub   = parse_date(pub_el.text if pub_el is not None else '')
            desc  = strip_html(sum_el.text if sum_el is not None else '')
            if not title or not link or not in_window(pub, today, yesterday):
                continue
            articles.append({
                "title": title, "url": link, "source": source_name,
                "category": category, "date": format_date(pub),
                "summary": truncate(desc),
            })
    return articles


# ── Source fetchers ───────────────────────────────────────────────────────────

def fetch_anthropic(today, yesterday):
    """Sitemap discovery -> fetch each article -> filter by page publish date."""
    articles = []
    try:
        xml_bytes = fetch('https://www.anthropic.com/sitemap.xml')
        root = ET.fromstring(xml_bytes)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        candidates = []
        for url_el in root.findall('.//sm:url', ns):
            loc = url_el.findtext('sm:loc', namespaces=ns) or ''
            mod = url_el.findtext('sm:lastmod', namespaces=ns) or ''
            if '/news/' not in loc:
                continue
            if in_window(parse_date(mod), today, yesterday):
                candidates.append(loc)
    except Exception as e:
        print(f'[FAIL] Anthropic sitemap: {e}', file=sys.stderr)
        return []

    for url in candidates:
        try:
            body = fetch(url).decode('utf-8', errors='ignore')
            dt = parse_anthropic_page_date(body)
            if not in_window(dt, today, yesterday):
                continue
            title_match = re.search(r'<title>([^<|]+)', body)
            title   = get_meta(body, 'og:title') or (title_match.group(1).strip() if title_match else '')
            summary = get_meta(body, 'og:description')
            if not title:
                continue
            articles.append({
                "title": title, "url": url, "source": "Anthropic",
                "category": "Official Update", "date": format_date(dt),
                "summary": truncate(summary),
            })
        except Exception:
            continue

    print(f'[OK] Anthropic ({len(articles)} articles)', file=sys.stderr)
    return articles

def fetch_claude_blog(today, yesterday):
    """Blog listing page → top slugs → fetch each article's JSON-LD date + og meta."""
    articles = []
    try:
        body = fetch('https://claude.com/blog').decode('utf-8', errors='ignore')
        # Deduplicated /blog/slug links from listing page
        all_slugs = re.findall(r'href="(/blog/[a-z0-9][a-z0-9\-]+)"', body)
        slugs = list(dict.fromkeys(all_slugs))[:12]  # top 12, deduplicated
    except Exception as e:
        print(f'[FAIL] Claude Blog listing: {e}', file=sys.stderr)
        return []

    for slug in slugs:
        url = f'https://claude.com{slug}'
        try:
            page = fetch(url).decode('utf-8', errors='ignore')
            # Date from JSON-LD BlogPosting.datePublished
            ld_match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', page)
            if not ld_match:
                # Fallback: visible date pattern like "Jun 18 2026"
                dm = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}', page)
                if not dm:
                    continue
                dt = parse_date(dm.group(0))
            else:
                dt = parse_date(ld_match.group(1))

            if not in_window(dt, today, yesterday):
                continue

            title   = get_meta(page, 'og:title').replace(' | Claude', '').strip()
            summary = get_meta(page, 'og:description')
            if not title:
                continue
            articles.append({
                "title": title, "url": url, "source": "Claude Blog",
                "category": "Official Update", "date": format_date(dt),
                "summary": truncate(summary),
            })
        except Exception:
            continue

    print(f'[OK] Claude Blog ({len(articles)} articles)', file=sys.stderr)
    return articles


def fetch_rss_source(name, category, rss_urls, today, yesterday):
    """Try RSS URLs in order; return articles from first success."""
    for url in rss_urls:
        try:
            xml_bytes = fetch(url)
            articles = parse_rss_or_atom(xml_bytes, name, category, today, yesterday)
            print(f'[OK] {name} ({len(articles)} articles) — {url}', file=sys.stderr)
            return articles
        except Exception as e:
            print(f'[SKIP] {url} — {e}', file=sys.stderr)
    print(f'[FAIL] {name} — no RSS URL succeeded', file=sys.stderr)
    return []


RSS_SOURCES = [
    {
        "name": "OpenAI",
        "category": "Official Update",
        "rss_urls": [
            "https://openai.com/news/rss.xml",
            "https://openai.com/feed.xml",
        ],
    },
    {
        "name": "The AI Valley",
        "category": "Independent News",
        "rss_urls": [
            "https://www.theaivalley.com/feed/",
            "https://www.theaivalley.com/feed",
        ],
    },
    {
        "name": "smol.ai",
        "category": "Independent News",
        "rss_urls": [
            "https://news.smol.ai/rss.xml",
            "https://news.smol.ai/feed.xml",
            "https://news.smol.ai/feed",
        ],
    },
    # Every.to — newsletter-specific feeds
    {
        "name": "Every.to",
        "category": "Independent News",
        "rss_urls": ["https://every.to/chain-of-thought/feed"],
    },
    {
        "name": "Every.to",
        "category": "Independent News",
        "rss_urls": ["https://every.to/napkin-math/feed"],
    },
    {
        "name": "Every.to",
        "category": "Independent News",
        "rss_urls": ["https://every.to/superorganizers/feed"],
    },
    {
        "name": "Every.to",
        "category": "Independent News",
        "rss_urls": ["https://every.to/divinations/feed"],
    },
    {
        "name": "Every.to",
        "category": "Independent News",
        "rss_urls": ["https://every.to/context-window/feed"],
    },
]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today     = datetime.now(BEIJING_TZ).date()
    yesterday = today - timedelta(days=1)

    results = []

    # Sitemap-based sources (parallel-ish via sequential calls — fast enough)
    results.extend(fetch_anthropic(today, yesterday))
    results.extend(fetch_claude_blog(today, yesterday))

    # RSS sources
    for src in RSS_SOURCES:
        results.extend(fetch_rss_source(
            src['name'], src['category'], src['rss_urls'], today, yesterday
        ))

    # Deduplicate by URL
    seen = set()
    deduped = []
    for a in results:
        if a['url'] not in seen:
            seen.add(a['url'])
            deduped.append(a)

    # Sort: Official Updates first, then by source name
    order = {"Official Update": 0, "Independent News": 1}
    deduped.sort(key=lambda x: (order.get(x['category'], 9), x['source'], x['date']))

    sys.stdout.buffer.write(json.dumps(deduped, ensure_ascii=False, indent=2).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')


main()
