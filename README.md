# TeleDirectory

A Telegram Mini App that organizes Ethiopia's fragmented informal commerce into a searchable, verified, neighborhood-organized business directory.

## Vision

Telegram is where Ethiopian consumers and merchants already live. TeleDirectory puts a structured, trusted directory *inside* the app people use all day — no behavior change needed, just better organization of existing commerce.

## Target Market

- **Location:** Addis Ababa (starting with Piazza + Bole)
- **Categories:** Electronics, Clothing & Fashion, Jewelry & Watches, Services
- **Users:** Millions of daily Telegram users in Ethiopia
- **Merchants:** Hundreds of thousands of SMEs in urban Addis Ababa

## Revenue Model

| Tier | Price (ETB/month) | Features |
|------|-------------------|----------|
| Free | 0 | Basic listing, contact button |
| Verified | 500–800 | Trust badge, priority in search, analytics |
| Promoted | 800–1,500 | Top of category + location search |
| Featured Banner | 1,000–2,000/week | Discovery feed placement |

## Tech Stack

- **Frontend:** Telegram WebApp SDK + React/Vue + Tailwind CSS
- **Backend:** Node.js (Express) or Python (FastAPI)
- **Database:** PostgreSQL (full-text search) + Redis (caching)
- **Data Pipeline:** Telethon/Pyrogram for public channel scraping
- **Bot:** Telegram Bot API for notifications and merchant verification

## Documents

| Document | Description |
|----------|-------------|
| [Strategy](teleDirectory-unified-strategy.md) | Product vision, market analysis, business model, roadmap |
| [SRS](teleDirectory-srs.md) | Technical requirements — database schemas, API endpoints, SDK integration, scraper specs |
| [Ground Operations](teleDirectory-ground-operations.md) | Data collection plan, street survey routes, verification checklists, merchant outreach, launch playbook |
| [Strategic Q&A](teleDirectory-strategic-qa.md) | Detailed Q&A on merchant/consumer experience, competitive landscape, pricing |

## 6-Week Launch Plan

| Week | Focus |
|------|-------|
| 1 | Setup: Telegram API creds, scraper dev, begin channel scraping |
| 2 | Data: Complete 50-channel scrape, begin street surveys |
| 3 | Build: Core search + shop profiles + contact buttons |
| 4 | Build: Claim This Shop + Add Your Shop + merchant dashboard |
| 5 | Integration: Connect all pages to live data, soft launch with 50 merchants |
| 6 | Launch: Public release, share in Telegram commerce groups |

## Key Features (MVP)

- [x] Search by item keyword + location + category
- [x] Shop profiles with tap-to-call and tap-to-message
- [x] Pre-filled message attribution ("I found you on TeleDirectory")
- [x] Tier 1 verification (digital: phone + channel ownership)
- [x] "Claim This Shop" for pre-indexed merchants
- [x] "Add Your Shop" self-submission
- [x] Shop update feed (text + photo)
- [x] Favorites / Saved Shops
- [x] Basic merchant analytics dashboard

## License

Proprietary — All rights reserved.
