#!/usr/bin/env python3
"""Fetch today's AI news from official blogs and independent sources.

Strategy per source:
  Anthropic   — sitemap.xml (has lastmod dates) + article page og meta
  Claude Blog — blog listing page (slugs) + article page JSON-LD date + og meta
  OpenAI      — RSS feed
  The AI Valley — RSS feed
  Every.to    — posts sitemap + article metadata (legacy RSS fallback)
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
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    for fmt in ('%b %d, %Y', '%B %d, %Y', '%b %d %Y', '%B %d %Y', '%B %Y', '%b %Y'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=BEIJING_TZ)
        except ValueError:
            pass
    return None

def has_window_human_date(body, today, yesterday):
    """Whether page text visibly contains a date in the current digest window."""
    dates = re.findall(
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\b',
        body,
    )
    return any(in_window(parse_date(value), today, yesterday) for value in dates)

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
        r'"publishedOn"\s*:\s*"([^"]+)"',
        r'<meta[^>]+property="article:published_time"[^>]+content="([^"]*)"',
        r'<meta[^>]+content="([^"]*)"[^>]+property="article:published_time"',
    ):
        match = re.search(pattern, body)
        if match:
            dt = parse_date(html.unescape(match.group(1)))
            if dt:
                return dt

    for time_match in re.finditer(r'<time\b[^>]*>([^<]+)</time>', body):
        dt = parse_date(strip_html(time_match.group(1)))
        if dt:
            return dt

    title_match = re.search(r'<h1\b[^>]*>.*?</h1>', body, flags=re.S)
    if title_match:
        surrounding = body[max(0, title_match.start() - 600):min(len(body), title_match.end() + 1200)]
        date_match = re.search(
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\b',
            strip_html(surrounding),
        )
        if date_match:
            return parse_date(date_match.group(0))

    date_matches = re.findall(
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\b',
        strip_html(body[:4000]),
    )
    for dm in date_matches:
        dt = parse_date(dm)
        if dt:
            return dt

    month_year_match = re.search(
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',
        strip_html(body[:4000]),
    )
    if month_year_match:
        dt = parse_date(month_year_match.group(0))
        if dt:
            return dt

    return None

def parse_every_page_date(body):
    """Extract Every.to's real publication date from article metadata."""
    for pattern in (
        r'<meta[^>]+property="article:published_time"[^>]+content="([^"]*)"',
        r'<meta[^>]+content="([^"]*)"[^>]+property="article:published_time"',
        r'"datePublished"\s*:\s*"([^"]+)"',
    ):
        match = re.search(pattern, body)
        if match:
            dt = parse_date(html.unescape(match.group(1)))
            if dt:
                return dt
    return None


# ── RSS / Atom parser ─────────────────────────────────────────────────────────

def parse_rss_or_atom(xml_bytes, source_name, category, today, yesterday):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(f'[XML ERROR] {source_name}: {e}', file=sys.stderr)
        raise ValueError(f'{source_name} returned malformed XML: {e}') from e

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
            if not desc and link:
                try:
                    page_bytes = fetch(link, timeout=8, retries=1)
                    page_body = page_bytes.decode('utf-8', errors='ignore')
                    desc = get_meta(page_body, 'og:description') or get_meta(page_body, 'description')
                except Exception:
                    pass
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
            if not desc and link:
                try:
                    page_bytes = fetch(link, timeout=8, retries=1)
                    page_body = page_bytes.decode('utf-8', errors='ignore')
                    desc = get_meta(page_body, 'og:description') or get_meta(page_body, 'description')
                except Exception:
                    pass
            articles.append({
                "title": title, "url": link, "source": source_name,
                "category": category, "date": format_date(pub),
                "summary": truncate(desc),
            })
    return articles


# ── Source fetchers ───────────────────────────────────────────────────────────

