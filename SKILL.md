---
name: ai-daily
description: Daily AI news briefing skill. Fetches today's content from independent news sites, YouTube AI channels, X.com AI accounts, and Anthropic/OpenAI/Claude official blogs. Outputs a bilingual (Chinese + English) Markdown digest. HTML newspaper layout is optional — ask the user after the Markdown is shown. Use when the user says "daily brief", "AI news", "today's brief", "每日简报", "AI日报", or asks for today's AI news.
---

# AI Daily — Daily AI Brief

## Purpose
Fetch and present today's AI news in a bilingual digest with a professional HTML newspaper layout.

## Paths
All paths below are relative to this skill's base directory, which Claude Code provides in the system context as "Base directory for this skill: ...". Use it to construct absolute paths for all bash commands.

- Scripts: `scripts/`
- Templates: `assets/rationalist/` and `assets/modernism/`
- Output: `output/` — pre-created; all 4 hero images already included

## Setup Requirements
- **X.com credentials:** `~/.claude/private/x-creds.json` (see README for details)
- **twscrape:** `pip install "twscrape[curl]"`
- **Output directory:** `output/` inside this skill's base directory (already exists in the repo)

## Trigger Phrases
- "daily brief" / "ai news" / "today's ai news"
- "每日简报" / "AI日报" / "今天的新闻"
- "fetch my daily brief"

---

## Workflow

### Step 1 — Calculate Dates
Beijing Time (UTC+8).

- **File name:** today's date (the run date). e.g. run on 2026-06-20 → `daily-brief-2026-06-20.md`
- **Content window:** yesterday (full 24 hours) + today up to the current run time. e.g. run at 10:00 AM on 6/20 → include all 6/19 content + any 6/20 content published before 10:00 AM Beijing time.

### Step 2 — Run All Fetch Scripts (parallel)

Run all three in one turn as parallel Bash calls. Replace `<BASE>` with the skill's base directory from context:

```bash
python "<BASE>/scripts/fetch_youtube.py"
```
```bash
python "<BASE>/scripts/fetch_x.py"
```
```bash
python "<BASE>/scripts/fetch_news.py"
```

Each script auto-retries failed requests up to 3 times (2s / 4s backoff) before giving up.

**Script outputs:**
- `fetch_youtube.py` → JSON array of videos from subscribed AI channels
- `fetch_x.py` → JSON array of posts sorted by engagement (takes 1-2 min)
- `fetch_news.py` → JSON array with `title, url, source, category, date, summary`; stderr shows `[OK]` / `[FAIL]` per source

**Date window (all scripts):** yesterday full day + today up to run time, Beijing time (UTC+8). 0 results is normal on weekends and slow news days.

### Step 3 — Verify Data Before Proceeding

After scripts finish, tally the counts:
- News articles: N
- YouTube videos: N
- X.com posts: N

**If all three return 0 AND `fetch_news.py` stderr shows `[FAIL]`:**
Stop. Tell the user all scripts failed (likely a network issue) and ask whether to retry. Re-run on confirmation.

**If X.com returns 0 AND YouTube returns 0 (both empty on a weekday):**
Ask the user to confirm before continuing.

**If at least one section has data:** proceed immediately.

### Step 4 — Save Markdown File & Ask About HTML

Save the full digest as a Markdown file to the `output/` directory:
`<BASE>/output/daily-brief-YYYY-MM-DD.md`

Then open it:
```bash
# Windows
start "<BASE>/output/daily-brief-YYYY-MM-DD.md"
# macOS
open "<BASE>/output/daily-brief-YYYY-MM-DD.md"
```

In chat, output only a brief confirmation: filename saved, total item counts per section, and 1-line summary of the top insight.

After that, ask:
> "要生成 HTML 报纸版式吗？（输入 Y 生成并打开）"

Only generate HTML if the user confirms. If yes, ask which style, then follow the HTML Generation section below.

---

## HTML Generation — Style Selection

When the user confirms HTML output, ask:

