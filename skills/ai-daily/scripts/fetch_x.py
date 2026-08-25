#!/usr/bin/env python3
"""Fetch current-window AI posts from X.com accounts via twscrape.

Credentials are read from ``~/.claude/private/x-creds.json`` or from the
``X_AUTH_TOKEN`` / ``X_CT0`` environment variables. X changes its web bundle
frequently, so this wrapper keeps transport and transaction-id discovery fixes
local instead of silently treating parser errors as an empty result.
"""
import asyncio
import json
import os
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path


CREDS_FILE = Path(os.path.expanduser("~/.claude/private/x-creds.json"))

X_ACCOUNTS = [
    "GoogleLabs", "nickstpierre", "mattturck", "karpathy",
    "garrytan", "levie", "HamelHusain", "alexalbert__",
    "rauchg", "amasad", "george__mack", "mckaywrigley",
    "lennysan", "gregisenberg", "swyx", "kevinweil",
    "joshwoodward", "petergyang"
]

# Post must contain at least one of these keywords (case-insensitive).
AI_KEYWORDS = [
    'ai', 'ml', 'llm', 'gpt', 'claude', 'gemini', 'openai', 'anthropic',
    'model', 'agent', 'prompt', 'token', 'inference', 'training', 'neural',
    'embedding', 'vector', 'rag', 'fine-tun', 'transformer', 'diffusion',
    'multimodal', 'frontier', 'open weight', 'open-weight',
    'chatgpt', 'copilot', 'cursor', 'replit', 'automation',
    'machine learning', 'deep learning', 'foundation model', 'language model',
    'benchmark', 'evals', 'alignment', 'vibe cod', 'coding assistant',
    'startup', 'founder', 'saas', 'product', 'software', 'developer', 'api',
    'open source', 'dataset', 'research', 'paper', 'deploy',
]


def _normalize_proxy(value):
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None

    # Windows may expose protocol-specific values such as
    # ``http=127.0.0.1:7897;https=127.0.0.1:7897``.
    if ';' in value:
        parts = {}
        for part in value.split(';'):
            if '=' in part:
                name, address = part.split('=', 1)
                parts[name.strip().lower()] = address.strip()
        value = parts.get('https') or parts.get('http') or value.split(';', 1)[0]
        if '=' in value:
            value = value.split('=', 1)[1].strip()

    return value if '://' in value else f'http://{value}'


def _detect_proxy():
    """Return the proxy used by the desktop environment, if one is configured."""
    for name in ('HTTPS_PROXY', 'https_proxy', 'HTTP_PROXY', 'http_proxy', 'ALL_PROXY', 'all_proxy'):
        proxy = _normalize_proxy(os.environ.get(name))
        if proxy:
            return proxy

    if sys.platform == 'win32':
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
            )
            enabled, _ = winreg.QueryValueEx(key, 'ProxyEnable')
            configured, _ = winreg.QueryValueEx(key, 'ProxyServer')
            winreg.CloseKey(key)
            if enabled:
                return _normalize_proxy(configured)
        except Exception:
            pass
    return None


PROXY_URL = _detect_proxy()
if PROXY_URL:
    # curl-cffi does not consistently inherit the Windows registry proxy. Set
    # the environment as a compatibility measure and also pass PROXY_URL
    # explicitly to twscrape.API below.
    for _name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'):
        os.environ.setdefault(_name, PROXY_URL)

# Prefer curl-cffi when it is installed, but do not turn a missing optional
# dependency into an opaque import failure; twscrape can fall back to httpx.
if not os.environ.get('TWS_HTTP_BACKEND'):
    try:
        import curl_cffi  # noqa: F401
        os.environ['TWS_HTTP_BACKEND'] = 'curl'
    except ImportError:
        pass

from twscrape import API, gather
from twscrape import xclid
from twscrape.logger import set_log_level

set_log_level('ERROR')


