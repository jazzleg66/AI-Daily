# Rationalist — Design Standards

Reference: https://worksinprogress.co/
Design inspiration: Works in Progress editorial style. Final template adapts the WIP aesthetic with deliberate changes — darker contrast, monospace masthead, restructured layout.

## Philosophy
Academic-editorial with high contrast. Near-black lines and text on warm off-white background. Monospace type for all structural elements (masthead, nav, labels, meta); serif for all editorial content. Section identity expressed through four accent colors. No shadows, no gradients, no border-radius.

---

## Color Palette

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#fff7f4` | Page background (warm off-white) |
| `--text` | `#121212` | Primary text — all headlines and body |
| `--muted` | `#121212` | Same as text; nav bar overrides to `#888880` locally |
| `--border` | `#1d1d1d` | All lines and rules — near-black, not gray |
| `--line` | `#1d1d1d` | Same as border; used for card borders |
| `--brown` | `#121212` | Article summaries |

### Section Accent Colors
| Section | Primary | Dark variant | Text on Primary |
|---|---|---|---|
| Spotlight (Official/News) | `#363b8f` (blue) | — | `#fff7f4` |
| YouTube Picks | `#f4d06f` (gold) | `#4c3906` (gold-dark) | `#4c3906` |
| X.com Posts | `#cee0dc` (sage) | `#073429` (sage-dark) | `#073429` |

Note: Red `#e20a39` is defined but not used in the current layout.

### Nav Bar Exception
Nav bar locally overrides `--muted` to `#888880` for label text only. All borders remain `#1d1d1d`.

---

## Typography

### Font Families
- **Serif (headlines + body):** `'Spectral', 'Songti SC', Georgia, serif`
  - Google Fonts: `Spectral` weights 400, 600, italic 400
- **Mono (masthead + nav + labels + meta):** `'GT America Mono', 'GT America Mono Light', 'JetBrains Mono', 'Courier New', monospace`
  - Primary: GT America Mono Light (commercial, system font — not loaded via Google Fonts)
  - Fallback: JetBrains Mono (Google Fonts: weights 300, 500)

### Google Fonts Load
```html
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@300;500&display=swap" rel="stylesheet">
```

### Type Scale
| Element | Family | Size | Weight | Notes |
|---|---|---|---|---|
| Masthead eyebrow "Daily Intelligence" | Mono | 10px | 300 | uppercase, ls 0.14em |
| Masthead name "AI Daily" | GT America Mono Light / Mono | 28px | 300 | ls 0.04em, line-height 1 |
| Masthead date | Mono | 12px | 300 | right-aligned, line-height 1.6 |
| Nav section toggles | Mono | 11px | 400 (active: 500) | ls 0.04em |
| Lang tabs (English / 中文) | Mono | 11px | 500 | ls 0.04em |
| Section label | Mono | 13px | 500 | uppercase, ls 0.10em |
| Section count text | Mono | 10px | 400 | — |
| Hero title | Spectral | 28px | 700 | line-height 1.16, ls -0.01em |
| Hero byline | Mono | 11px | 400 | bold on source name |
| Hero summary | Spectral | 14px | 400 | line-height 1.55 |
| Hero CTA "Read more →" | Spectral | 13px | 700 | right-aligned |
| Hero footer tag | Mono | 10.5px | 400 | ls 0.02em, padding 7px 14px |
| Card title | Spectral | 18px | 700 | line-height 1.16, ls -0.01em |
| Card byline | Mono | 10.5px | 400 | bold on source name |
| Card summary | Spectral | 12.5px | 400 | line-height 1.5 |
| Card CTA "Read more →" | Spectral | 12.5px | 700 | right-aligned |
| Card footer tag | Mono | 10px | 400 | ls 0.02em |
| X.com handle | Mono | 12px | 500 | color: sage-dark `#073429` |
| X.com stats | Mono | 11px | 300 | — |
| X.com body | Spectral | 13.5px | 400 | line-height 1.58 |
| X.com link "View post →" | Mono | 11px | 300 | color: sage-dark `#073429` |
| Footer brand | Spectral | 14px | 600 | — |
| Footer credit | Mono | 11px | 300 | — |

---

## Layout

- **Max-width:** 1120px, centered
- **Side padding:** 40px desktop
- **Content grid (Spotlight + YouTube):** 3fr left (sticky hero) + 2fr right (2-col card grid), gap 24px
- **Card grid (right side):** 2 columns, gap 16px
- **X.com feed:** single column vertical feed, full width

---

## Spacing

| Context | Value |
|---|---|
| Section vertical padding | 40px top + bottom |
| Section bottom border | 1px `#1d1d1d` (removed on last section) |
| Panel top padding | 36px |
| Panel bottom padding | 56px |
| Section label margin-bottom | 20px |
| Hero image height | 280px, object-fit cover |
| Hero caption padding | 24px 28px 22px |
| Hero → footer tag padding | 7px 14px |
| Card body padding | 18px 18px 16px |
| Card min-height | 150px |
| X.com row padding | 18px top + bottom (first row: padding-top 0) |
| X.com row gap (meta ↔ content) | 28px |
| X.com meta column width | 200px fixed |

