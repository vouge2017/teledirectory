# TeleDirectory — Strategic Q&A & Product Thinking

**Document Version:** 1.0
**Date:** 2026-07-29
**Status:** Living Document — For Review & Iteration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [The Market & Problem](#the-market--problem)
3. [Merchant Experience Deep Dive](#merchant-experience-deep-dive)
4. [Consumer Experience Deep Dive](#consumer-experience-deep-dive)
5. [Competitive Landscape & Scam Analysis](#competitive-landscape--scam-analysis)
6. [Business Model & Monetization](#business-model--monetization)
7. [Technical Execution & Team](#technical-execution--team)
8. [Data Collection Strategy](#data-collection-strategy)
9. [Strategic Recommendations](#strategic-recommendations)
10. [Next Steps](#next-steps)

---

## Executive Summary

**TeleDirectory** is a Telegram Mini App that turns Ethiopia's fragmented informal commerce (scattered across messy Telegram channels, Facebook groups, and word of mouth) into a searchable, verified, neighborhood-organized business directory. Starting with Addis Ababa (Piazza + Bole), categories like Electronics and Apparel, and building outward.

**Core Bet:** Telegram is where Ethiopian consumers and merchants already live. If you put a structured, trusted directory *inside* the app they already use 10+ hours a day, you don't need to change behavior — you just need to make existing behavior better.

**Revenue Model:** Promoted listings, paid verification badges, featured merchant banners.

**Moat:** Trust (verification in a scam-heavy environment) + local density (first to properly map specific commercial hubs) + merchant data freshness (they update because they're already on Telegram daily).

**Bootstrapping Strategy:** Scrape public Telegram commerce channels + seed manually in target neighborhoods + enable self-onboarding from day one.

---

## The Market & Problem

### Current Alternatives & Their Flaws

| Platform | What It Does | Why It Fails |
|----------|-------------|--------------|
| **Google Maps** | Business listings with location | Lacks density for small/informal merchants in Addis. Outdated contact details. Missing price/catalog info. Merchants don't update profiles. |
| **Telegram Channels/Groups** | Informal commerce via posts | Disorganized. Endless scrolling. Search is noisy and uncurated. No structured profiles. |
| **Facebook Groups** | Buy/sell communities | Cluttered with spam. No neighborhood filtering. No structured shop profiles. Scam-heavy. |
| **Word of Mouth** | Personal recommendations | Limited reach. Doesn't scale. No way to discover new shops outside your network. |

### Market Size

- **Merchants:** Hundreds of thousands of SMEs across retail (electronics, clothing, footwear), local services, and food/beverage in urban centers like Addis Ababa.
- **Users:** Millions of daily active Telegram users in Ethiopia. Telegram is virtually synonymous with the consumer internet in the country.

### Why Telegram (Not WhatsApp or Standalone App)

- **Dominance & Habit:** Telegram is the default social, news, and informal commerce app in Ethiopia. WhatsApp has significantly lower market share.
- **Mini App Ecosystem:** Telegram Mini Apps run seamlessly inside the app, leveraging existing chat UI, user context, and instant notifications — no app store download required.
- **Distribution:** Zero-friction onboarding. Users click a link, the Mini App opens inside Telegram. No 50MB download, no registration, no new account.

---

## Merchant Experience Deep Dive

### 1. What Does a Merchant's Daily Life Look Like on Telegram Right Now?

**The Current Workflow:**

Merchants run a Telegram channel where they post product photos with prices in the caption, typically formatted like:

```
📱 iPhone 15 Pro Max
💰 Price: 85,000 Birr
📍 Piazza, near Hotel XYZ
📞 @username or 09XX XXX XXX
```

They're also members of 3-5 buy/sell groups where they cross-post the same items. They spend 2-3 hours a day reposting, responding to DMs, and negotiating. Their "catalog" is their channel's post history — scroll up to see what's available.

**What This Means for TeleDirectory:**

You're not replacing their channel. You're making it *discoverable*. The merchant keeps doing what they're doing, but now there's a structured layer on top that brings in new customers they'd never reach through their existing channel alone.

**Key Design Implication:** Don't ask merchants to maintain a separate catalog in TeleDirectory. Let them import from their existing channel. The tool should feel like an amplifier, not another job.

### 2. What's the Merchant's "Aha Moment"?

**It's the first customer message that says "I found you on TeleDirectory."**

That's it. Everything before that — setting up a profile, getting verified — is just setup. The moment a merchant gets a lead they *wouldn't have gotten otherwise*, the value clicks.

**What to Optimize For:**

- Get their profile live in under 5 minutes
- Push their listing into search results immediately (not after some approval queue)
- Show them a dashboard: "X people viewed your profile today" — even if X is 3

**The Psychological Hook:** Merchants are competitive. If they see that a neighboring shop got 50 views and they got 5, they'll upgrade, optimize, and engage without being asked.

### 3. How Do Merchants Handle Inventory/Catalog Today?

**Answer: Photos in a Telegram channel. That's it.**

No spreadsheet. No structured data. Just a stream of product images with prices in the caption. Maybe a pinned message with contact info and location.

**What This Means for "Updates & Catalog":**

Don't build a complex inventory management system. That's solving a problem merchants don't have. Instead:

- **Phase 1:** Let merchants post updates (text + photo) that show up on their profile, like a mini feed. Simple, familiar, mirrors what they already do in their channel.
- **Phase 1.5:** Let them link their Telegram channel and auto-import posts as catalog items.
- **Phase 2:** Add structured catalog fields (price, availability, category) as an optional enhancement for merchants who want better search visibility.

**The Principle:** Meet merchants where they are. Don't teach them a new workflow — amplify the one they already have.

---

## Consumer Experience Deep Dive

### 4. What's the Typical Search Intent?

**All three modes exist, but in a specific order of frequency:**

1. **Location-first (Most Common):** "What's in Bole?" or "Shops near Piazza" — the user is in an area and wants to know what's around them. Addis is a city where you *go to* a commercial area to shop.
2. **Category-second:** "Electronics shops" or "clothing stores" — the user knows what they need but not where.
3. **Product-third (Highest Purchase Intent):** "iPhone 15 case" or "wedding dress" — specific item search. Less common but highest conversion potential.

**Search UX Implications:**

- **Default view should be location-based.** When someone opens the app, show shops near popular areas first, not a blank search bar.
- **Search bar supports all three modes,** but the UI should make location browsing effortless (tap a neighborhood → see categories → see shops).
- **Quick filter tags** at the top: `[Piazza]` `[Bole]` `[Kazanchis]` `[Electronics]` `[Clothing]` `[Services]` — one tap to filter.

**Mental Model:** "What's around here?" first, "What has what I need?" second.

### 5. How Do Users Decide Which Merchant to Contact?

**Decision Factors (In Order of Importance):**

1. **Proximity/Location** — "Is this shop in an area I can actually get to?" In Addis, where traffic is brutal, this matters more than anything.
2. **Trust Badge** — "Is this a real shop or a scam?" The verification badge is the primary trust signal in a market where fake listings are common.
3. **Product Availability** — "Do they actually have what I'm looking for right now?" A shop that posted 2 hours ago feels more alive than one that hasn't updated in weeks.
4. **Price** — Important, but secondary to trust and proximity.
5. **Reviews/Ratings** — Nice to have, but less critical in Phase 1.

**What to Surface on Result Cards:**

- Shop name + logo (identity)
- Area tag: "📍 Bole" (proximity)
- Verification badge: ✓ (trust)
- Last active: "Updated 2h ago" (freshness)
- Category tag: "Electronics" (relevance)

**Save for Profile View:** Full catalog, prices, ratings. Keep cards scannable.

### 6. Is There a Repeat-Use Case?

**Yes, but different from e-commerce patterns:**

- **Discovery phase:** User finds 2-3 electronics shops in Bole through TeleDirectory.
- **Relationship phase:** They contact one, buy something, and now they *know* that shop. They saved the Telegram chat.
- **Repeat phase:** Next time they need electronics, they either go back to that shop directly (from Telegram chat history) OR they come back to TeleDirectory to compare options.

**TeleDirectory's repeat value is in discovery, not transactions.** Users come back when they need something *new* — a new category, a new area, a comparison.

**Retention Feature Priority:**

1. **Favorites/Bookmarks** — Let users save shops they've had good experiences with.
2. **Search History** — Quick access to previous searches.
3. **Deal Notifications** — If a bookmarked shop posts a promotion, notify the user.

**Investment Priority:** Favorites > Search history > Push notifications. Get discovery right first.

---

## Competitive Landscape & Scam Analysis

### 7. Existing Attempts in Ethiopia

| Attempt | Format | Why It Failed/Partial |
|---------|--------|----------------------|
| **Telegram Bots** | Chat-based directory interfaces | Feel like talking to a spreadsheet. No visual profiles, no browsable categories, no trust signals. Works for power users, fails for mass adoption. |
| **Listing Websites** | Desktop-first directories | Outdated, no mobile optimization, merchants don't update. Become digital graveyards. |
| **Facebook Marketplace/Groups** | Unstructured buy/sell communities | Huge volume but no verification, no location filtering, scam-heavy. Works *despite* the UX, not because of it. |

**Why They Failed:** They either solved directory without solving trust, or solved trust without solving discovery. Nobody combined structured search + verification + Telegram-native experience.

**TeleDirectory's Advantage:** Not building a new platform. Building a *layer* on top of the platform people already use. Fundamentally different distribution strategy.

### 8. The Scam Landscape

**The Typical Scam:**

1. Someone creates a Telegram channel with stolen product photos (electronics, clothing, etc.)
2. Posts at prices 20-30% below market to attract buyers
3. Asks for partial or full payment via mobile money (TeleBirr, CBE Birr) before delivery
4. Disappears. Or sends a counterfeit/empty box.

**The Variant:** A "shop" that's actually a middleman. Takes your order, buys the item from somewhere else at lower quality, pockets the difference. No accountability.

**What Verification Needs to Solve:**

| Tier | Method | What It Proves |
|------|--------|---------------|
| **Tier 1 (Digital)** | Confirm phone number is real and active. Confirm they own the claimed Telegram channel. Cross-reference with known scam databases. | This is a real, reachable person. |
| **Tier 2 (Physical)** | Verify physical location. Photo of storefront with TeleDirectory-branded sign/QR code. | This is a real business with a physical presence. |
| **Tier 3 (Community)** | Verified customer reviews over time. | This business has a track record. |

**Key Insight:** Verification isn't a one-time gate. It's an ongoing trust score that compounds. Start simple, get more sophisticated over time.

---

## Business Model & Monetization

### 9. Pricing Strategy

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Basic listing: shop name, category, location, contact button. No badge. No promotion. |
| **Verified Badge** | ~$3-5/month (~$30-50/year) | Trust badge visible in search results. Priority in category listings. Basic analytics dashboard. |
| **Promoted Listing** | ~$5-10/month | Appear at the top of a specific category + location combination. "Top of Electronics in Bole." |
| **Featured Banner** | ~$10-20/week | Spot on the discovery feed. Seasonal/event-driven (holiday sales, back-to-school, etc.). |

**Pricing Rationale:**

- Ethiopian SMEs are price-sensitive but not broke. A shop doing $500-2000/month in revenue can afford $5/month for customer acquisition.
- Cheaper than a single Facebook ad, more targeted, with measurable results.
- Price in Ethiopian Birr for the local market. Show USD equivalents for reference.

**Strategic Pricing Principle:** Start lower than you think. Getting 1000 merchants at $3/month ($3000 MRR) is better than 50 merchants at $20/month ($1000 MRR). Volume builds the moat.

### 10. Free-to-Paid Conversion Strategy

**The Trigger: Visibility Competition.**

The conversion journey:

1. Merchant signs up for free. Gets listed. Gets a few views.
2. Dashboard shows: "You appeared in 15 searches this week. 3 people viewed your profile."
3. They notice a competitor with a Verified badge appeared in 45 searches and got 12 views.
4. They think: "I'm losing customers to this guy because he has a badge and I don't."
5. They upgrade.

**What Makes This Work:**

- **Show competitive intelligence.** Don't just show *their* stats — show how they compare to similar shops (anonymized). "Shops like yours average 50 views/week. You're at 15."
- **Make the badge visible and desirable.** Show it prominently in search results. Make unbadged listings feel slightly inferior (not hidden, just less trustworthy-looking).
- **Offer a free trial of premium.** Give every merchant 7 days of Verified status for free. Let them feel the difference in views/messages. Then take it away. Loss aversion does the rest.

**Critical Rule:** Don't artificially suppress free listings. That's coercive and kills trust. Free listings should work fine — paid listings should just work *better*.

---

## Technical Execution & Team

### 11. Team Composition

**Minimum Viable Team for MVP:**

| Role | Count | Responsibilities |
|------|-------|-----------------|
| **Full-Stack Developer** | 1 | Telegram WebApp SDK, React/Vue frontend, Node.js/Python backend, PostgreSQL, Redis. Builds Mini App, API, and admin tools. |
| **On-the-Ground Operator** | 1 | Merchant onboarding, data collection, physical verification. Knows target neighborhoods. Walks into shops, takes photos, collects info. |
| **Founder/Product** | 0.5 (part-time) | UX decisions, visual identity, product direction, business development. |

**If Solo Project:** The dev also handles data collection. Slower progress but viable. Expect 2-3x the timeline.

**What You Don't Need Yet:** A dedicated designer (use a clean template), marketer (Telegram Mini Apps spread virally), data scientist, or DevOps person.

### 12. Recommended Tech Stack

```
Frontend:
├── Telegram WebApp SDK (core integration)
├── React or Vue 3 (UI framework)
├── Tailwind CSS (mobile-first styling)
└── PWA capabilities (offline fallback)

Backend:
├── Node.js (Express/Fastify) or Python (FastAPI)
├── PostgreSQL (primary database — shops, users, categories)
├── Redis (caching layer — sub-second search results)
└── Telegram Bot API (notifications, merchant communication)

Infrastructure:
├── Any cloud provider (AWS, GCP, DigitalOcean, or local)
├── CDN for shop images
└── Basic CI/CD pipeline
```

---

## Data Collection Strategy

### 12. Detailed Data Collection Plan

**Phase 1 — Manual + Scraping (Weeks 1-3):**

| Method | Target | Volume | Approach |
|--------|--------|--------|----------|
| **Street Survey** | Piazza, Bole | 200-500 shops | Walk commercial streets. Photograph shops. Note names, categories, phone numbers, GPS coordinates. |
| **Telegram Channel Scraping** | Public commerce channels | 500-1000 listings | Extract business names, contact info, categories from public channels listing shops/products in Addis. |
| **Public Registry Cross-Reference** | Available business registries | As accessible | Match scraped data against any public Ethiopian business registration data. |

**Phase 2 — Merchant Self-Submission (Week 3+):**

- Launch "Add Your Shop" button in the Mini App
- Simple form: name, category, location, phone, photo
- On-the-ground person verifies new submissions by visiting or calling

**Legal & Ethical Considerations:**

- Scraping public Telegram channels is generally legal (public data), but don't scrape private groups or personal data.
- Don't republish merchant data without their knowledge — use scraped data to *initiate contact* and invite merchants to claim their listing.
- Have a clear takedown process. If a merchant wants their listing removed, do it immediately.

**The Principle:** Scrape to seed, but quickly transition to merchant-owned data. The goal is for merchants to *want* to be on the platform.

---

## Strategic Recommendations

### What's Strongest

1. **Market timing is right.** Ethiopia's digital commerce is at the "organized chaos" stage. Telegram channels are booming but unstructured. You're not creating demand — you're organizing existing demand.

2. **Verification as a product, not a feature.** In a market where online scams are common, the trust badge isn't decoration — it's the core value proposition. This is defensible because trust compounds over time.

3. **Bootstrapping strategy is smart.** Scraping public Telegram commerce channels to pre-populate the directory solves the cold-start problem without manual onboarding of hundreds of merchants.

### What to Watch Out For

1. **Don't try to be everything on day one.** One city, two categories, get density right before expanding. A thin directory across everything is worse than a rich directory in one niche.

2. **Merchant self-onboarding should be in Phase 1, not Phase 2.** Even a simple "add your shop" flow prevents the platform from being bottlenecked by manual data collection.

3. **Don't build complex inventory management.** Merchants don't have this problem. Let them post updates like they do in their channels. Simple beats sophisticated.

### Feature to Consider: Merchant Channel Integration

Let merchants **link their existing Telegram channel** and have TeleDirectory auto-parse and structure their catalog from channel posts. This would:

- Dramatically reduce merchant onboarding friction
- Keep catalogs fresh automatically (as they post to their channel, TeleDirectory updates)
- Create a powerful reason for adoption ("it's not yet another thing to manage — it makes my existing thing work better")

**Timing:** Phase 1.5 — right after launch, before full self-service catalog management.

---

## Next Steps

### Immediate Actions

1. **Validate assumptions** — Spend 2-3 days in Piazza and Bole talking to merchants. Confirm the daily workflow, pricing tolerance, and pain points described above.
2. **Lock in MVP scope** — Define exactly what's in Phase 1 and what's deferred.
3. **Build technical spec** — Detailed architecture doc that a developer can pick up and start building from.
4. **Define first sprint** — What gets built in week 1, week 2, week 3.

### MVP Scope Recommendation

**IN (Phase 1):**
- Search by location + category + keyword
- Shop profile pages with contact buttons
- Basic verification (Tier 1 — digital check)
- Simple "Add Your Shop" self-submission
- Shop update feed (text + photo)
- Favorites/bookmarks

**OUT (Phase 1.5+):**
- Merchant channel auto-import
- Promoted listings / paid features
- Ratings & reviews
- Advanced analytics dashboard
- Payment integration
- Push notifications for deals

---

*This document is a living reference. Update as assumptions are validated or invalidated through market research and user conversations.*
