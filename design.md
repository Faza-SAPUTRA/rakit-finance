# design.md — Rakit Finance

This file defines the persistent design system for the Rakit Finance landing 
page and product UI. Paste this into your AI coding assistant (Cursor, etc.) 
as project context before running revision prompts, so every change stays 
consistent with the actual visual identity already shipped — instead of 
drifting toward a different palette or style.

Colors and values below were extracted directly from the current production 
screenshot, not estimated from generic Tailwind defaults — treat this as the 
source of truth and correct any value below if it doesn't match your actual 
CSS/Tailwind config.

---

## Product

**Rakit** — a premium-feeling personal finance dashboard for Indonesia. A 
Flask-rendered PWA covering transactions, Smart Import, OCR receipt 
scanning, asset/liability tracking, an investment simulator, and market 
analytics — positioned as a "SaaS-grade finance command center," not a 
basic budgeting app.

## Mood / Art Direction

Calm, confident, premium-fintech. The tagline itself states the intent: 
"One calm, intelligent dashboard." This is not playful or colorful fintech 
(no gradients-everywhere, no rounded mascot illustrations) — it reads closer 
to a private banking / wealth-management product than a consumer budgeting 
app. Trust and clarity over excitement.

---

## Color Palette

| Token | Approx. value | Usage |
|---|---|---|
| `bg-base` | `#FFFFFF` | Page background, top of hero |
| `bg-wash` | very pale green-tinted white, roughly `#F3F8F4` → `#EAF3EC` | Hero background gradient (white fading into a faint mint wash toward the bottom/edges of the hero) |
| `surface-card` | `#FFFFFF` | Dashboard preview cards, content cards — clean white with soft shadow |
| `surface-card-soft` | very light gray/green, roughly `#F0F3F1` | Secondary/nested card surface (e.g. "Assets" tile inside the dashboard preview) |
| `text-primary` | near-black, roughly `#0B0E0C` | Headlines, primary numbers (e.g. "Rp 1.13B") |
| `text-secondary` | mid gray, roughly `#8A9089` | Supporting/label text (e.g. "NET WORTH", "Assets") |
| `accent-emerald` | deep emerald green, roughly `#0F4D3A`–`#155E45` | Primary actions ("Get Started" button fill, "Create free account" button border+text, logo mark background, badge text/border) |
| `accent-emerald-soft` | pale mint, roughly `#D9EFE1` | Positive-value pill backgrounds (e.g. "+12.4%" badge, "Live" badge background) |
| `accent-black` | true near-black, roughly `#0B0E0C`–`#111412` | Secondary high-contrast accent used deliberately alongside emerald — NOT just for text. Used as solid fill on the "Liabilities" card and the "SAVINGS GOAL / 78%" card. This black-as-accent pairing alongside emerald is a distinctive trait of the current design — preserve it. |
| `border-subtle` | very light gray, roughly `#E7EAE7` | Card borders, hairline dividers (e.g. divider under the top nav, ticker strip border) |

**Rule:** This is a two-accent system — emerald for primary/positive actions 
and signals, near-black for secondary high-contrast emphasis blocks. Both 
sit on a white-to-pale-mint base. Do not introduce additional accent hues 
(no blue, no orange/red except possibly a future "negative value" red if 
needed for expenses — confirm before adding). Do not flatten the background 
to pure white everywhere — the soft gradient wash in the hero is part of the 
current visual identity and should be preserved or deliberately extended to 
other sections, not removed.

---

## Typography

| Role | Direction observed | Usage |
|---|---|---|
| Headline | Bold, geometric/grotesk sans-serif, heavy weight, tight line-height | Hero headline ("All your money. One calm, intelligent dashboard.") |
| Body | Regular-weight sans-serif, comfortable line-height, gray (`text-secondary`) | Supporting paragraph copy |
| UI labels | Small, uppercase or sentence-case, letter-spaced, muted gray | Card labels like "NET WORTH", "SAVINGS GOAL", ticker brand names (BRI, GOPAY, MANDIRI, etc.) |
| Numeric/financial values | Bold sans-serif (NOT monospace) | "Rp 1.13B", "+12.4%", "Rp 92.5M" — numbers are styled as confident bold statements, not as monospace "system output" the way a dev-tool product would render them |