> 选择排版风格：
> - **Rationalist** — Works in Progress 风格：学术编辑风，衬线+等宽字体，米白背景，sticky hero 图片，双语切换
> - **Modernism** — Monocle 风格：极简黑白，EB Garamond 衬线，大号 masthead 滚动收缩，4列 YouTube 卡片，双列 X.com
>
> 输入风格名称（Rationalist / Modernism）：

---

## HTML Generation — Template-Based Workflow

**Do NOT generate HTML from scratch.** Always read the template for the chosen style, fill placeholders, expand REPEAT blocks, and save.

Images are already pre-placed in `output/` — no copying needed.

---

### Rationalist

**Template:** `<BASE>/assets/rationalist/template.html`

**Output file:** `<BASE>/output/r-brief-YYYY-MM-DD.html`

**Steps:**
1. Read `assets/rationalist/template.html`
2. Fill every `{{PLACEHOLDER}}` with today's content from the Markdown digest
3. For Spotlight and YouTube Picks: expand `<!-- REPEAT ... /REPEAT -->` blocks — one `.si` card per article/video beyond the hero
4. Save the filled HTML to `output/r-brief-YYYY-MM-DD.html`
5. Open the file:
```bash
# Windows
start "<BASE>/output/r-brief-YYYY-MM-DD.html"
# macOS
open "<BASE>/output/r-brief-YYYY-MM-DD.html"
```

**Layout notes:**
- Spotlight: sticky hero card (blue caption) left + 2-col card grid right
- YouTube Picks: sticky hero card (gold caption) left + 2-col card grid right
- X.com: 1-column vertical feed

**Placeholder Reference — Rationalist:**

| Placeholder | Value |
|---|---|
| `{{DATE_EN}}` | e.g. `June 20, 2026` |
| `{{OFFICIAL_COUNT}}` | number of Official Updates articles |
| `{{NEWS_COUNT}}` | number of Independent News articles |
| `{{SPOTLIGHT_HERO_URL}}` | URL of the top Spotlight article |
| `{{SPOTLIGHT_HERO_TITLE_EN}}` | English title of hero article |
| `{{SPOTLIGHT_HERO_TITLE_CN}}` | Chinese title of hero article |
| `{{SPOTLIGHT_HERO_SOURCE}}` | Source name (e.g. `Claude Blog`) |
| `{{SPOTLIGHT_HERO_SUMMARY_EN}}` | 1-2 sentence English summary |
| `{{SPOTLIGHT_HERO_SUMMARY_CN}}` | 1-2 sentence Chinese summary |
| `{{SPOTLIGHT_HERO_DATE}}` | Display date shared by both panels (e.g. `Jun 18, 2026`) |
| `{{SPOTLIGHT_1_URL}}` `{{SPOTLIGHT_1_TITLE_EN}}` `{{SPOTLIGHT_1_TITLE_CN}}` `{{SPOTLIGHT_1_SOURCE}}` `{{SPOTLIGHT_1_SUMMARY_EN}}` `{{SPOTLIGHT_1_SUMMARY_CN}}` `{{SPOTLIGHT_1_DATE}}` | Same fields for each additional Spotlight article (expand REPEAT block) |
| `{{YT_COUNT}}` | number of YouTube videos |
| `{{YT_HERO_URL}}` `{{YT_HERO_TITLE_EN}}` `{{YT_HERO_TITLE_CN}}` `{{YT_HERO_SOURCE}}` `{{YT_HERO_SUMMARY_EN}}` `{{YT_HERO_SUMMARY_CN}}` `{{YT_HERO_DATE}}` | Top YouTube video (the hero) |
| `{{YT_1_URL}}` `{{YT_1_TITLE_EN}}` `{{YT_1_TITLE_CN}}` `{{YT_1_SOURCE}}` `{{YT_1_SUMMARY_EN}}` `{{YT_1_SUMMARY_CN}}` `{{YT_1_DATE}}` | Each additional YouTube video (expand REPEAT block) |
| `{{X_COUNT}}` | number of X.com posts |
| `{{X_1_HANDLE}}` | e.g. `@swyx` |
| `{{X_1_LIKES}}` | e.g. `12,209` |
| `{{X_1_DATE}}` | e.g. `Jun 19` (shared by both panels) |
| `{{X_1_BODY_EN}}` | English post text |
| `{{X_1_BODY_CN}}` | Chinese translation of post |
| `{{X_1_URL}}` | Post URL |