def fetch_anthropic(today, yesterday):
    """Discover from News and sitemap, then verify each page's publish date."""
    articles = []
    candidates = []
    listing_dates = {}
    sitemap_dates = {}
    listing_has_recent_date = False

    # The visible listing is the primary discovery source. It is updated for
    # readers independently of sitemap metadata.
    try:
        listing = fetch('https://www.anthropic.com/news').decode('utf-8', errors='ignore')
        listing_has_recent_date = has_window_human_date(listing, today, yesterday)
        for path in re.findall(r'href="(/news/[a-z0-9\-]+|/research/[a-z0-9\-]+|/claude-[a-z0-9\-]+)"', listing):
            candidates.append(f'https://www.anthropic.com{path}')

        for m in re.finditer(r'<a[^>]+href="(/[^"#?]+)"[^>]*>.*?<time[^>]*>([^<]+)</time>', listing, re.S):
            c_path = m.group(1)
            c_date = parse_date(m.group(2))
            if c_date:
                listing_dates[f'https://www.anthropic.com{c_path}'] = c_date
    except Exception as e:
        print(f'[WARN] Anthropic News listing: {e}', file=sys.stderr)

    # Sitemap is a supplemental discovery source only. Its lastmod must never
    # be presented or used as an article publish date.
    try:
        xml_bytes = fetch('https://www.anthropic.com/sitemap.xml')
        root = ET.fromstring(xml_bytes)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for url_el in root.findall('.//sm:url', ns):
            loc = (url_el.findtext('sm:loc', namespaces=ns) or '').strip()
            mod = (url_el.findtext('sm:lastmod', namespaces=ns) or '').strip()
            mod_dt = parse_date(mod)
            if any(k in loc for k in ('/news/', '/research/', '/claude-')) and in_window(mod_dt, today, yesterday):
                candidates.append(loc)
                if mod_dt:
                    sitemap_dates[loc] = mod_dt
    except Exception as e:
        print(f'[WARN] Anthropic sitemap: {e}', file=sys.stderr)

    candidates = list(dict.fromkeys(candidates))
    if not candidates:
        print('[FAIL] Anthropic: no listing or sitemap candidates', file=sys.stderr)
        return []

    page_failures = 0
    for url in candidates:
        try:
            body = fetch(url).decode('utf-8', errors='ignore')
            dt = parse_anthropic_page_date(body) or listing_dates.get(url) or sitemap_dates.get(url)
            if not in_window(dt, today, yesterday):
                continue
            title_match = re.search(r'<title>([^<|]+)', body)
            title   = get_meta(body, 'og:title') or (title_match.group(1).strip() if title_match else '')
            summary = get_meta(body, 'og:description')
            if not title:
                continue
            title = re.sub(r'\s*[\\|]\s*Anthropic.*$', '', title).strip()
            articles.append({
                "title": title, "url": url, "source": "Anthropic",
                "category": "Official Update", "date": format_date(dt),
                "summary": truncate(summary),
            })
        except Exception:
            page_failures += 1
            continue

    if page_failures == len(candidates) and candidates:
        print(
            f'[FAIL] Anthropic: all {len(candidates)} article pages failed',
            file=sys.stderr,
        )
    elif listing_has_recent_date and not articles:
        print('[FAIL] Anthropic: listing has a current-window date but no article was parsed', file=sys.stderr)
    else:
        if page_failures:
            print(
                f'[WARN] Anthropic: {page_failures}/{len(candidates)} article pages failed',
                file=sys.stderr,
            )
        print(f'[OK] Anthropic ({len(articles)} articles)', file=sys.stderr)
    return articles

def fetch_claude_blog(today, yesterday):
    """Blog listing page → top slugs → fetch each article's JSON-LD date + og meta."""
    articles = []
    try:
        body = fetch('https://claude.com/blog').decode('utf-8', errors='ignore')
        starts = list(re.finditer(
            r'<div role="listitem" class="blog_cms_item w-dyn-item">',
            body,
        ))
    except Exception as e:
        print(f'[FAIL] Claude Blog listing: {e}', file=sys.stderr)
        return []

    cards = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(body)
        card = body[start.start():end]
        date_match = re.search(r'fs-list-fieldtype="date"[^>]*>([^<]+)<', card)
        title_match = re.search(r'card_blog_title[^>]*>(.*?)</div>', card, flags=re.S)
        url_match = re.search(r'href="(/blog/[a-z0-9][a-z0-9\-]+)"', card)
        dt = parse_date(strip_html(date_match.group(1)) if date_match else '')
        if title_match and url_match and in_window(dt, today, yesterday):
            cards.append((
                f'https://claude.com{url_match.group(1)}',
                strip_html(title_match.group(1)),
                dt,
            ))

    if not starts:
        print('[FAIL] Claude Blog: no dated blog cards found', file=sys.stderr)
        return []
    if has_window_human_date(body, today, yesterday) and not cards:
        print('[FAIL] Claude Blog: listing has a current-window date but no card was parsed', file=sys.stderr)
        return []

    page_failures = 0
    for url, listing_title, dt in cards:
        try:
            page = fetch(url).decode('utf-8', errors='ignore')
            # Listing date is authoritative for discovery; only replace it
            # when the article has a machine-readable publish date.
            ld_match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', page)
            if ld_match:
                page_dt = parse_date(ld_match.group(1))
                if page_dt:
                    dt = page_dt

            title   = get_meta(page, 'og:title').replace(' | Claude', '').replace(' by Anthropic', '').strip() or listing_title
            summary = get_meta(page, 'og:description')
            articles.append({
                "title": title, "url": url, "source": "Claude Blog",
                "category": "Official Update", "date": format_date(dt),
                "summary": truncate(summary),
            })
        except Exception:
            page_failures += 1
            articles.append({
                "title": listing_title, "url": url, "source": "Claude Blog",
                "category": "Official Update", "date": format_date(dt),
                "summary": "",
            })

    if page_failures:
        print(
            f'[WARN] Claude Blog: {page_failures}/{len(cards)} article pages failed; '
            'listing metadata was retained',
            file=sys.stderr,
        )
    print(f'[OK] Claude Blog ({len(articles)} articles)', file=sys.stderr)
    return articles


