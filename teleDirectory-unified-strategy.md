# TeleDirectory — Unified Strategic Document (v2.0)

**Date:** 2026-07-29
**Status:** Aligned — Ready for Execution
**Sources:** Internal team responses + strategic analysis, merged and validated

---

## 1. Executive Summary

**TeleDirectory** is a Telegram Mini App that organizes Ethiopia's fragmented informal commerce into a searchable, verified, neighborhood-organized business directory.

**The Core Bet:** Telegram is where Ethiopian consumers and merchants already live. A structured, trusted directory *inside* the app they use all day doesn't change behavior — it makes existing behavior better.

**Market:** Addis Ababa (starting with Piazza + Bole), targeting Electronics and Apparel categories first.

**Revenue:** Free listings → Verified badges (500–1,500 ETB/month) → Promoted listings → Featured banners.

**Moat:** Trust verification + local merchant density + first-mover in structured Telegram commerce.

**Bootstrapping:** Scrape public Telegram channels → pre-populate directory → merchants "Claim This Shop" → organic onboarding begins.

---

## 2. The Problem

### Current Alternatives & Why They Fail

| Platform | What It Does | Why It Fails |
|----------|-------------|--------------|
| **Google Maps** | Business listings | Sparse coverage of small merchants. Outdated info. Merchants don't update. |
| **Telegram Channels/Groups** | Informal commerce | Disorganized. Endless scrolling. No structured search. No trust signals. |
| **Facebook Groups** | Buy/sell communities | Spam-heavy. No neighborhood filtering. No verification. Scam-prone. |
| **Text-Only Telegram Bots** | Basic search | Poor UX. Command-line interfaces yield clunky text dumps, not visual cards. |
| **Standalone Apps** | Full directory apps | High acquisition cost. Users won't download a 50MB app to search once a month. |
| **Static Web Directories** | Listing websites | Data decay. Merchants never log into web panels. Directories go stale in months. |

### Why Previous Attempts Failed

