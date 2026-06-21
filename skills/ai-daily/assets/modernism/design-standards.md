# Modernism — Design Standards

References: https://monocle.com/
Design inspiration: Monocle magazine editorial layout. Final template adapts the Monocle aesthetic with deliberate changes — all colors collapsed to pure black, 2-column X.com grid, simplified section labels.

## Philosophy
Maximum editorial restraint. Pure white page, pure black for all text and borders — no grays, no intermediate tones. EB Garamond for all editorial content; Helvetica Neue for all structural elements. Red accent used only on category tags, active nav, and CTA links. Nothing decorates — everything informs.

---

## Color Palette

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#ffffff` | Pure white page background |
| `--bg-warm` | `#fdfcf3` | Defined but not used in current layout |
| `--bg-subtle` | `#f9f9f9` | Utility bar background (top strip) |
| `--text` | `#000000` | Primary text — all headlines, body, handles |
| `--muted` | `#000000` | Secondary text — same as text (no visual distinction) |
| `--tertiary` | `#000000` | Dates, tertiary labels — same as text |
| `--border` | `#000000` | All lines, rules, dividers — pure black hairlines |
| `--accent` | `#e10912` | Red — category tags, active/hover nav, CTA links |

**Key design decision:** Unlike Monocle's original gray hierarchy (`#6e6e6e` muted, `#e7e7e7` border), this template uses pure black (`#000`) for all text and borders. This creates a sharper, higher-contrast appearance.

