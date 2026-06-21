#!/usr/bin/env python3
"""Fetch today's X.com posts from AI accounts via twscrape.
Credentials are read from C:\\Users\\Alex\\.claude\\private\\x-creds.json
or from X_AUTH_TOKEN / X_CT0 environment variables.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta

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

def is_ai_relevant(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in AI_KEYWORDS)

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
        except Exception:
            continue

    results.sort(key=lambda x: x.get('likes', 0) + x.get('retweets', 0) * 3, reverse=True)
    sys.stdout.buffer.write(json.dumps(results, ensure_ascii=False).encode('utf-8'))
    sys.stdout.buffer.write(b'\n')

asyncio.run(main())