---

### Modernism

**Template:** `<BASE>/assets/modernism/template.html`

**Output file:** `<BASE>/output/m-brief-YYYY-MM-DD.html`

**Steps:**
1. Read `assets/modernism/template.html`
2. Fill every `{{PLACEHOLDER}}` with today's content from the Markdown digest
3. For Spotlight stack: expand `<!-- REPEAT .stack-item /REPEAT -->` — one `.stack-item` per article beyond the hero (stack items have no summary, only tag + title + byline + CTA)
4. For YouTube Picks: expand `<!-- REPEAT .card /REPEAT -->` — one `.card` per video (all videos are cards; there is no separate hero video)
5. For X.com: expand `<!-- REPEAT .x-row /REPEAT -->` — one `.x-row` per post
6. Save the filled HTML to `output/m-brief-YYYY-MM-DD.html`
7. Open the file:
```bash
# Windows
start "<BASE>/output/m-brief-YYYY-MM-DD.html"
# macOS
open "<BASE>/output/m-brief-YYYY-MM-DD.html"
```

**Layout notes:**
- Masthead: large EB Garamond "AI Daily" that shrinks on scroll (JS-driven)
- Spotlight: sticky left article (hero-grid 3fr 2fr) + right stack of articles with no scroll limit
- YouTube Picks: banner image centered above, then 4-column card grid (all videos are equal cards — no separate hero)
- X.com: 2-column grid

**Empty Spotlight state (0 articles):** Keep the `hero-grid` structure — show `spotlight.png` with a "No articles today" message in place of article content. Do NOT remove the image. Pattern:
```html
<div class="hero-grid">
  <article>
    <img class="hero-img" src="spotlight.png" alt="Spotlight">
    <div class="hero-cap">
      <span class="hero-tag">Weekend</span>
      <h2 class="hero-title">No articles today</h2>
      <p class="hero-sum">Official updates and independent news published nothing in today's content window. All sources reachable — weekend publishing cycle.</p>
      <div class="hero-by">— · [DATE_EN]</div>
    </div>
  </article>
  <div class="hero-stack"></div>
</div>
```
Chinese panel: tag = `周末`, title = `今日无文章`, summary in Chinese, date in `YYYY年M月D日` format.

**Placeholder Reference — Modernism:**

