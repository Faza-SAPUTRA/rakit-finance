You are working in the existing "rakit-finance" Flask repo. I want two upgrades to the landing page, both inspired by specific React Bits components — but since this project has no React runtime (it's Flask + Jinja2 + vanilla JS, with GSAP and Anime.js already loaded via CDN in app/templates/base.html), you must recreate the BEHAVIOR of these components in vanilla JS/CSS using GSAP, not import React code. Match Rakit's existing design tokens exactly: colors defined in base.html's tailwind.config (white #FFFFFF, offwhite #F7F8F7, primary #0F5C3F, accent #2ECC71, black #0A0A0A, charcoal #1A1A1A, muted #8A9A92, line #DDE6E0), font Inter, existing shadow-glow/shadow-card utilities.

============================================
PART 1 — Replace the navbar with a "Staggered Menu" pattern
============================================

Reference: https://reactbits.dev/components/staggered-menu (an open/close full-screen or panel overlay menu where the nav links animate in with a staggered slide/fade as the menu opens, and a hamburger/menu icon morphs into a close icon).

Current navbar lives in app/templates/landing/index.html (the <header> with the sticky bg-white/80 backdrop-blur-xl bar, logo, nav links: Features / How it works / Why Rakit, Log in link, and Get Started button).

Replace it with a Staggered Menu pattern:
1. Keep the persistent top bar (logo on the left, "Log in" + "Get Started" pill button on the right) but replace the inline center nav links with a single menu trigger button (animated hamburger icon — two/three lines that morph into an X on open, using GSAP or CSS transitions).
2. On click, open a full-height overlay panel (covers full viewport height, slides in from the right or top — your choice, but right-side panel sliding in is the closest match to the reference component's most common variant) with a solid background using our offwhite or white token plus a subtle blur/overlay behind it dimming the page content.
3. Inside the panel, list the nav items (Features, How it works, Why Rakit, Log in, Get Started) as large, bold text links stacked vertically. Animate them in with a STAGGERED entrance: each link slides in from the right (or fades up) with a small delay offset between each one (GSAP stagger, ~0.06-0.09s between items), so they cascade in sequence rather than appearing all at once — this stagger is the signature effect of the reference component.
4. The panel background itself should also animate in (a quick slide/reveal, e.g. clip-path or transform translateX from 100% to 0) slightly before or simultaneously with the staggered links, so the panel "arrives" and then the links cascade inside it.
5. On close, reverse the stagger (links exit first, fastest item last, or all together — match whichever direction feels snappier) then the panel slides back out.
6. Add a subtle hover state on each link (color shift to primary green, small underline-grow or arrow-slide-in effect) consistent with the rest of Rakit's premium feel.
7. This must work on both desktop and mobile widths — on mobile, the panel can simply be full-width/full-height.
8. Respect prefers-reduced-motion: if set, skip the stagger/slide and just show/hide the panel with a simple opacity fade.
9. Implement this as a new file: app/static/js/staggered-menu.js, loaded in base.html alongside the other animation scripts (after gsap and anime.js, same position as the other static/js/*.js includes). Add any new menu markup directly into app/templates/landing/index.html (and reuse the same header partial across other pages if the navbar is duplicated elsewhere in app/templates — check app/templates/partials/ for a shared header/nav include before duplicating markup).

============================================
PART 2 — Add a new landing page section using the "Scroll Stack" pattern
============================================

Reference: https://reactbits.dev/components/scroll-stack (a scroll-driven section where multiple cards stack on top of each other — as the user scrolls, each card animates from below into a "stacked" resting position, slightly offset/scaled from the card beneath it, like a deck of cards being dealt and pinned as you scroll past).

Add a NEW section to app/templates/landing/index.html (place it after the existing #features section and before the #how "Three steps to financial clarity" section, so it reinforces features right after they're introduced). This section must showcase what Rakit ACTUALLY provides — do not invent generic content. Use these real Rakit modules, one per stacked card, pulling language consistent with what's already used elsewhere on the page:

Card 1 — "Smart Import": polymorphic parsing of bank/e-wallet statements (BCA, GoPay, and more) via CSV/Excel upload.
Card 2 — "Receipt Scanner": OCR-based receipt scanning (Pytesseract) that extracts merchant, date, and nominal for confirmation.
Card 3 — "Assets & Liabilities": net worth tracking via Account subclasses (AssetAccount / LiabilityAccount) with signed contributions.
Card 4 — "Investment Simulator": projected growth across Reksa Dana (mutual fund), Gold, and Crypto instrument subclasses, each overriding calculate_projection().
Card 5 — "Market Analytics": portfolio distribution donut chart, risk exposure gauge meter, and a structured market news feed.

(If you want a punchier section instead of one card per existing feature, you may consolidate to 3-4 cards, but every card must map to a real Rakit feature already implemented in the codebase — check app/models, app/parsers, app/services and app/templates/dashboard for the authoritative feature list before writing card copy.)

Implementation:
1. Each card should be a rounded-[24px] white card with shadow-card/shadow-glow (consistent with other cards on this page), containing: an icon (Material Symbols, consistent with the rest of the page), a bold title, a short 1-2 sentence description, and optionally a small visual accent (a mini chart placeholder, a colored stat pill, or an icon-based illustration relevant to that feature — keep it simple, this is a supporting visual not a full mockup).
2. As the user scrolls through this section, each card should animate in from slightly below and behind the previous card, then "stack" into a pinned/sticky resting position with a slight vertical offset and a slight scale-down compared to the card in front of it (e.g. each successive card sits ~20-30px lower and ~2-4% smaller, creating a layered stack effect, similar to a deck of cards fanned vertically). Use GSAP ScrollTrigger with `pin: true` (or `scrub`) on a wrapping container so the stacking effect is driven directly by scroll position, not just a one-time entrance animation — the user should feel like scrolling "deals" each card into the stack.
3. Once all cards are stacked, continuing to scroll should release the pin and continue normally into the next section (#how).
4. Use Primary Green or Accent Green accents on the icons/stat pills inside each card — keep the white/offwhite background dominant per our existing design system (do not introduce a dark background for this section).
5. Respect prefers-reduced-motion: if set, render the cards in a simple static vertical stack with normal spacing (no pin/scroll-stacking), just a basic fade-in via the existing .reveal GSAP pattern already used elsewhere on the page.
6. Implement this as a new file: app/static/js/scroll-stack.js, loaded in base.html in the same script block as the other animation files. Add the section markup directly into app/templates/landing/index.html.

============================================
GENERAL RULES FOR BOTH PARTS
============================================
- Do not add a React/Vue dependency or any new npm-based frontend build step — everything stays vanilla JS + GSAP/Anime.js loaded via the existing CDN script tags in base.html.
- Do not change the existing color tokens or introduce blue.
- Keep both new scripts modular and namespaced (IIFE pattern like the existing JS files) so they don't conflict with anime-animations.js, gsap-animations.js, or react-bits-effects.js.
- After implementing, list every file you created or modified, and give a one-line summary of what each new script does.