1. **Standalone apps** — solved discovery but failed on distribution (app install friction).
2. **Web directories** — solved structure but failed on freshness (merchants don't update web profiles).
3. **Telegram bots** — solved distribution but failed on UX (text dumps, no visual profiles).

**TeleDirectory's advantage:** It lives inside Telegram (zero install), has rich visual UI (cards, maps, filters), and merchants are already on the platform daily (data stays fresh).

---

## 3. Market

### Merchants
- Hundreds of thousands of SMEs across retail (electronics, clothing, footwear), local services, and food/beverage in urban Addis Ababa.
- Current workflow: Telegram broadcast channels + cross-posting in buy/sell groups. 2-3 hours/day managing posts.

### Consumers
- Millions of daily active Telegram users in Ethiopia.
- Telegram is the default social, news, and commerce app — virtually synonymous with the consumer internet.

### Why Telegram (Not WhatsApp or Standalone)
- **Dominance:** Telegram is the default platform. WhatsApp has significantly lower market share in Ethiopia.
- **Mini App Ecosystem:** Runs inside Telegram, leveraging existing chat UI, user context, and instant notifications.
- **Distribution:** Zero-friction. Users click a link → Mini App opens. No download, no registration, no new account.

---

## 4. Merchant Experience

### 4.1 Current Workflow

Merchants run dedicated Telegram broadcast channels (e.g., `@StoreName_Electronics`) and cross-post into large public directory or broker groups.

**Daily flow:**
1. Take phone photos of fresh stock
2. Add brief description + price + phone number in caption
3. Post to their channel
4. Cross-post into 3-5 buy/sell groups
5. Respond to DMs, negotiate, close sales

**Their "catalog" is their channel's post history.** No spreadsheets. No inventory software. Just photos and captions.

### 4.2 How TeleDirectory Fits In

TeleDirectory doesn't replace their channel — it acts as an **automated search index** for it. Instead of forcing merchants to re-upload products, TeleDirectory plugs into their existing Telegram presence and organizes their chaotic posts into searchable UI cards.

### 4.3 The "Aha Moment"

The moment a merchant receives this in their Telegram inbox:

> *"Hi, I found your shop [Shop Name] on TeleDirectory regarding your post about [Item]!"*

This is a warm lead appearing directly in their existing chat — no dashboard to check, no analytics to interpret. Instant proof of ROI with zero tech skills required.

**What to optimize for:**
- Profile live in under 5 minutes
- Listing appears in search immediately (no approval queue)
- Pre-filled message attribution on every contact

### 4.4 Updates & Catalog

**Must be lightweight.** If a feature requires manual SKU entry or stock quantities, merchants will abandon it.

- **Phase 1:** Merchants post updates (text + photo) that appear on their TeleDirectory profile as a mini feed. Mirrors their existing channel workflow.
- **Phase 1.5:** Merchants link their Telegram channel. TeleDirectory auto-parses channel posts (photos + captions) into an image grid on their profile.
- **Phase 2:** Optional structured fields (price, availability, category) for merchants who want better search visibility.

**Principle:** Meet merchants where they are. Don't teach a new workflow — amplify the existing one.

---

## 5. Consumer Experience

### 5.1 Search Intent (Ordered by Frequency)

1. **Item-Level (Highest Intent):** "iPhone 15 Pro Max 256GB" or "Nike Pegasus size 42." Users know exactly what they want.
2. **Location/Area:** "Electronics shop around Bole" or "Watch repair in Piazza." Users are in or heading to an area.
3. **Category (Broadest):** "Women's shoes" or "Grocery stores." Exploratory browsing.

### 5.2 Search UX Design

- **Search bar** prioritizes item-level matching against product descriptions in channel posts.
- **Quick filter chips** for sub-city locations: `[Piazza]` `[Bole]` `[Kazanchis]` `[Merkato]`
- **Category chips:** `[Electronics]` `[Clothing]` `[Services]` `[Grocery]`
- **Default view:** Location-based browsing (tap neighborhood → see categories → see shops).

**Mental model:** "Find this item" first, "What's around here?" second.

### 5.3 Decision Factors (When Choosing a Merchant)

1. **Verification Badge / Trust Signal** — Proves the shop physically exists. Prevents advance-payment scams.
2. **Location Proximity** — Can I get there? Is pickup or local delivery feasible?
3. **Price Clarity** — Is the price explicitly listed? No "contact for price" friction.
4. **Recency of Post** — Posted within last 48 hours = item is actually in stock.

### 5.4 What to Surface on Result Cards

| Element | Why |
|---------|-----|
| Shop name + logo | Identity |
| Area tag: "📍 Bole" | Proximity |
| Verification badge: ✓ | Trust |
| Last active: "Updated 2h ago" | Freshness |
| Category tag: "Electronics" | Relevance |

**Save for profile view:** Full catalog, all prices, ratings. Keep cards scannable.

### 5.5 Repeat Use & Retention

**Reality:** High-intent product searches (laptop, shoes) are periodic, not daily. Users won't open TeleDirectory every day to browse.

**Retention engine:**
1. **Saved Shops / Favorites** — Users bookmark shops they've had good experiences with. Creates a personal directory.
2. **Deal Alerts** — Notify users inside Telegram when a saved shop posts a price drop or new item.
3. **Search History** — Quick access to previous searches for recurring needs.

**Priority:** Favorites > Search History > Deal Alerts. Get discovery right first.

---

## 6. Trust & Verification

### 6.1 The Scam Landscape

**The typical scam:**
1. Unverified Telegram channel posts photos of high-demand items (iPhones, PlayStation 5s) at unrealistically low prices.
2. Buyer messages → merchant demands partial advance payment via TeleBirr or bank transfer.
3. Merchant blocks buyer immediately after payment. Or sends counterfeit/empty box.

**The variant:** A "shop" that's a middleman — takes orders, buys from elsewhere at lower quality, pockets the difference. No accountability.

### 6.2 Three-Tier Verification System

| Tier | Method | What It Proves | When It Ships |
|------|--------|---------------|---------------|
| **Tier 1 — Digital** | Cross-reference active phone numbers. Verify Telegram channel ownership via bot. Check against known scam databases. | Real, reachable person. | Phase 1 (MVP) |
| **Tier 2 — Physical** | Validate physical storefront. Photo of shop with TeleDirectory-branded QR code/sign. Trade license verification. | Real business with physical presence. | Phase 1.5 |
| **Tier 3 — Community** | Verified customer reviews over time. Rating accumulation. | Established track record. | Phase 2+ |

**Key insight:** Verification is not a one-time gate. It's an ongoing trust score that compounds. Start simple (Tier 1), layer on sophistication over time.

### 6.3 "Claim This Shop" Mechanism

When a pre-indexed merchant joins TeleDirectory, they see their shop already listed (from scraped data). They can:

1. Tap "Claim This Shop"
2. Authenticate ownership by messaging TeleDirectory's verification bot *from the Telegram account that owns their channel*
3. Bot confirms channel ownership → merchant gets control of their profile

**Why this is powerful:**
- Flips the cold-start problem — merchants see they're already listed, motivating them to take control
- Zero-friction onboarding (they're already on Telegram)
- Built-in verification (channel ownership = identity proof)

---

## 7. Business Model

### 7.1 Pricing (In Ethiopian Birr)

| Tier | Price (ETB/month) | What You Get |
|------|-------------------|-------------|
| **Free** | 0 | Basic listing: shop name, category, location, contact button. No badge. No promotion. |
| **Verified** | 500–800 ETB (~$5-8 USD) | Trust badge visible in search results. Priority in category listings. Basic view/click analytics. |
| **Promoted** | 800–1,500 ETB (~$8-15 USD) | Top of specific category + location search. "Top of Electronics in Bole." |
| **Featured Banner** | 1,000–2,000 ETB/week (~$10-20 USD) | Discovery feed placement. Seasonal/event-driven (holiday sales, back-to-school). |

**Pricing principles:**
- Price in ETB. Always. USD is reference only.
- Start lower than you think. 1000 merchants at 500 ETB/month > 50 merchants at 5000 ETB/month.
- Cheaper than a single Facebook ad, more targeted, with measurable results.

### 7.2 Free-to-Paid Conversion Path

```
Free merchant signs up
    ↓
Gets listed, receives a few leads via pre-filled messages
    ↓
Dashboard shows: "15 users viewed your profile this week. 3 tapped contact."
    ↓
Sees competitor with Verified badge: 45 views, 12 contacts
    ↓
FOMO kicks in → upgrades
```

**Conversion levers:**
- **Competitive intelligence:** "Shops like yours average 50 views/week. You're at 15."
- **Free trial:** 7 days of Verified status for free. Let them feel the difference. Loss aversion does the rest.
- **Visible badges:** Show Verified prominently in search results. Unbadged listings feel slightly inferior.

**Rule:** Never artificially suppress free listings. Free must work fine. Paid must work *better*.

---

## 8. Data Collection Strategy

### Phase 1 — Seeding (Weeks 1-3)

| Method | Target | Volume | Approach |
|--------|--------|--------|----------|
| **Street Survey** | Piazza, Bole | 200-500 shops | Walk commercial streets. Photograph shops. Note names, categories, phone numbers, GPS coordinates. |
| **Telegram Channel Scraping** | Public commerce channels | 500-1,000 listings | Use Telethon/Pyrogram to index public channel metadata (username, post text, image URLs, contact numbers). |
| **Registry Cross-Reference** | Public business registries | As available | Match scraped data against Ethiopian business registration data. |

### Phase 2 — Merchant Self-Onboarding (Week 3+)

- "Add Your Shop" button in the Mini App
- Simple form: name, category, location, phone, photo
- "Claim This Shop" for pre-indexed merchants (verify via Telegram channel ownership)
- On-the-ground agent verifies new submissions by calling or visiting

### Ethical & Legal Guardrails

- Only index **public** channel metadata. No private messages or group chats.
- Don't republish data without merchant knowledge — use scraped data to **invite** merchants to claim their listing.
- Immediate takedown process if a merchant requests removal.
- All scraped data is used to initiate contact, not to publish without consent.

**Principle:** Scrape to seed, transition to merchant-owned data as fast as possible.

---

## 9. Technical Architecture

### 9.1 Stack

```
Frontend:
├── Telegram WebApp SDK (core integration)
├── React or Vue 3 (UI framework)
├── Tailwind CSS (mobile-first responsive)
└── PWA capabilities (offline fallback)

Backend:
├── Node.js (Express/Fastify) or Python (FastAPI)
├── PostgreSQL (primary: shops, users, categories, verification)
├── Redis (caching: sub-second search responses)
└── Telegram Bot API (notifications, merchant communication, "Claim This Shop")

Data Pipeline:
├── Telethon or Pyrogram (public channel scraping)
├── Image CDN (shop photos)
└── Basic ETL for data normalization

Infrastructure:
├── Cloud provider (AWS, GCP, DigitalOcean, or local Ethiopian hosting)
├── CI/CD pipeline
└── Monitoring & alerting
```

### 9.2 Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Frontend framework** | Telegram WebApp SDK + React/Vue | Cross-platform inside Telegram. No app store. |
| **Primary database** | PostgreSQL | Relational data, shop metadata, full-text search support. |
| **Cache layer** | Redis | Sub-second search responses. Critical for UX. |
| **Scraping** | Telethon (Python) | Mature library for Telegram client API. Public channels only. |
| **Auth** | Telegram User ID | Zero-friction login. No passwords, no email verification. |
| **Image storage** | CDN + object storage | Fast image delivery for shop photos and logos. |

---

## 10. Team & Execution

### 10.1 Minimum Viable Team

| Role | Count | Responsibilities |
|------|-------|-----------------|
| **Full-Stack Developer** | 1 | Telegram WebApp frontend, API endpoints, Redis caching, Telegram Bot. Builds everything technical. |
| **On-the-Ground Operator** | 1 | Merchant onboarding, street surveys, physical verification visits in Piazza/Bole. Data collection. |
| **Founder / Product** | 0.5 | UX decisions, visual identity, product direction, business development, merchant relationships. |

### 10.2 Solo Build Scenario

If building alone (1 person doing dev + operations):
- Expect 2-3x the timeline
- Prioritize: get the directory live with seeded data first, then add merchant self-onboarding
- Ground data collection happens on weekends or evenings

### 10.3 What You Don't Need Yet

- Dedicated designer (use a clean Tailwind template)
- Marketer (Telegram Mini Apps spread virally through sharing)
- Data scientist
- DevOps engineer
- Customer support team (handle manually at MVP scale)

---

## 11. MVP Scope (Phase 1)

### IN — Ships with MVP

- [x] Search by item keyword + location + category
- [x] Shop profile pages with contact buttons (Call / Telegram Message)
- [x] Pre-filled message attribution: "I found your shop on TeleDirectory regarding [Item]"
- [x] Quick filter chips (Piazza, Bole, Kazanchis + categories)
- [x] Tier 1 verification (digital: phone + channel ownership)
- [x] "Claim This Shop" for pre-indexed merchants
- [x] Simple "Add Your Shop" self-submission form
- [x] Shop update feed (text + photo posts)
- [x] Favorites / Saved Shops
- [x] Basic merchant dashboard (views, contacts this week)
- [x] Pre-seeded directory (200-500 shops from scraping + street survey)

### OUT — Phase 1.5+

- [ ] Channel auto-import (parse merchant's Telegram channel into catalog)
- [ ] Promoted listings / paid features
- [ ] Ratings & reviews
- [ ] Advanced analytics (demographics, peak hours)
- [ ] Deal alerts / push notifications
- [ ] Payment integration
- [ ] Multi-city expansion
- [ ] Merchant subscription billing

---

## 12. Roadmap

### Phase 1 — Directory & Verification (Weeks 1-6)
- Launch Telegram Mini App
- Pre-seeded directory (Piazza + Bole, Electronics + Apparel)
- Search + filter + shop profiles + contact buttons
- Tier 1 verification + "Claim This Shop"
- Basic merchant dashboard
- **Goal:** 300+ listed shops, 1000+ active users

### Phase 1.5 — Merchant Empowerment (Weeks 7-10)
- Channel auto-import feature
- Enhanced "Add Your Shop" flow with photo verification
- Merchant self-service updates
- **Goal:** 50+ merchants actively managing their profiles

### Phase 2 — Growth & Monetization (Months 3-4)
- Promoted listings + paid verification badges
- Featured banners on discovery feed
- Deal alerts for saved shops
- Tier 2 verification (physical storefront validation)
- **Goal:** First revenue, 100+ paid merchants

### Phase 3 — Platform & Expansion (Months 5+)
- Ratings & reviews (Tier 3 verification)
- Advanced merchant analytics
- Multi-city expansion beyond Addis Ababa
- Payment integration (TeleBirr, CBE Birr)
- In-app order management
- **Goal:** Self-sustaining platform, regional expansion

---

## 13. Immediate Next Steps

| # | Action | Owner | Timeline |
|---|--------|-------|----------|
| 1 | Validate assumptions: 2-3 days talking to merchants in Piazza/Bole | Ground operator + Founder | Week 1 |
| 2 | Start data collection: scrape 5-10 public Telegram commerce channels | Developer | Week 1 |
| 3 | Design wireframes for search results + shop profile + "Claim This Shop" | Founder | Week 1 |
| 4 | Set up tech stack: Telegram WebApp + PostgreSQL + Redis | Developer | Week 1-2 |
| 5 | Build search + filter core functionality | Developer | Week 2-3 |
| 6 | Build shop profile pages + contact buttons with pre-filled messages | Developer | Week 3-4 |
| 7 | Street survey: manually collect 200+ shops in Piazza/Bole | Ground operator | Week 2-4 |
| 8 | Launch "Claim This Shop" flow | Developer | Week 4-5 |
| 9 | Soft launch: invite 50 merchants to claim their listings | Founder | Week 5 |
| 10 | Public launch: share Mini App link in Telegram commerce groups | Founder | Week 6 |

---

*This is a living document. Update as assumptions are validated or invalidated through market research and user conversations.*