def fetch_every_article(url, today, yesterday):
    """Fetch one Every.to sitemap candidate and verify its publish date."""
    try:
        body = fetch(url).decode('utf-8', errors='ignore')
        dt = parse_every_page_date(body)
        if dt is None:
            return None, 'date-metadata'
        if not in_window(dt, today, yesterday):
            return None, 'out-of-window'

        title = get_meta(body, 'og:title')
        if not title:
            title_match = re.search(r'<title>([^<|]+)', body)
            title = title_match.group(1).strip() if title_match else ''
        summary = get_meta(body, 'og:description')
        if not title:
            return None, 'title-metadata'
        return {
            "title": title, "url": url, "source": "Every.to",
            "category": "Independent News", "date": format_date(dt),
            "summary": truncate(summary),
        }, 'ok'
    except Exception:
        return None, 'fetch-error'


def fetch_every(today, yesterday):
    """Discover current Every.to posts from the new sitemap-backed site.

    Every.to's old newsletter RSS endpoints remain reachable but are stale,
    so HTTP 200 is not enough to treat them as a current-news source.
    """
    sitemap_urls = []
    try:
        index = ET.fromstring(fetch('https://every.to/sitemap.xml'))
        ns = index.tag.split('}')[0] + '}' if index.tag.startswith('{') else ''
        sitemap_urls = [
            loc.text.strip()
            for sitemap in index.findall(f'{ns}sitemap')
            for loc in [sitemap.find(f'{ns}loc')]
            if loc is not None and loc.text and '/sitemaps/posts-' in loc.text
        ]
    except Exception as e:
        print(f'[FAIL] Every.to sitemap index: {e}', file=sys.stderr)
        return None

    candidates = []
    successful_sitemaps = 0
    for sitemap_url in sitemap_urls:
        try:
            root = ET.fromstring(fetch(sitemap_url))
            successful_sitemaps += 1
            ns = root.tag.split('}')[0] + '}' if root.tag.startswith('{') else ''
            for url_el in root.findall(f'{ns}url'):
                loc_el = url_el.find(f'{ns}loc')
                mod_el = url_el.find(f'{ns}lastmod')
                loc = loc_el.text.strip() if loc_el is not None and loc_el.text else ''
                lastmod = mod_el.text.strip() if mod_el is not None and mod_el.text else ''
                if loc and in_window(parse_date(lastmod), today, yesterday):
                    candidates.append(loc)
        except Exception as e:
            print(f'[WARN] Every.to sitemap: {sitemap_url} — {e}', file=sys.stderr)

    if not successful_sitemaps:
        print('[FAIL] Every.to sitemap: no post sitemap succeeded', file=sys.stderr)
        return None

    candidates = list(dict.fromkeys(candidates))
    if not candidates:
        print('[OK] Every.to (0 articles; no current-window sitemap candidates)', file=sys.stderr)
        return []

    articles = []
    status_counts = {}
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(fetch_every_article, url, today, yesterday) for url in candidates]
        for future in as_completed(futures):
            article, status = future.result()
            status_counts[status] = status_counts.get(status, 0) + 1
            if article:
                articles.append(article)

    failed_pages = status_counts.get('fetch-error', 0)
    metadata_failures = sum(
        count for status, count in status_counts.items()
        if status in {'date-metadata', 'title-metadata'}
    )
    if failed_pages + metadata_failures == len(candidates):
        print(
            f'[FAIL] Every.to: all {len(candidates)} sitemap candidates failed verification',
            file=sys.stderr,
        )
    elif failed_pages or metadata_failures:
        print(
            f'[WARN] Every.to: {failed_pages + metadata_failures}/{len(candidates)} '
            'candidates failed verification',
            file=sys.stderr,
        )
        print(
            f'[OK] Every.to ({len(articles)} articles; '
            f'{len(candidates)} sitemap candidates)',
            file=sys.stderr,
        )
    else:
        print(
            f'[OK] Every.to ({len(articles)} articles; '
            f'{len(candidates)} sitemap candidates)',
            file=sys.stderr,
        )
    return articles