| Placeholder | Value |
|---|---|
| `{{DATE_EN}}` | e.g. `June 20, 2026` |
| `{{SPOTLIGHT_HERO_TAG_EN}}` | English category tag for hero (e.g. `Official Update · Claude Blog`) |
| `{{SPOTLIGHT_HERO_TAG_CN}}` | Chinese category tag for hero |
| `{{SPOTLIGHT_HERO_URL}}` | URL of the top Spotlight article |
| `{{SPOTLIGHT_HERO_TITLE_EN}}` | English title |
| `{{SPOTLIGHT_HERO_TITLE_CN}}` | Chinese title |
| `{{SPOTLIGHT_HERO_SUMMARY_EN}}` | 1-2 sentence English summary (italic in layout) |
| `{{SPOTLIGHT_HERO_SUMMARY_CN}}` | 1-2 sentence Chinese summary |
| `{{SPOTLIGHT_HERO_SOURCE}}` | Source name |
| `{{SPOTLIGHT_HERO_DATE_EN}}` | English date (e.g. `June 18, 2026`) |
| `{{SPOTLIGHT_HERO_DATE_CN}}` | Chinese date (e.g. `2026年6月18日`) |
| `{{SPOTLIGHT_1_TAG_EN}}` `{{SPOTLIGHT_1_TAG_CN}}` `{{SPOTLIGHT_1_URL}}` `{{SPOTLIGHT_1_TITLE_EN}}` `{{SPOTLIGHT_1_TITLE_CN}}` `{{SPOTLIGHT_1_SOURCE}}` `{{SPOTLIGHT_1_DATE_EN}}` `{{SPOTLIGHT_1_DATE_CN}}` | Each additional Spotlight article (expand REPEAT block; no summary field) |
| `{{YT_COUNT}}` | number of YouTube videos |
| `{{YT_1_TAG_EN}}` `{{YT_1_TAG_CN}}` `{{YT_1_URL}}` `{{YT_1_TITLE_EN}}` `{{YT_1_TITLE_CN}}` `{{YT_1_SUMMARY_EN}}` `{{YT_1_SUMMARY_CN}}` `{{YT_1_SOURCE}}` `{{YT_1_DATE_EN}}` `{{YT_1_DATE_CN}}` | Each YouTube video card (expand REPEAT block; all videos including the first are cards) |
| `{{X_1_HANDLE}}` | e.g. `@swyx` |
| `{{X_1_DATE_EN}}` | English date (e.g. `Jun 19`) |
| `{{X_1_DATE_CN}}` | Chinese date (e.g. `6月19日`) |
| `{{X_1_BODY_EN}}` | English post text |
| `{{X_1_BODY_CN}}` | Chinese translation |
| `{{X_1_LIKES}}` | e.g. `12,209` |
| `{{X_1_URL}}` | Post URL |
| `{{SPOTLIGHT_COUNT}}` | Total Spotlight articles |
| `{{YT_COUNT}}` | Total YouTube videos |
| `{{X_COUNT}}` | Total X.com posts |

**Content selection rules (both styles):**
- Spotlight hero: pick the single most important article (Official Updates first, then top news)
- Rationalist YouTube hero: pick the most relevant or highest-quality video; remaining go to cards
- Modernism YouTube: no hero — all videos go into the card grid
- X.com posts: include all posts sorted by likes descending
- Both EN and CN panels share the same URLs and source names — only titles, summaries, tags, post bodies, and date formats differ by language

---

## Output Format (Markdown file — two separate language sections)

The file has two self-contained halves. Do NOT interleave Chinese and English line by line. A reader should be able to read one section start to finish in their language.

```
# AI Daily Brief — YYYY-MM-DD · 北京时间 / Beijing Time

---

# 中文版

## 官方动态 (N)
- **[中文标题]** — [来源] · [日期]
  [1句中文摘要]
  URL

## 独立新闻 (N)
- **[中文标题]** — [来源] · [日期]
  [1句中文摘要]
  URL

## YouTube 精选 (N)
- **[中文标题]** — [频道] · [日期]
  [1句中文摘要]
  URL

注意：中文版的官方动态、独立新闻、YouTube精选，标题必须是中文翻译，不保留英文原标题；链接只在摘要下方单独一行显示，标题不加超链接。

## X.com 热议 (N，按互动量排序)
- **[@username]** · ❤ [likes] · [日期]
  [推文内容的中文翻译，限100字以内]
  [URL]

---
*共收录：官方动态N条 · 独立新闻N条 · YouTube N条 · X.com N条*

---

# English Version

## Official Updates (N)
- **[Title]** — [Source] · [Date]
  [1-sentence English summary]
  URL

## Independent News (N)
- **[Title]** — [Source] · [Date]
  [1-sentence English summary]
  URL

## YouTube Picks (N)
- **[Title]** — [Channel] · [Date]
  [1-sentence English summary] · [URL]

## X.com Top Posts (N, sorted by engagement)
- **[@username]** · ❤ [likes] · [Date]
  [Original post content, truncated to 100 chars]
  [URL]

---
*Total: Official N · News N · YouTube N · X.com N*
```

---

## Security Note
Your X.com credentials are personal — never commit `x-creds.json` to any repo. The `.gitignore` in this repo already excludes it. Share only `SKILL.md` and the `scripts/` folder when distributing this skill.