**Note for AI builder:** unlike a developer-tool aesthetic (terminal/monospace 
heavy), Rakit's financial figures are rendered in the same warm bold 
sans-serif as the rest of the UI — keep it that way. Don't introduce 
monospace for prices/numbers here; that belongs to a different kind of 
product (e.g. a dev/security tool), not a calm consumer finance dashboard.

---

## Layout & Component Rules

- **Rounded, soft geometry** — cards use generous border-radius (rounded-2xl 
  / rounded-3xl range), not sharp corners. This is the opposite of a 
  sharp-cornered "technical" aesthetic — softness reinforces the "calm" 
  positioning.
- **Layered card composition in the hero** — the dashboard preview is shown 
  as multiple overlapping cards at slightly different depths/positions (net 
  worth card, savings goal card, cashflow card, recent activity card), not a 
  single flat screenshot. This layered-overlap treatment is a key part of 
  what makes the hero feel premium — preserve and consider extending this 
  pattern to other sections (e.g. feature showcases) rather than replacing it 
  with flat single-image mockups.
- **Soft shadows, not borders, separate floating cards** — the dashboard 
  preview cards use subtle drop shadows rather than hard outlines.
- **Pill-shaped buttons and badges** — both CTA buttons ("Create free 
  account", "Open demo") and the eyebrow badge ("Premium personal finance for 
  Indonesia") use fully rounded/pill shapes, not rectangular buttons.
- **Primary button** = solid emerald fill, white text, pill shape. 
  **Secondary button** = white fill, black/dark text, thin border, pill 
  shape (seen on "Open demo"). A third variant exists with emerald border + 
  emerald text on white fill, pill shape (seen on "Create free account").
- **Logo mark** = small solid emerald circle with a white letter mark ("R") — 
  keep this treatment consistent anywhere the brand mark appears.
- **Bottom ticker strip** — a horizontal row of bank/wallet partner names 
  (BRI, ShopeePay, GoPay, Mandiri, OVO, etc.) in muted uppercase gray text, 
  separated by a hairline border from the hero above it. Functions like a 
  "works with" trust strip.

---

## Copy Voice

- Calm, confident, benefit-led. Example from the current hero: "All your 
  money. One calm, intelligent dashboard." — short declarative sentences, 
  not feature-dumping.
- Supporting copy lists concrete capabilities directly (expenses, assets, 
  liabilities, receipts, imports, investments, market analytics) rather than 
  vague benefit language — specific nouns, not "powerful insights."
- Position language: "SaaS-grade finance command center" — premium and 
  professional framing, not casual/playful budgeting-app language.
- Button labels are direct actions: "Create free account", "Open demo", "Get 
  Started" — not vague nouns.

---

## What to avoid

- Do not introduce a strict monochrome black/white-only palette (that belongs 
  to a different product's design system — do not cross-apply it here).
- Do not switch financial numbers to monospace font.
- Do not flatten the soft gradient hero background to solid flat white.
- Do not replace the rounded/pill geometry with sharp corners.
- Do not replace the layered overlapping card composition with a single flat 
  screenshot/mockup image.
- Do not add accent colors beyond emerald + near-black (confirm before adding 
  red/orange for negative-value states if that becomes necessary).

---

## Page Structure (current landing page — reference for revision work)

1. Top nav (logo, Menu, Log in, Get Started)
2. Hero (eyebrow badge, headline, supporting paragraph, two CTAs, layered 
   dashboard preview composition)
3. Partner/bank ticker strip
4. (Further sections below the fold — features, FAQ, etc. — not visible in 
   this reference screenshot; confirm actual current structure directly in 
   the codebase before revising.)