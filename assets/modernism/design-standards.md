# Modernism — Design Standards

References: https://monocle.com/
Source audit: Monocle theme CSS extracted June 2026 (frontend.css + inline custom properties)

## Philosophy
Pure editorial restraint. White page, hairline rules, Plantin-class old-style serif for all content, Helvetica Neue for all utility. Inspired by Monocle's actual production design: the masthead is a large, light-weight sans-serif wordmark centered on white; editorial text is Plantin (old-style serif, high contrast, bracketed serifs); structure is communicated through hairlines and tiny colored indicators. Nothing decorates — everything informs.

---

## Color Palette (extracted from monocle.com)

| Token | Hex | Monocle source variable | Role |
|---|---|---|---|
| `--bg` | `#ffffff` | `--color-neutral-50` | Pure white page background |
| `--bg-warm` | `#fdfcf3` | `--color-yellow-100` | Signature Monocle cream — hero captions, featured blocks |
| `--bg-subtle` | `#f9f9f9` | `--color-neutral-100` | Very light section tints |
| `--text` | `#000000` | `--color-neutral-900` | Primary text — all headlines and body |
| `--muted` | `#6e6e6e` | `--color-neutral-500` | Secondary text — bylines, meta, captions |
| `--tertiary` | `#b3b3b3` | `--color-neutral-300` | Dates, tertiary labels |
| `--border` | `#e7e7e7` | `--color-neutral-250` | Hairlines — all dividers, rules |
| `--divider` | `#d9d9d9` | `--color-neutral-200` | Heavier dividers, section separators |
| `--accent` | `#e10912` | `--color-salmon-500` | Monocle red — SEE ALL links, section dots, category tags |

Accent (`#e10912`) is used on: section dot indicators, category tags, SEE ALL links, active nav. Nowhere else — never on card backgrounds or decorative elements.

---

## Typography

### Font Stack
- **Editorial (headlines + body):** `'EB Garamond', Georgia, serif` — old-style serif, Plantin substitute. Plantin is Monocle's print font (commercial); EB Garamond is the closest web-available equivalent: high contrast, bracketed serifs, short ascenders.
- **Utility (masthead + nav + labels + meta):** `'Helvetica Neue', Arial, sans-serif` — system font, no extra load. Monocle uses Helvetica Neue throughout for all non-editorial text.

### Google Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
```
Only one Google Fonts load — Helvetica Neue is system.

### Type Scale

| Element | Family | Size | Weight | Style | Transform | Letter-spacing |
|---|---|---|---|---|---|---|
| Masthead name "AI DAILY" | Helvetica Neue | 72px | 300 | normal | uppercase | 0.12em |
| Masthead eyebrow | Helvetica Neue | 10px | 400 | normal | uppercase | 0.22em |
| Masthead date | Helvetica Neue | 11px | 300 | normal | none | 0.02em |
| Nav links | Helvetica Neue | 11px | 400 | normal | uppercase | 0.08em |
| Section label | Helvetica Neue | 10px | 400 | normal | uppercase | 0.16em |
| "SEE ALL →" | Helvetica Neue | 10px | 400 | normal | uppercase | 0.10em |
| Hero headline | EB Garamond | 36px | 500 | normal | none | -0.01em |
| Article card title (large) | EB Garamond | 22px | 500 | normal | none | 0 |
| Article card title (small) | EB Garamond | 17px | 400 | normal | none | 0 |
| Article summary | EB Garamond | 14px | 400 | normal | none | 0 |
| Hero summary | EB Garamond | 15px | 400 | italic | none | 0 |
| Byline / meta | Helvetica Neue | 11px | 400 | normal | none | 0.02em |
| Category tag | Helvetica Neue | 10px | 400 | normal | uppercase | 0.10em |
| X.com handle | Helvetica Neue | 12px | 400 | normal | none | 0.01em |
| X.com stats | Helvetica Neue | 11px | 300 | normal | none | 0 |
| X.com body | EB Garamond | 14px | 400 | normal | none | 0 |
| Footer | Helvetica Neue | 11px | 300 | normal | none | 0 |

---

## Layout

- **Max-width:** 1280px, centered
- **Side padding:** 40px desktop
- **Hero section:** asymmetric — 3fr large article left + 2fr item stack right
- **Article card grid:** 4 columns, gap 24px (3 columns acceptable for wider cards)
- **X.com list:** single column, full width
- **Alignment:** left throughout

---

## Spacing

| Context | Value |
|---|---|
| Section vertical padding | 48px top + bottom |
| Hero image height | 320px (CSS-only placeholder until real images) |
| Small card image height | 160px |
| Text block padding (hero caption) | 20px 24px |
| Title → summary gap | 10px |
| Summary → meta gap | 10px |
| Between section label and content | 16px |
| X.com row padding | 18px top + bottom |

---

## Borders

- **All rules:** 1px solid `#e7e7e7` (`--border`) — hairlines only
- **Section label rule:** 1px solid `--border` full-width below section label
- **Masthead:** hairline above (1px `--border`) and below (1px `--border`)
- **Card borders:** none — whitespace separates cards
- **X.com rows:** 1px `--border` bottom per row
- **Border-radius:** 0 everywhere
- **No box-shadows**
- **No gradients**