def fetch_the_ai_valley(today, yesterday):
    """Fetch The AI Valley via RSS, then fall back to its Beehiiv listing."""
    rss_urls = [
        'https://www.theaivalley.com/feed/',
        'https://www.theaivalley.com/feed',
        'https://www.theaivalley.com/rss.xml',
    ]
    for url in rss_urls:
        try:
            xml_bytes = fetch(url)
            articles = parse_rss_or_atom(
                xml_bytes, 'The AI Valley', 'Independent News', today, yesterday
            )
            print(f'[OK] The AI Valley ({len(articles)} articles) — {url}', file=sys.stderr)
            return articles
        except Exception as error:
            print(f'[WARN] The AI Valley RSS {url}: {error}', file=sys.stderr)

    # The publication migrated these URLs to a Beehiiv-rendered HTML page. The
    # page still exposes article cards with a machine-readable <time> value.
    try:
        body = fetch('https://www.theaivalley.com/').decode('utf-8', errors='ignore')
        articles = []
        seen = set()
        for match in re.finditer(r'href="(/p/[a-z0-9][a-z0-9\-]+)"', body):
            url = f'https://www.theaivalley.com{match.group(1)}'
            if url in seen:
                continue
            card = body[match.start():match.start() + 8000]
            date_match = re.search(r'<time[^>]+dateTime="([^"]+)"', card, flags=re.I)
            dt = parse_date(html.unescape(date_match.group(1))) if date_match else None
            if not in_window(dt, today, yesterday):
                continue
            title_match = re.search(r'<h2[^>]*>(.*?)</h2>', card, flags=re.I | re.S)
            summary_match = re.search(r'<p[^>]*>(.*?)</p>', card, flags=re.I | re.S)
            title = strip_html(title_match.group(1)) if title_match else ''
            if not title:
                continue
            seen.add(url)
            articles.append({
                'title': title, 'url': url, 'source': 'The AI Valley',
                'category': 'Independent News', 'date': format_date(dt),
                'summary': truncate(strip_html(summary_match.group(1)) if summary_match else ''),
            })

        print(
            f'[OK] The AI Valley ({len(articles)} articles; homepage fallback)',
            file=sys.stderr,
        )
        return articles
    except Exception as error:
        print(f'[FAIL] The AI Valley: RSS and homepage fallback failed — {error}', file=sys.stderr)
        return []


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
        "name": "Google DeepMind",
        "category": "Official Update",
        "rss_urls": [
            "https://deepmind.google/blog/rss.xml",
        ],
    },
    {
        "name": "Google",
        "category": "Official Update",
        "rss_urls": [
            "https://blog.google/technology/ai/rss/",
        ],
    },
    {
        "name": "OpenAI",
        "category": "Official Update",
        "rss_urls": [
            "https://openai.com/news/rss.xml",
            "https://openai.com/blog/rss.xml",
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
    results.extend(fetch_the_ai_valley(today, yesterday))

    # Every.to migrated away from its newsletter feeds; use the sitemap-backed
    # discovery path first and retain the old feeds only as a transport fallback.
    every_articles = fetch_every(today, yesterday)
    if every_articles is None:
        for src in RSS_SOURCES:
            if src['name'] == 'Every.to':
                results.extend(fetch_rss_source(
                    src['name'], src['category'], src['rss_urls'], today, yesterday
                ))

    # RSS sources
    for src in RSS_SOURCES:
        if src['name'] == 'Every.to':
            continue
        results.extend(fetch_rss_source(
            src['name'], src['category'], src['rss_urls'], today, yesterday
        ))
    if every_articles is not None:
        results.extend(every_articles)

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
