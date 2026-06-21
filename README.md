# AI Daily

A Claude Code skill that fetches today's AI news from multiple sources and generates a bilingual (English + Chinese) HTML newspaper — in two design styles.

Built as a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills) so it runs directly inside your AI assistant workflow.

---

## What it does

Every day, run one command in Claude Code:

> "today's daily brief" / "今天的 AI 日报"

Claude will:
1. Fetch today's AI news from Anthropic, OpenAI, Claude Blog, The AI Valley, smol.ai, Every.to newsletters
2. Pull the latest videos from 10 AI YouTube channels
3. Scrape top posts from 18 AI accounts on X.com (filtered for AI relevance)
4. Save a bilingual Markdown digest
5. Ask if you want an HTML newspaper — in **Rationalist** or **Modernism** style (or both)

---

## Design styles

### Rationalist
Inspired by [Works in Progress](https://worksinprogress.co/) — academic editorial feel, serif + monospace fonts, warm off-white background, sticky hero image, bilingual toggle.

![Rationalist style](screenshots/rationalist-preview.jpeg)

### Modernism
Inspired by [Monocle](https://monocle.com/) — minimal black and white, large EB Garamond masthead that shrinks on scroll, 4-column YouTube card grid, 2-column X.com feed, bilingual toggle.

![Modernism style](screenshots/modernism-preview.jpeg)

---

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (the CLI)
- Python 3.9+
- [twscrape](https://github.com/vladkens/twscrape) for X.com scraping:
  ```bash
  pip install "twscrape[curl]"
  ```
- An X.com account with valid session cookies (`auth_token` + `ct0`)

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/jazzleg66/AI-Daily.git
```

Place it anywhere — Claude Code will detect the skill's base directory automatically. The `output/` folder is pre-created with all required images inside.

**2. Configure X.com credentials**

Create the credentials file:
```bash
mkdir -p ~/.claude/private
```

```json
// ~/.claude/private/x-creds.json
{
  "auth_token": "your_auth_token_here",
  "ct0": "your_ct0_here"
}
```

To get your cookies: log into x.com in a browser, open DevTools → Application → Cookies → copy `auth_token` and `ct0`.

**3. Register the skill in Claude Code**

Add this to your `.claude/settings.json`:
```json
{
  "skills": [
    { "path": "path/to/ai-daily/SKILL.md" }
  ]
}
```

---

## Usage

In Claude Code, just say:

```
today's daily brief
```

or

```
今天的 AI 日报
```

Claude will run the fetch scripts, show you a summary, save a Markdown file, and ask if you want the HTML newspaper.

### Customise your sources

- **News:** Edit `fetch_news.py` to add or remove sites
- **YouTube channels:** Edit `CHANNELS` in `fetch_youtube.py`
- **X.com accounts:** Edit `X_ACCOUNTS` in `fetch_x.py`
- **AI keyword filter:** Edit `AI_KEYWORDS` in `fetch_x.py` to tune what counts as AI-relevant

---

## File structure

```
ai-daily/
├── SKILL.md                        # Skill definition — Claude reads this
├── scripts/
│   ├── fetch_news.py               # Fetches Anthropic, OpenAI, blogs, newsletters
│   ├── fetch_youtube.py            # Fetches AI YouTube channels via RSS
│   └── fetch_x.py                  # Fetches X.com posts via twscrape
├── assets/
│   ├── rationalist/
│   │   ├── template.html           # Rationalist HTML template
│   │   ├── spotlight.jpg           # Hero image (Spotlight section)
│   │   └── youtubepicks.jpg        # Hero image (YouTube section)
│   └── modernism/
│       ├── template.html           # Modernism HTML template
│       ├── spotlight.png           # Hero image (Spotlight section)
│       └── youtubepicks.png        # Hero image (YouTube section)
└── resources.md                    # Source list
```

---

## Design credits

- **Modernism style** — layout and typography inspired by [Monocle](https://monocle.com/)
- **Rationalist style** — layout and typography inspired by [Works in Progress](https://worksinprogress.co/)

---

## License

MIT
