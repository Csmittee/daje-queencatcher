# CLAUDE.md — daje-queencatcher
> Version 1.0 — 2026-06-25
> Changes: Initial creation — governance seed
> Previous: NONE

Project: Daje Games — Claw machine and vending machine mini-site (BUS02)
Domain: daje.janishammer.com
BUS ID: BUS02

Governance: ALL rules at janishammer-central/RULES.md + .claude/rules/
Read janishammer-central CLAUDE.md before reading anything in this repo.

Injector:
  injector-config.js — YES — sync from assets.janishammer.com
  injector-core.js   — YES — sync from assets.janishammer.com

Local key files:
  index.html                   — EN homepage (1184L ⚠️ OVER 800 LINES)
  scripts/generate_products.py — Airtable → bilingual product HTML
  products.json                — generated product data

Critical constraint: index.html is 1184 lines — over the 800-line limit.
Do not edit without reading RULES-html.md (HTML-1) and proposing a split plan
to the owner first. See RETROFIT_QUEUE item #8.

Tech: Vanilla HTML/CSS/JS · Airtable · Python build · GitHub Actions · Cloudflare Pages
