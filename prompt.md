# Rakit — AI Builder Prompt

## PROJECT BRIEF

Build **"Rakit"** — a premium-feeling, SaaS-grade Personal Finance Dashboard web app (Progressive Web App) using **Python + Flask** for the backend. The product tracks a user's daily expenses, assets, and liabilities in one place, with Smart Import, OCR receipt scanning, an investment simulator, and a market analytics dashboard. The app must **look and feel expensive** — like a funded fintech startup's flagship product, not a student project or generic CRUD app.

This is an academic OOP (Object-Oriented Programming) project, so the **backend architecture must visibly demonstrate Inheritance and Polymorphism** — this is a hard requirement, not a nice-to-have.

---

## 1. TECH STACK (do not substitute)

**Backend**
- Python 3.11+, Flask (microframework, Class-Based Views where appropriate)
- SQLAlchemy ORM (SQLite for dev, structured so it's swappable to PostgreSQL)
- Flask-Login for auth/session management
- Pytesseract + Pillow for OCR (Receipt Scanner)
- Pandas for CSV/Excel parsing (Smart Import)
- Flask-RESTful or plain Flask routes returning JSON for any endpoint the frontend fetches asynchronously

**Frontend**
- Server-rendered Jinja2 templates (Flask's default), enhanced with vanilla JS / fetch calls for dynamic widgets — **no React/Vue framework**, since this stays a Flask-rendered app
- **Tailwind CSS** (via CDN or build step) as the styling foundation
- **GSAP** (GreenSock) — core scroll-triggered animations, micro-interactions, page transitions, number counters
- **Anime.js** — landing page hero animations, especially any 3D/depth motion effects and SVG path animations
- **React Bits**-style animation patterns — since this is a Flask app (not React), recreate the *visual effects* React Bits is known for (animated gradient backgrounds, magnetic buttons, spotlight cards, animated borders, text reveal effects, particle backgrounds) using **vanilla JS + CSS + GSAP/Anime.js** instead of importing React Bits components directly. Be explicit in the code comments that these are "React Bits-inspired" recreations in vanilla JS.
- Chart.js or ApexCharts for Donut Chart (portfolio distribution) and Gauge Meter (risk exposure index)

**Do not** introduce a separate Node/React frontend, a separate API gateway, or a no-code builder. Everything renders from Flask.

---

## 2. DESIGN SYSTEM — "Premium Fintech"

### Color Palette (strict — green / white / black only, no blue)
- **White**: `#FFFFFF` (DEFAULT background color — main app background, all light-mode cards, landing page, dashboard, everything starts here)
- **Off-White**: `#F7F8F7` (secondary background — section backgrounds, subtle contrast against White cards)
- **Primary Green**: `#0F5C3F` (deep emerald — primary actions, active states)
- **Accent Green**: `#1FAA59` or `#2ECC71` (bright green for highlights, success states, CTA buttons, chart accents)
- **Pure Black**: `#0A0A0A` (headings and body text color — NOT a default background; reserve for a single deliberate dark accent section, such as the landing page's final CTA band, if desired)
- **Off-Black / Charcoal**: `#1A1A1A` (text/icon color for liability or warning states, and text within the one allowed dark section)
- **Muted Gray-Green**: `#8A9A92` (secondary text, borders, dividers)
- Default to a **White-dominant** look throughout — landing page, auth, and dashboard all use White/Off-White backgrounds with Black text and Green accents (think Stripe, Mercury, Ramp aesthetic — premium and airy, not playful, not pastel, and not dark-themed by default)

### Typography
- Headings: a modern grotesque/geometric sans (e.g., "Inter", "Satoshi", or "General Sans") — bold, tight letter-spacing
- Body: "Inter" or system sans, comfortable line-height
- Numbers/financial figures: tabular-nums, slightly larger weight for emphasis (this is a money app — numbers must feel substantial)

### Visual Language
- Generous white space, large border-radius (16–24px) on cards
- Soft, colored shadows (green-tinted glow on hover, not generic gray drop-shadows)
- Glassmorphism touches on overlapping elements (frosted blur cards over light gradient backgrounds)
- Subtle pale-green gradient mesh or soft glow behind hero content to avoid a flat white look
- Iconography: thin-stroke, consistent icon set (Lucide or Phosphor icons)
- Avoid: default Bootstrap look, default Tailwind gray palette, generic shadow-md cards, comic/playful illustration styles

---

## 3. PAGES & STRUCTURE

### A. Landing Page (public, marketing, must feel "expensive")
Sections, in order:
1. **Navbar** — logo "Rakit", nav links, "Log in" + prominent green "Get Started" CTA button (magnetic hover effect)
2. **Hero Section** (White background, default)
   - Animated headline (text reveal/split-text animation on load via Anime.js)
   - Subheading: positions Rakit as the all-in-one personal finance dashboard
   - Animated 3D/parallax mockup of the dashboard (CSS 3D transform + Anime.js, tilts on mouse move)
   - Primary CTA button with animated gradient border or particle/spotlight hover effect
   - Subtle animated background (floating gradient blobs or particle network, low-opacity green on White/Off-White)
3. **Logos/Trust strip** — "Works with BCA, GoPay, Mandiri..." (placeholder bank/e-wallet logos) with marquee/infinite-scroll animation
4. **Feature Showcase** (scroll-triggered GSAP reveal, one feature per scroll section):
   - Smart Import (drag-and-drop CSV/Excel from multiple banks)
   - Receipt Scanner (OCR) — show a mock "scan receipt → auto-filled transaction" animation
   - Assets & Liabilities Tracker — animated net worth counter ticking up
   - Investment Simulator — animated line/area chart drawing in on scroll
   - Market Analytics — animated Donut Chart and Gauge Meter drawing in on scroll
5. **How it works** — 3-step process with connecting animated line (SVG path animation via Anime.js)
6. **Social proof / stats strip** — animated counting numbers (e.g., "Rp 2.4B+ tracked", "10,000+ transactions categorized") using GSAP ScrollTrigger + number tween
7. **Pricing or "Why Rakit" comparison** (optional, can be a simple comparison table with hover-glow rows)
8. **Final CTA** — full-width section, big headline, "Create free account" button. May optionally use a Black/deep-green background as a single deliberate dark accent moment, but White/Off-White also works and is the safer default.
9. **Footer** — minimal, White or Off-White background, Black/Gray-Green text, links + social icons

### B. Auth Pages
- Login / Register — centered card on a subtly animated gradient/particle background, same premium feel, NOT a bare Bootstrap form

### C. User Dashboard (post-login app shell)
Persistent **left sidebar** (collapsible) + **top bar** layout:

- **Sidebar nav**: Overview, Transactions, Smart Import, Receipt Scanner, Assets & Liabilities, Investment Simulator, Market Analytics, Settings
- **Top bar**: search, notifications, profile avatar/dropdown, dark/light mode toggle

**Dashboard pages:**

1. **Overview** — Net worth hero number (animated count-up on load), Assets vs Liabilities summary cards, recent transactions list, mini donut chart of spend categories, quick "Scan Receipt" and "Import File" action buttons
2. **Transactions** — filterable/sortable table of all transactions, category tags (color-coded), search, date range filter
3. **Smart Import** — drag-and-drop zone (animated border on drag-over) for CSV/Excel upload; backend parses via the Polymorphic `TransactionParser` → `BcaParser` / `GopayParser` architecture (see Section 4); shows preview table before confirming import
4. **Receipt Scanner** — upload/drag a receipt photo, shows OCR processing animation (Anime.js loading state), then displays extracted nominal/merchant/date for user confirmation before saving as a transaction
5. **Assets & Liabilities** — two-column layout: Assets (cash, bank balances, investments) vs Liabilities (debt, credit), with an "Account" architecture (Inheritance: `Account` → `AssetAccount` / `LiabilityAccount`); supports transfer/payment between accounts
6. **Investment Simulator** — pick an instrument (Reksa Dana / Gold / Crypto — each a subclass of `InvestmentAsset` overriding `calculate_projection()`), input amount + duration, see animated projected growth chart
7. **Market Analytics** — Donut Chart (portfolio distribution), Gauge Meter (Risk Exposure Index), real-time-style news feed list (placeholder/dummy data is fine, structured so a real API can be plugged in later)
8. **Settings** — profile, linked accounts, theme, notification preferences

---

## 4. BACKEND ARCHITECTURE — OOP REQUIREMENTS (critical, do not skip)

This project must visibly demonstrate **Inheritance** and **Polymorphism**. Structure the Flask backend like this:

```
app/
├── models/
│   ├── account.py          # abstract Account base class
│   │                       #   -> AssetAccount(Account)
│   │                       #   -> LiabilityAccount(Account)
│   ├── transaction.py
│   ├── investment.py       # abstract InvestmentAsset base class
│   │                       #   -> MutualFundAsset(InvestmentAsset)   # Reksa Dana
│   │                       #   -> GoldAsset(InvestmentAsset)
│   │                       #   -> CryptoAsset(InvestmentAsset)
│   │                       #   each overrides calculate_projection()
│   └── user.py
├── parsers/
│   ├── transaction_parser.py   # abstract TransactionParser base class
│   │                           #   -> BcaParser(TransactionParser)
│   │                           #   -> GopayParser(TransactionParser)
│   │                           #   each overrides parse(file) -> List[Transaction]
│   └── __init__.py
├── services/
│   ├── ocr_service.py       # wraps pytesseract for Receipt Scanner
│   ├── analytics_service.py # builds donut chart + gauge meter data
│   └── import_service.py    # selects correct parser via polymorphism
├── routes/
│   ├── auth.py
│   ├── dashboard.py
│   ├── transactions.py
│   ├── import_routes.py
│   ├── receipt_routes.py
│   ├── investment_routes.py
│   └── analytics_routes.py
├── templates/
│   ├── landing/
│   ├── auth/
│   └── dashboard/
├── static/
│   ├── css/
│   ├── js/   (gsap-animations.js, anime-animations.js, react-bits-effects.js, charts.js)
│   └── img/
└── __init__.py  (Flask app factory)
```

**Key OOP rules to implement literally:**
- `Account` is an abstract base class with shared fields (`balance`, `name`, `account_type`) and a shared `display_balance()` method; `AssetAccount` treats balance as positive net worth contribution, `LiabilityAccount` treats it as a deduction. A `transfer(amount, from_account, to_account)` function should work polymorphically regardless of account subtype.
- `TransactionParser` defines an abstract `parse(file) -> list[Transaction]`. `BcaParser` and `GopayParser` each implement their own column-mapping/parsing logic for their bank's CSV format. The import service picks the right parser class based on a user-selected source or detected file signature — this IS the polymorphism: same method call, different behavior per subclass.
- `InvestmentAsset` defines an abstract `calculate_projection(years, contribution)`. Each subclass (`MutualFundAsset`, `GoldAsset`, `CryptoAsset`) overrides it with different growth-rate assumptions/formulas.

Use Python `abc.ABC` and `@abstractmethod` to enforce this properly.

---

## 5. ANIMATION IMPLEMENTATION NOTES

- Load **GSAP** + **ScrollTrigger** plugin via CDN for: scroll-reveal sections, sticky feature panels, animated number counters, smooth page-section transitions.
- Load **Anime.js** via CDN for: hero text split/reveal, SVG path drawing (how-it-works connector lines), the 3D tilt/parallax effect on the hero dashboard mockup (combine with CSS `perspective` + `transform-style: preserve-3d`, driven by mouse-move listener calling `anime()` on rotateX/rotateY).
- Recreate "React Bits" signature effects in vanilla JS/CSS, e.g.:
  - **Spotlight Card**: CSS radial-gradient that follows cursor position via JS mousemove
  - **Magnetic Button**: button translates slightly toward cursor on hover, springs back on leave (GSAP `quickTo`)
  - **Animated Gradient Border**: CSS `@property` + conic-gradient rotation, or animated background-position on a gradient border
  - **Text Reveal**: clip-path or mask animation revealing text on scroll into view
  - **Particle/Network Background**: lightweight canvas particle system for the hero background (keep performant — cap particle count, pause when tab inactive)
- Respect `prefers-reduced-motion` — disable/simplify animations for users who request it (accessibility, also signals "premium" attention to detail).
- Keep animations snappy (200–500ms for micro-interactions, 600–1000ms for scroll reveals) — premium products feel responsive, not sluggish.

---

## 6. DATA & SCOPE NOTES

- Smart Import: support CSV/Excel upload, initially supporting BCA and GoPay formats (per the parser architecture above); design it so adding a new bank parser later is trivial (just subclass `TransactionParser`).
- Receipt Scanner: accept image upload (jpg/png), run through Pytesseract, extract and return the total nominal amount + attempt merchant name/date extraction; always show an editable confirmation step before saving (OCR isn't perfect).
- Market Analytics news feed and real-time asset prices can use **mock/dummy data** for now, but structure the service layer so a real third-party API (e.g., crypto price API, financial news API) can be swapped in later without touching the frontend.
- All monetary values should be stored as integers (cents/smallest unit) or `Decimal` — never raw floats — to avoid rounding bugs.

---

## 7. DELIVERABLE EXPECTATIONS

- Fully runnable Flask app (`flask run` or `python app.py` starts it) with `requirements.txt`
- Seed/demo data script so the dashboard isn't empty on first run
- Responsive design (desktop-first, but usable on mobile/tablet since it's a PWA)
- Basic `manifest.json` + service worker stub so it qualifies as a PWA
- Clean, commented code — especially around the OOP class hierarchies, since this is the core academic requirement
- README explaining setup steps and where the Inheritance/Polymorphism implementations live

---

## 8. WHAT TO AVOID

- No blue in the palette (the original brief used Gojek Green + Deep Blue, but this version is green/white/black only)
- No React/Vue/Next.js frontend — stay Flask + Jinja2 + vanilla JS
- No generic "admin template" look (no default Bootstrap, no AdminLTE, no default shadcn defaults without customization)
- No flat, static, animation-free landing page — motion is a core requirement, not decoration
- No cluttered dashboard — premium fintech means restraint: lots of whitespace, a few bold numbers, not 20 small widgets crammed together

---

**Build this step by step**: start with the Flask app factory + models/OOP architecture first, then auth, then the dashboard shell, then each feature page, and finally the landing page with full animation polish.