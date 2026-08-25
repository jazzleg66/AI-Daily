# AI Daily — Source List

## News Sources (fetch_news.py)
- https://www.anthropic.com/ (sitemap-based date detection)
- https://www.anthropic.com/blog (Claude Blog, JSON-LD date detection)
- https://openai.com/ (RSS)
- https://www.theaivalley.com/ (RSS + Beehiiv homepage-card fallback)
- https://news.smol.ai/ (RSS)
- https://every.to/ (posts sitemap + article metadata; legacy newsletter RSS fallback)

## YouTube Channels (fetch_youtube.py)
Configured inside the script — edit `CHANNELS` to add or remove channels.

## X.com Accounts (fetch_x.py)
Configured inside the script — edit `X_ACCOUNTS` to track your preferred AI accounts.
The fetcher uses twscrape first and verified public profile HTML as a
rate-limit fallback.