def _patch_xclid_script_parser():
    """Handle both current and legacy X web bundle layouts.

    Recent authenticated X pages still use the legacy ``responsive-web``
    bundle, but its chunk hashes grew from 7 to 16 hex characters. twscrape
    versions that only recognize 7-character hashes report
    ``X web scripts not found`` even though the page is healthy.
    """
    original = getattr(xclid, 'get_scripts_list', None)
    parse_error = getattr(xclid, 'XClIdParseError', Exception)
    if original is None or getattr(original, '_ai_daily_compatible', False):
        return

    direct_script_re = re.compile(
        r"https://abs\.twimg\.com/"
        r"(?:responsive-web/client-web|x-web)/[^\"'\s<>]+?\.js"
        r"(?:\?[^\"'\s<>]*)?"
    )

    def compatible(text):
        try:
            return original(text)
        except parse_error as original_error:
            # Legacy webpack maps: accept the current 16-character hashes as
            # well as the old 7-character format.
            hash_map = {
                match.group(1): match.group(2)
                for match in re.finditer(r'(\d+):"([0-9a-f]{7,64})"', text)
            }
            if hash_map:
                name_map = {}
                for match in re.finditer(r'(\d+):"([^"]+)"', text):
                    value = match.group(2)
                    if not re.fullmatch(r'[0-9a-f]{7,64}', value):
                        name_map[match.group(1)] = value

                return [
                    f"https://abs.twimg.com/responsive-web/client-web/"
                    f"{name_map.get(chunk_id, chunk_id)}.{hash_value}a.js"
                    for chunk_id, hash_value in hash_map.items()
                ]

            direct = list(dict.fromkeys(direct_script_re.findall(text)))
            if direct:
                return direct
            raise original_error

    compatible._ai_daily_compatible = True
    xclid.get_scripts_list = compatible


_patch_xclid_script_parser()


def is_ai_relevant(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in AI_KEYWORDS)


def load_creds():
    auth_token = os.environ.get('X_AUTH_TOKEN')
    ct0 = os.environ.get('X_CT0')
    if auth_token and ct0:
        return auth_token, ct0
    with CREDS_FILE.open(encoding='utf-8') as handle:
        creds = json.load(handle)
    if not creds.get('auth_token') or not creds.get('ct0'):
        raise ValueError('x-creds.json must contain auth_token and ct0')
    return creds['auth_token'], creds['ct0']


def describe_error(error):
    detail = str(error).strip().replace('\n', ' ')
    if len(detail) > 180:
        detail = detail[:177] + '...'
    return f'{type(error).__name__}: {detail}' if detail else type(error).__name__


def _profile_meta(article, prop):
    element = article.find('meta', attrs={'itemprop': prop})
    return element.get('content', '').strip() if element else ''


def fetch_public_profile(username, today, yesterday, beijing_tz):
    """Read the public X profile HTML when the GraphQL queue is rate-limited."""
    url = f'https://x.com/{username}?lang=en'
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode('utf-8', errors='ignore')

    try:
        from bs4 import BeautifulSoup
    except ImportError as error:
        raise RuntimeError('BeautifulSoup is required for the X HTML fallback') from error

    soup = BeautifulSoup(body, 'html.parser')
    article_nodes = soup.select('article[itemtype="https://schema.org/SocialMediaPosting"]')
    if not article_nodes:
        raise RuntimeError('public profile contained no tweet cards')

    posts = []
    seen = set()
    for article in article_nodes:
        published_text = _profile_meta(article, 'datePublished')
        try:
            published = datetime.fromisoformat(published_text.replace('Z', '+00:00'))
        except ValueError:
            continue
        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)
        if published.astimezone(beijing_tz).date() not in (today, yesterday):
            continue

        post_url = _profile_meta(article, 'url')
        content = _profile_meta(article, 'text')
        if (
            not post_url
            or not content
            or content.startswith('RT @')
            or not is_ai_relevant(content)
            or post_url in seen
        ):
            continue
        seen.add(post_url)
        author_name = _profile_meta(article, 'name') or username
        posts.append({
            'username': username,
            'displayname': author_name,
            'content': content,
            'date': published.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M'),
            'url': post_url,
            # The public semantic card does not expose reliable like counts;
            # primary GraphQL results retain exact engagement values.
            'likes': 0,
            'retweets': 0,
        })

    posts.sort(key=lambda item: item['date'], reverse=True)
    return posts