`--accent` (#e10912) used on: hero tags, stack tags, card tags, active nav links, hover nav links, lang button active/hover, CTA links ("Read More →", "Watch →", "View post →"). Nowhere else.

---

## Typography

### Font Families
- **Editorial (headlines + body):** `'EB Garamond', Georgia, serif`
  - Google Fonts: EB Garamond weights 400, 500, 600, 700, italic 400
- **Utility (masthead + nav + labels + meta):** `'Helvetica Neue', Arial, sans-serif`
  - System font — no Google Fonts load needed

### Google Fonts Load
```html
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
```

### Type Scale
| Element | Family | Size | Weight | Notes |
|---|---|---|---|---|
| Masthead eyebrow "Daily Intelligence" | Helvetica Neue | 10px | 400 | uppercase, ls 0.22em |
| Masthead name "AI Daily" (rendered uppercase) | EB Garamond | clamp(80px, 8vw, 112px) | 500 | uppercase via CSS, ls 0.04em, shrinks to clamp(28px, 3vw, 36px) on scroll |
| Masthead date | Helvetica Neue | 11px | 300 | right-aligned, line-height 1.6 |
| Nav section links | Helvetica Neue | 11px | 400 | uppercase, ls 0.10em |
| Nav separators " \| " | Helvetica Neue | 11px | 400 | color: `--border` (#000) |
| Lang buttons (EN / 中文) | Helvetica Neue | 11px | 400 | ls 0.06em |
| Section name | EB Garamond | 28px | 600 | uppercase, ls 0.04em, line-height 1.1 |
| Section sort label | Helvetica Neue | 10px | 400 | ls 0.04em |
| Hero category tag | Helvetica Neue | 10px | 400 | uppercase, ls 0.10em, color accent |
| Hero title | EB Garamond | 34px | 500 | line-height 1.16, ls -0.01em |
| Hero summary | EB Garamond | 15px | 400 | italic, line-height 1.55 |
| Hero byline | Helvetica Neue | 11px | 400 | ls 0.02em |
| CTA "Read More →" / "Watch →" | Helvetica Neue | 10px | 700 | uppercase, ls 0.10em |
| Stack tag | Helvetica Neue | 10px | 400 | uppercase, ls 0.10em, color accent |
| Stack title | EB Garamond | 17px | 500 | line-height 1.3 |
| Stack byline | Helvetica Neue | 10px | 400 | ls 0.02em |
| Card tag | Helvetica Neue | 10px | 400 | uppercase, ls 0.10em, color accent |
| Card title | EB Garamond | 17px | 400 | line-height 1.3 |
| Card summary | EB Garamond | 13px | 400 | line-height 1.5 |
| Card byline | Helvetica Neue | 10px | 400 | ls 0.02em |
| X.com handle | Helvetica Neue | 12px | 600 | — |
| X.com date | Helvetica Neue | 11px | 300 | — |
| X.com body | EB Garamond | 15px | 400 | line-height 1.6 |
| X.com stats | Helvetica Neue | 11px | 300 | — |
| X.com "View post →" | Helvetica Neue | 10px | 700 | uppercase, ls 0.08em |
| Footer brand | Helvetica Neue | 12px | 400 | uppercase, ls 0.08em |
| Footer credit | Helvetica Neue | 11px | 300 | — |

---

## Layout

- **Max-width:** 1280px, centered
- **Side padding:** 40px desktop
- **Spotlight:** 3fr left (sticky article + hero-grid) + 2fr right (stack list), gap 40px
- **YouTube Picks:** centered banner image (55% width) above 4-column card grid
- **Card grid:** 4 columns, column-gap 24px, row-gap 0 (rows separated by border-top on each card)
- **X.com feed:** 2-column grid, column-gap 40px

---

## Spacing

| Context | Value |
|---|---|
| Section vertical padding | 40px top + 48px bottom |
| Section label margin-bottom | 24px |
| Section label padding-bottom | 10px (above 1px border) |
| Hero grid gap | 40px |
| Hero image height | 420px, object-fit cover |
| Hero caption padding | 16px 0 0 |
| Hero tag margin-bottom | 10px |
| Hero title margin-bottom | 12px |
| Hero summary margin-bottom | 12px |
| Hero byline margin-bottom | 8px |
| Stack item padding | 16px top + bottom (first: padding-top 0) |
| Stack tag margin-bottom | 6px |
| Stack title margin-bottom | 6px |
| YouTube banner image width | 55%, centered, margin-bottom 28px |
| Card padding | 16px top + bottom |
| Card tag margin-bottom | 7px |
| Card title margin-bottom | 8px |
| Card summary margin-bottom | 8px |
| Card byline margin-bottom | 6px |
| X.com row padding | 20px top + bottom (first two rows: padding-top 0) |
| X.com handle→body gap | 10px (margin-bottom on x-top) |
| X.com body margin-bottom | 12px |

---

## Borders

- **Utility bar bottom:** 1px solid `#000`
- **Masthead top:** 1px solid `#000`
- **Masthead bottom:** 1px solid `#000`
- **Nav bar bottom:** 1px solid `#000`
- **Section label bottom:** 1px solid `#000` (padding-bottom 10px)
- **Section bottom:** 1px solid `#000` (last section has none)
- **Stack items bottom:** 1px solid `#000` (last item has none)
- **Card top:** 1px solid `#000` (separates rows; row-gap is 0)
- **X.com rows bottom:** 1px solid `#000` (last row has none)
- **Footer top:** 1px solid `#000`
- **Border-radius:** 0 everywhere
- **No box-shadows, no gradients**

Note: There are NO card borders on article cards — only a border-top on each card acts as a row separator. Cards have no box, no background.

---

## Components

### Utility Bar
- `#f9f9f9` background, 1px `#000` bottom border, height 30px
- Currently empty (reserved for date/edition info)

### Masthead (scrolling shrink behavior)
- White background, 1px `#000` top + bottom borders
- 3-column grid: left (eyebrow), center (name), right (date)
- Name centered: EB Garamond clamp(80px–112px) 500 uppercase ls 0.04em
- On scroll (`.scrolled`): name shrinks to clamp(28px–36px); padding reduces from 20px to 8px
- Transition: 0.3s ease on font-size and padding

### Navigation
- Flex row: section links left (pipe-separated) + lang buttons right
- Section links: Helvetica Neue 11px 400 uppercase ls 0.10em; active/hover = accent red
- Pipe separators: color `#000`, not decorative
- Lang buttons: Helvetica Neue 11px 400; active/hover = accent red
- No box, no background — links only
- Height 40px, 1px `#000` bottom border

### Section Label
```
SECTION NAME ──────────────────────── (optional sort label)
(1px #000 hairline below, padding-bottom 10px)
```
- No dot, no "SEE ALL" link
- Name: EB Garamond 28px 600 uppercase ls 0.04em
- Rule: flex-1 spacer (no visible element — border is on the container)
- Sort label far right: Helvetica Neue 10px 400

### Spotlight Hero (left, sticky)
- Position: sticky top 120px while right stack scrolls
- Image: full-width, 420px height, object-fit cover, display block
- Caption below image (no background color — transparent/white):
  - Tag: Helvetica Neue 10px 400 uppercase accent red
  - Title: EB Garamond 34px 500
  - Summary: EB Garamond 15px italic
  - Byline: Helvetica Neue 11px 400
  - CTA: Helvetica Neue 10px 700 uppercase

### Spotlight Stack (right)
- Vertical list of articles, no images
- Each item: 16px padding top + bottom, 1px `#000` bottom border
- Tag: Helvetica Neue 10px 400 uppercase accent red
- Title: EB Garamond 17px 500
- Byline: Helvetica Neue 10px 400
- CTA: Helvetica Neue 10px 700 uppercase

### YouTube Picks
- Banner image (youtubepicks.png): 55% width, centered, margin-bottom 28px
- 4-column card grid below; row-gap 0, each card has 1px `#000` border-top
- Card: tag (accent) → title (EB Garamond 17px) → summary (13px) → byline → CTA
- No card border-box, no background

### X.com Feed
- 2-column grid, column-gap 40px
- Each row: handle + date on top row (space-between), then body, then footer (stats + CTA)
- Handle: Helvetica Neue 12px 600
- Date: Helvetica Neue 11px 300
- Body: EB Garamond 15px 400 line-height 1.6
- Stats: Helvetica Neue 11px 300
- "View post →": Helvetica Neue 10px 700 uppercase accent red
- 1px `#000` bottom border per row (last row: none)
- First two rows: padding-top 0

### Footer
- 1px `#000` top border
- Flex row: brand left (Helvetica Neue 12px 400 uppercase ls 0.08em) + credit right (Helvetica Neue 11px 300)
- Padding: 20px 0

---

## Rules
- Border-radius: 0 everywhere
- No shadows, no gradients
- All text and borders are pure black `#000` — no grays
- `--accent` (#e10912) used only on: category tags, stack tags, card tags, active/hover nav, lang button active/hover, CTA links
- Never use accent on backgrounds, borders, or section fills
- EB Garamond for all editorial content (headlines, summaries, body text, X.com posts)
- Helvetica Neue for all structure (masthead eyebrow, nav, labels, meta, bylines, CTA, footer)
- `--bg-warm` (#fdfcf3) is defined but NOT used in the current layout — do not apply it to hero captions
- Masthead name is EB Garamond rendered uppercase via CSS — it should feel editorial and large, not mechanical
- The masthead shrinks on scroll: this is a JS behavior triggered by `.scrolled` class on `.site-header`
