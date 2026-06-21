# Style C — Works in Progress Design Standards

Reference: https://worksinprogress.co/
CSS source: https://worksinprogress.co/_astro/Layout.CZZSTtxS.css

## Philosophy
Academic-editorial. Color is category-coded — four section colors map to the site's four editorial pillars. Warm off-white background, not pure white. Custom serif + mono type stack. No shadows, no gradients, no border-radius. Every element earns its place.

---

## Color Palette (extracted from live CSS)

### Base
| Token | Hex | Role |
|---|---|---|
| `--bg` | `#fff7f4` | Page background (warm off-white) |
| `--text-primary` | `#121212` | Headlines, primary copy |
| `--text-on-dark` | `#fff7f4` | Text on dark accent backgrounds |
| `--border` | `#e0dbd8` | Dividers, rules (warm gray) |

### Section Accent Colors (direct from WIP category system)
| Section | Primary | Alt/Light | Text on Primary |
|---|---|---|---|
| Official Updates (Science) | `#363b8f` | `#d8d9f1` | `#fff7f4` |
| Independent News (Economics) | `#e20a39` | `#f8e6ea` | `#fff7f4` |
| YouTube Picks (Politics) | `#f4d06f` | `#4c3906` | `#4c3906` |
| X.com Posts (Culture) | `#cee0dc` | `#073429` | `#073429` |

### CSS Custom Properties
```css
--color--science:      #363b8f;
--color--science-alt:  #d8d9f1;
--color--economics:    #e20a39;
--color--economics-alt:#f8e6ea;
--color--culture:      #cee0dc;
--color--culture-alt:  #073429;
--color--politics:     #f4d06f;
--color--politics-alt: #4c3906;
```

---

## Typography (extracted from live CSS)

### Font Families (actual site fonts)
- **Serif (headlines/body):** `Editor-Regular`, `Editor-Bold`, `Editor-Italic` — Colophon foundry custom serif
- **Mono (labels/nav/meta):** `GT America Mono Light`, `GT America Mono Bold`

### Google Fonts substitutes (for self-contained HTML)
- **Serif:** `Spectral` (weights 400, 600, italic 400) — closest Google Fonts match to Editor
- **Mono:** `JetBrains Mono` (weights 300, 500) — close stand-in for GT America Mono

### Type Scale (inferred from visual reference + CSS)
| Element | Family | Size | Weight | Line-height | Notes |
|---|---|---|---|---|---|
| Publication name | Serif | 32px | 600 | 1.0 | letter-spacing: -0.01em |
| Pub eyebrow | Mono | 10px | 300 | 1.0 | uppercase, ls: 0.14em |
| Section label | Mono | 11px | 500 | 1.0 | uppercase, ls: 0.10em |
| Insight number | Mono | 11px | 300 | 1.0 | uppercase, ls: 0.08em |
| Insight title | Serif | 20px | 600 | 1.25 | — |
| Insight body | Serif | 15px | 400 | 1.70 | italic available |
| Article title | Serif | 16px | 400 | 1.35 | — |
| Article summary | Serif | 13px | 400 | 1.60 | italic |
| Source tag | Mono | 10px | 500 | 1.0 | uppercase, ls: 0.10em |
| Article meta | Mono | 11px | 300 | 1.2 | — |
| Tab label | Mono | 12px | 500 | 1.0 | ls: 0.04em |
| X.com handle | Mono | 12px | 500 | 1.0 | — |
| X.com body | Serif | 13px | 400 | 1.55 | — |
| Footer | Mono | 11px | 300 | 1.0 | — |

---

## Spacing (from live CSS)

| Token | Value | Context |
|---|---|---|
| `--main-padding` | 16px mobile / 24px tablet / 40px desktop | Side padding |
| Card gap | 24px | Between grid cards |
| X.com card gap | 16px | Denser grid |
| Section vertical padding | 32px top + bottom | Between sections |
| Element inner gap | 8–14px | Tag → title → summary → meta |

---

## Grid

- Content max-width: 1120px, centered
- Side padding: 40px desktop (var --main-padding)
- Insights: 3 equal columns, gap 24px
- Official (3 items): 3 equal columns, gap 24px
- News (2 items): 2 equal columns, gap 24px
- YouTube (N items): 3 columns, gap 24px, auto row wrap
- X.com (N items): 3 columns, gap 16px, auto row wrap

---

## Components

### Masthead
- 3px solid `#121212` top border
- Background: `#fff7f4`
- Eyebrow mono text "Daily Intelligence" above pub name
- Pub name: Spectral 32px 600
- Date right-aligned: Mono 12px
- 1px `--border` bottom rule

### Language Tabs
- Mono 12px, letter-spacing 0.04em
- Active: `#121212` text + 2px solid `#121212` bottom border, margin-bottom -1px
- Inactive: muted (~`#999`), no border
- No background, no radius

### Section Label
- Square 8×8px dot in section primary color (no radius)
- Mono 11px uppercase ls 0.10em
- Flex horizontal rule extending right
- Optional count text far right

### Accent Blocks (image replacement)
- **Insight cards:** full width, height 120px, solid section primary color
- **Article cards:** full width, height 72px, solid section primary color, opacity 0.18

### Article Card
- 2px top border: `--border`
- Padding-top 14px, no card background
- Source tag: Mono 10px uppercase, section primary color
- Title: Spectral 16px 400, linked
- Summary: Spectral 13px 400 italic, secondary text
- Meta: Mono 11px 300, "Read →" / "Watch →" link

### Insight Card
- Order: accent block → number (mono) → title (serif 20px 600) → body (serif 15px italic)
- Numbers "01" "02" "03" in Mono 11px 300 uppercase muted

### X.com Card
- Background: section alt color (`#cee0dc` culture light)
- Left border: 3px solid `#073429` (culture dark)
- Handle: Mono 12px 500, culture dark
- Body: Serif 13px 400
- Footer row: date mono muted · "View post →"

### Footer
- 3px solid `#121212` top border (mirrors masthead)
- Brand: Spectral 14px 600 left
- Credit: Mono 11px 300 muted right

---

## Rules
- Border-radius: 0 everywhere
- No box-shadows
- No gradients (except shimmer loader, not used in digest)
- Section accent colors always paired with their section: Science/Official, Economics/News, Politics/YouTube, Culture/X.com
- Body copy uses Spectral (serif), not sans-serif — this is key to the WIP academic feel
- Links: inherit color, underline on hover only