---

## Components

### Masthead (Monocle-faithful)
- White background, 1px `--border` hairline at very top, 1px `--border` below
- Centered layout: eyebrow above name, name centered, date right-aligned on same baseline row
- Eyebrow: Helvetica Neue 10px 400 uppercase tracking 0.22em, `--muted`
- Name "AI DAILY": Helvetica Neue 72px 300 uppercase tracking 0.12em, `--text`
- Date: Helvetica Neue 11px 300, `--muted`, absolute right
- Padding: 24px top 20px bottom

### Navigation
- Helvetica Neue 11px 400 uppercase tracking 0.08em
- Section anchors left; language toggles (EN / 中文) right
- 1px `--border` bottom, 1px `--border` between items
- Active/hover: color `--accent` (#e10912)
- Padding 10px 16px per item

### Section Label (Monocle-faithful)
```
[●] SECTION NAME ─────────────────────────────── SEE ALL →
                  (1px --border hairline below)
```
- 6px × 6px square dot in `--accent` (#e10912)
- Helvetica Neue 10px 400 uppercase tracking 0.16em, `--text`
- Hairline (1px `--border`) extends full-width to right
- "SEE ALL →": Helvetica Neue 10px 400 uppercase, `--accent`
- Margin-bottom 16px below rule

### Article Card (open card, no background)
- Image: full-width block, no radius; use `--bg-warm` CSS block as placeholder
- Below image: category tag (`--accent`) → title (EB Garamond, 22px 500) → summary (EB Garamond 14px, `--muted`) → byline (Helvetica Neue 11px `--muted`)
- No card border, no shadow
- Link color inherit, underline on hover

### Hero Feature
- 3fr / 2fr grid: large article image left, item stack right
- Hero caption area: `--bg-warm` (#fdfcf3) background — Monocle's signature warmth
- Headline: EB Garamond 36px 500, `--text`
- Summary: EB Garamond 15px 400 italic, `--muted`
- Right stack: 3–4 items with small image (right-aligned 80px) or no image, separated by 1px `--border`

### X.com Feed
- Each row: left meta column (140px) + right body column
- Meta: handle Helvetica Neue 12px 400, stats Helvetica Neue 11px 300 `--muted`, date Helvetica Neue 11px 300 `--tertiary`
- Body: EB Garamond 14px 400, "View post →" Helvetica Neue 10px `--accent`
- 1px `--border` bottom per row

### Footer
- 1px `--border` top
- Two columns: brand name left (Helvetica Neue 12px 400 uppercase tracking 0.08em), credit right (Helvetica Neue 11px 300 `--muted`)
- Padding 20px 0

---

## Rules
- No border-radius anywhere
- No shadows, no gradients
- `--accent` (#e10912) used only on: section dots, category tags, SEE ALL links, active nav, X.com view-post links
- Never use accent on card backgrounds or section fills
- EB Garamond for all editorial authority (headlines, body, summaries, X.com posts)
- Helvetica Neue for all structure (masthead wordmark, nav, labels, meta, bylines, footer)
- Cream `--bg-warm` (#fdfcf3) used only on hero caption areas — not as page background
- Hero caption uses cream to contrast with white page — this is Monocle's primary warmth signal
- The masthead name should feel airy and light (weight 300, wide tracking) — never heavy or bold