---

## Borders

- **Masthead top:** 3px solid `#121212`
- **Masthead bottom:** 1px solid `#1d1d1d`
- **Nav bar bottom:** 1px solid `#1d1d1d`
- **Nav section toggle right borders:** 1px solid `#1d1d1d` (between items)
- **Lang tab left border:** 1px solid `#1d1d1d`
- **Section rule (`.sec-rule`):** 1px solid `#1d1d1d`, flex: 1
- **Section bottom:** 1px solid `#1d1d1d` (last section has none)
- **Hero card:** 1px solid `#1d1d1d` all sides
- **Hero image bottom:** 1px solid `#1d1d1d`
- **Hero caption → footer divider:** 1px `rgba(255,247,244,0.28)` (blue hero) / `rgba(76,57,6,0.28)` (gold hero)
- **Article cards:** 1px solid `#1d1d1d` all sides
- **Card footer top:** 1px solid `#1d1d1d`
- **Card footer source/date divider:** 1px solid `#1d1d1d` right
- **X.com row bottom:** 1px solid `#1d1d1d` (last row has none)
- **Footer top:** 3px solid `#121212` (mirrors masthead)
- **Border-radius:** 0 everywhere

---

## Components

### Masthead
- 3px solid `#121212` top border
- Background: `#fff7f4`
- Flex row: left side (eyebrow + name), right side (date)
- Eyebrow "Daily Intelligence": Mono 10px 300 uppercase ls 0.14em
- Name "AI Daily": GT America Mono Light 28px 300, ls 0.04em
- Date: Mono 12px 300, right-aligned, line-height 1.6
- Padding: 16px 0 14px
- 1px `#1d1d1d` bottom rule (separate `<hr>`)

### Navigation
- Flex row: section toggles left + lang tabs right
- Section toggles: Mono 11px, padding 10px 16px, 1px `#1d1d1d` right border between items
- Active toggle: weight 500, `--text` color
- Hover: gold `#f4d06f` background
- Lang tabs: Mono 11px 500, 1px `#1d1d1d` left border, gold hover
- 1px `#1d1d1d` bottom border on nav bar

### Section Label
```
[■ 8×8px dot] SECTION NAME ──────────────────── count text
```
- Square dot: 8×8px, section accent color, no radius
- Label: Mono 13px 500 uppercase ls 0.10em, color `--muted` (nav-bar grey)
- Rule: 1px `#1d1d1d` flex line to the right
- Count text far right: Mono 10px
- Margin-bottom 20px

### Hero Card (Spotlight = blue `.h-lt`, YouTube = gold `.h-dk`)
- Full bordered box: 1px `#1d1d1d`
- Image: 280px height, object-fit cover, 1px border-bottom
- Caption: solid color background (blue `#363b8f` or gold `#f4d06f`)
- Title: Spectral 28px 700, color `#fff7f4` (blue) / `#4c3906` (gold)
- Byline: Mono 11px, muted color
- Summary: Spectral 14px 400, muted color
- CTA: Spectral 13px 700, right-aligned
- Footer strip: same background as caption, 1px semi-transparent top border; date tag on left

### Article Cards (right grid)
- Full bordered box: 1px `#1d1d1d`
- Body: padding 18px 18px 16px; min-height 150px
- Title: Spectral 18px 700
- Byline: Mono 10.5px
- Summary: Spectral 12.5px italic
- CTA: Spectral 12.5px 700, right-aligned, margin-top auto
- Footer: 1px `#1d1d1d` top; source tag left (Mono 10px) + date area right

### X.com Feed
- 1-column vertical flex layout
- Each row: 200px meta column (handle + stats) + flex-1 content column, gap 28px
- Handle: Mono 12px 500, color sage-dark `#073429`
- Stats (❤ likes · date): Mono 11px 300
- Body: Spectral 13.5px 400 line-height 1.58
- Link "View post →": Mono 11px 300, color sage-dark `#073429`, margin-top 7px
- 1px `#1d1d1d` bottom border per row (last row: none)

### Footer
- 3px solid `#121212` top border
- Flex row: brand left (Spectral 14px 600) + credit right (Mono 11px 300)
- Padding: 20px 0

---

## Rules
- Border-radius: 0 everywhere
- No box-shadows, no gradients
- All lines are `#1d1d1d` (near-black) — never gray
- Masthead and footer use 3px top border to bookend the page
- Section colors: Spotlight = blue, YouTube = gold, X.com = sage; never swap
- Hero caption background is the section's primary color; text inverts accordingly
- GT America Mono Light is the masthead font; JetBrains Mono is the fallback — do NOT substitute Spectral here
- Spectral is for all editorial content only; never use it for labels, nav, or meta