async def main():
    try:
        auth_token, ct0 = load_creds()
    except Exception as error:
        print(f'[FAIL] X.com credentials: {describe_error(error)}', file=sys.stderr)
        sys.stdout.buffer.write(json.dumps({'error': str(error)}).encode('utf-8'))
        sys.stdout.buffer.write(b'\n')
        return 2

    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).date()
    yesterday = today - timedelta(days=1)

    results = []
    successful_accounts = 0
    failed_accounts = []

    # An isolated DB prevents stale cookies or locks from a previous run from
    # hiding a freshly supplied session cookie.
    with tempfile.TemporaryDirectory(prefix='ai-daily-x-') as temp_dir:
        api = API(
            pool=str(Path(temp_dir) / 'accounts.db'),
            proxy=PROXY_URL,
            raise_when_no_account=True,
            wait_timeout=30,
            wait_interval=1,
        )
        try:
            await api.pool.add_account_cookies(
                'ai_daily_session',
                f'auth_token={auth_token}; ct0={ct0}',
            )
        except Exception as error:
            print(f'[FAIL] X.com session setup: {describe_error(error)}', file=sys.stderr)
            sys.stdout.buffer.write(b'[]\n')
            return 2

        for username in X_ACCOUNTS:
            try:
                user = await api.user_by_login(username)
                if not user:
                    raise RuntimeError('profile lookup returned no user')

                tweets = await gather(api.user_tweets(user.id, limit=10))
                successful_accounts += 1
                for tweet in tweets:
                    tweet_date = tweet.date.astimezone(beijing_tz).date()
                    if tweet_date not in (today, yesterday):
                        continue
                    if tweet.rawContent.startswith('RT @'):
                        continue
                    if not is_ai_relevant(tweet.rawContent):
                        continue
                    results.append({
                        'username': username,
                        'displayname': user.displayname,
                        'content': tweet.rawContent,
                        'date': tweet.date.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M'),
                        'url': f'https://x.com/{username}/status/{tweet.id}',
                        'likes': tweet.likeCount,
                        'retweets': tweet.retweetCount,
                    })
            except Exception as api_error:
                # A single authenticated session can hit X's UserTweets rate
                # limit before all monitored accounts are visited. The public
                # profile page is a verified, lower-privilege fallback.
                try:
                    fallback_posts = fetch_public_profile(
                        username, today, yesterday, beijing_tz
                    )
                    results.extend(fallback_posts)
                    successful_accounts += 1
                    print(
                        f'[OK] X.com @{username} ({len(fallback_posts)} posts; '
                        f'HTML fallback after {describe_error(api_error)})',
                        file=sys.stderr,
                    )
                except Exception as html_error:
                    failed_accounts.append(username)
                    print(
                        f'[WARN] X.com @{username}: API {describe_error(api_error)}; '
                        f'HTML fallback {describe_error(html_error)}',
                        file=sys.stderr,
                    )

    results.sort(key=lambda item: item.get('likes', 0) + item.get('retweets', 0) * 3, reverse=True)
    sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

    if successful_accounts == 0:
        print(
            f'[FAIL] X.com: all {len(X_ACCOUNTS)} account lookups failed',
            file=sys.stderr,
        )
        return 2
    if failed_accounts:
        print(
            f'[WARN] X.com: {len(failed_accounts)}/{len(X_ACCOUNTS)} accounts failed; '
            f'{successful_accounts} succeeded',
            file=sys.stderr,
        )
    else:
        print(
            f'[OK] X.com ({len(results)} posts; '
            f'{successful_accounts}/{len(X_ACCOUNTS)} accounts succeeded)',
            file=sys.stderr,
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
