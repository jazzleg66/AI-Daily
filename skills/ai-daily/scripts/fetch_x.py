#!/usr/bin/env python3
"""Fetch today's X.com posts from AI accounts via twscrape.
Credentials are read from ~/.claude/private/x-creds.json
(%USERPROFILE%\\.claude\\private\\x-creds.json on Windows)
or from the X_AUTH_TOKEN / X_CT0 environment variables.
"""
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

# On Windows, curl-cffi ignores system proxy settings (Clash, V2Ray, etc.) stored
# in the registry. Read the registry and populate env vars before twscrape imports.
if sys.platform == 'win32' and not os.environ.get('HTTPS_PROXY'):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
        enabled, _ = winreg.QueryValueEx(key, 'ProxyEnable')
        if enabled:
            proxy, _ = winreg.QueryValueEx(key, 'ProxyServer')
            if proxy and '://' not in proxy:
                proxy = 'http://' + proxy
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            os.environ['ALL_PROXY'] = proxy
        winreg.CloseKey(key)
    except Exception:
        pass

# The curl backend needs curl-cffi, which only ships with twscrape[curl] — a plain
# `pip install twscrape` does not pull it in. Without it twscrape raises ImportError
# on the first account, marks that account locked, and every later call then waits
# forever for an account that can never unlock: no output, no error, no exit.
#
# Bail out here instead. Falling back to the default httpx backend is not a fix —
# X.com does not answer its requests and they hang with no timeout, which turns a
# missing dependency into the same silent deadlock.
try:
    import curl_cffi  # noqa: F401
except ImportError:
    print('[FATAL] curl-cffi is required but not installed. Without it this script '
          'hangs forever instead of failing. Install with:\n'
          '  pip install --upgrade "twscrape[curl] @ '
          'git+https://github.com/vladkens/twscrape.git"', file=sys.stderr)
    print('[]')
    sys.exit(1)

os.environ['TWS_HTTP_BACKEND'] = 'curl'

from twscrape import API, gather
from twscrape.logger import set_log_level
set_log_level('ERROR')

CREDS_FILE = os.path.join(os.path.expanduser('~'), '.claude', 'private', 'x-creds.json')

X_ACCOUNTS = [
    "GoogleLabs", "nickstpierre", "mattturck", "karpathy",
    "garrytan", "levie", "HamelHusain", "alexalbert__",
    "rauchg", "amasad", "george__mack", "mckaywrigley",
    "lennysan", "gregisenberg", "swyx", "kevinweil",
    "joshwoodward", "peteryang"
]

# Post must contain at least one of these keywords (case-insensitive) to be included.
#
# Short acronyms are matched as whole words only. Plain substring matching let 'ai'
# hit 'air' and 'Aisha', which pulled unrelated news and political posts into the
# results. A trailing 's' is allowed so 'llms' and 'apis' still match.
AI_ACRONYMS = ['ai', 'ml', 'llm', 'gpt', 'rag', 'api', 'saas']

# Matched from a word boundary but allowed to run on, so 'model' catches 'models',
# 'deploy' catches 'deployment', and 'fine-tun' catches 'fine-tuning'.
AI_STEMS = [
    'claude', 'gemini', 'openai', 'anthropic',
    'model', 'agent', 'prompt', 'token', 'inference', 'training', 'neural',
    'embedding', 'vector', 'fine-tun', 'transformer', 'diffusion',
    'multimodal', 'frontier', 'open weight', 'open-weight',
    'chatgpt', 'copilot', 'cursor', 'replit', 'automation',
    'machine learning', 'deep learning', 'foundation model', 'language model',
    'benchmark', 'eval', 'alignment', 'vibe cod', 'coding assistant',
    'startup', 'founder', 'product', 'software', 'developer',
    'open source', 'dataset', 'research', 'paper', 'deploy',
]

_ACRONYM_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(k) for k in AI_ACRONYMS) + r')s?\b', re.IGNORECASE)
_STEM_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(k) for k in AI_STEMS) + r')', re.IGNORECASE)

def is_ai_relevant(text: str) -> bool:
    return bool(_ACRONYM_RE.search(text) or _STEM_RE.search(text))

def load_creds():
    auth_token = os.environ.get('X_AUTH_TOKEN')
    ct0 = os.environ.get('X_CT0')
    if auth_token and ct0:
        return auth_token, ct0
    with open(CREDS_FILE, 'r') as f:
        creds = json.load(f)
    return creds['auth_token'], creds['ct0']

async def main():
    try:
        auth_token, ct0 = load_creds()
    except Exception as e:
        print(json.dumps({"error": f"Could not load credentials: {e}"}))
        sys.exit(1)

    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).date()
    yesterday = today - timedelta(days=1)

    api = API()
    await api.pool.add_account_cookies('morning_tea_account', f'auth_token={auth_token}; ct0={ct0}')

    results = []
    for username in X_ACCOUNTS:
        try:
            user = await api.user_by_login(username)
            if not user:
                continue
            tweets = await gather(api.user_tweets(user.id, limit=10))
            for tweet in tweets:
                tweet_date = tweet.date.astimezone(beijing_tz).date()
                if tweet_date in [today, yesterday]:
                    if tweet.rawContent.startswith('RT @'):
                        continue
                    if not is_ai_relevant(tweet.rawContent):
                        continue
                    results.append({
                        "username": username,
                        "displayname": user.displayname,
                        "content": tweet.rawContent,
                        "date": tweet.date.astimezone(beijing_tz).strftime('%Y-%m-%d %H:%M'),
                        "url": f"https://x.com/{username}/status/{tweet.id}",
                        "likes": tweet.likeCount,
                        "retweets": tweet.retweetCount
                    })
        except Exception as e:
            # Report and move on. Swallowing these silently made a missing
            # dependency look like a hang with no diagnostic output at all.
            print(f'[FAIL] {username}: {type(e).__name__}: {e}', file=sys.stderr)
            continue

    print(f'[OK] {len(results)} posts from {len(X_ACCOUNTS)} accounts', file=sys.stderr)
    results.sort(key=lambda x: x.get('likes', 0) + x.get('retweets', 0) * 3, reverse=True)
    sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

asyncio.run(main())
