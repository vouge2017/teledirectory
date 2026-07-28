# TeleDirectory — Ground Operations & Data Scraping Guide

**Version:** 1.0
**Date:** 2026-07-29
**Status:** Ready for Execution

---

## 1. Data Collection — Phase 1 Seeding

### 1.1 Telegram Channel Scraping

**Objective:** Pre-populate TeleDirectory with 500+ shop listings from public Telegram commerce channels before launch.

**Tools Required:**
- Python 3.10+
- Telethon library (`pip install telethon`)
- A Telegram account (not a bot — user account for client API access)
- API credentials from https://my.telegram.org

**Target Channels (First 50):**

#### Piazza Area (Jewelry, Watches, Electronics)

| # | Channel Type | Search Keywords | Expected Channels |
|---|-------------|----------------|-------------------|
| 1 | Electronics shops | "Piazza electronics", "ፒያሳ ኤሌክትሮኒክስ", "phone Piazza" | 10-15 |
| 2 | Jewelry & watches | "Piazza jewelry", "Piazza watch", "珠宝" | 8-12 |
| 3 | General commerce | "Piazza shop", "Piazza market", "buy sell Piazza" | 5-8 |
| 4 | Clothing | "Piazza clothing", "Piazza fashion", "dress Piazza" | 5-8 |

#### Bole Area (Fashion, Electronics, Services)

| # | Channel Type | Search Keywords | Expected Channels |
|---|-------------|----------------|-------------------|
| 5 | Fashion & clothing | "Bole fashion", "Bole clothing", "Bole boutique" | 10-15 |
| 6 | Electronics | "Bole electronics", "Bole phone", "laptop Bole" | 8-10 |
| 7 | Beauty & services | "Bole beauty", "Bole salon", "Bole gym" | 5-8 |
| 8 | Food & restaurants | "Bole food", "Bole restaurant", "delivery Bole" | 5-8 |

#### Cross-Area (City-Wide)

| # | Channel Type | Search Keywords | Expected Channels |
|---|-------------|----------------|-------------------|
| 9 | Buy/sell groups | "Addis buy sell", "Ethiopia market", "shop Addis" | 10-15 |
| 10 | Specific products | "iPhone Ethiopia", "laptop Addis", "car parts Ethiopia" | 5-10 |

**How to Find Channels:**

```
Method 1: Telegram Search
├── Open Telegram
├── Search: "Addis shop" / "Piazza electronics" / "buy sell Ethiopia"
├── Filter by: Channels
└── Note: channel username, subscriber count, post frequency

Method 2: Google Search
├── site:t.me "Addis Ababa" shop
├── site:t.me "Piazza" electronics
└── site:t.me Ethiopia buy sell

Method 3: Existing Channel Mining
├── Find one good commerce channel
├── Check its "similar channels" recommendation
├── Check forwarded posts (original channels)
└── Follow the network
```

**Channel Evaluation Criteria:**

| Criteria | Good | Skip |
|----------|------|------|
| Subscriber count | 500+ | < 100 |
| Post frequency | Daily/weekly | No posts in 30+ days |
| Content quality | Product photos + prices + contact | Spam, unrelated content |
| Business type | Actual shops/makers | Resellers, middlemen |
| Public access | Open channel | Private/invite-only |

### 1.2 Scraper Execution Plan

**Week 1: Setup & First Scrape**

```
Day 1-2: Setup
├── Create Telegram API credentials (my.telegram.org)
├── Install Telethon, configure environment
├── Test connection with 1-2 known channels
└── Set up PostgreSQL staging table (scraped_messages)

Day 3-5: First Scrape Batch
├── Scrape first 20 channels (Piazza-heavy)
├── Expected yield: 200-400 unique messages
├── Extract: shop names, prices, phone numbers, images
└── Review data quality, tune regex patterns

Day 6-7: Second Scrape Batch
├── Scrape next 20 channels (Bole-heavy)
├── Expected yield: 300-500 unique messages
├── ETL: Create shop records from channel groupings
└── Tag each channel with location + category
```

**Week 2: Refine & Expand**

```
Day 8-10: Data Cleaning
├── Deduplicate shops across channels
├── Normalize phone numbers (+251 format)
├── Validate extracted prices
├── Assign locations and categories
└── Generate shop slugs

Day 11-14: Final Scrape + Enrichment
├── Scrape remaining 10 channels
├── Manual review: flag low-quality extractions
├── Enrich: add descriptions, fix names, tag categories
└── Target: 500+ clean shop records ready for launch
```

### 1.3 Scraper Output Template

For each scraped channel, create a record:

```json
{
    "channel_username": "@PiazzaPhoneShop",
    "channel_title": "Piazza Phone & Accessories",
    "subscriber_count": 3420,
    "location_tag": "piazza",
    "category_tag": "electronics",
    "message_count": 87,
    "extracted_shops": [
        {
            "name": "Piazza Phone & Accessories",
            "phone": "+251911234567",
            "telegram": "@PiazzaPhoneShop",
            "sample_posts": 87,
            "price_range": "500-85000 ETB",
            "products": ["iPhone cases", "Samsung chargers", "screen protectors"]
        }
    ]
}
```

---

## 2. Street Survey Operations

### 2.1 Objective

Manually collect 200-500 shop listings by walking commercial areas in Piazza and Bole. This captures shops that don't have a Telegram presence yet — critical for directory density.

### 2.2 Survey Equipment

| Item | Purpose |
|------|---------|
| Smartphone with camera | Shop photos, GPS coordinates |
| Telegram app | Test if shop has a channel/username |
| Google Maps / OSMAnd | Pin locations, navigate areas |
| Notebook / Google Sheets | Offline data capture |
| Power bank | Full-day surveying |
| TeleDirectory QR card (print) | Leave with merchants for Phase 2 |

### 2.3 Data Points Per Shop

| Field | Required | How to Collect |
|-------|----------|---------------|
| Shop name | ✅ | Read signboard / ask owner |
| Photo (exterior) | ✅ | Take photo of storefront |
| Photo (interior) | Optional | Ask permission, take 1-2 photos |
| Phone number | ✅ | Ask owner / read posted number |
| Telegram username | ✅ | Ask: "Do you have a Telegram channel?" |
| Category | ✅ | Observe / ask: "What do you sell?" |
| Location name | ✅ | Record area (Piazza, Bole, etc.) |
| Address detail | ✅ | "Near [landmark], [street]" |
| GPS coordinates | ✅ | Phone GPS at storefront |
| Owner/manager name | Optional | Ask for first name |
| Business hours | Optional | Ask or observe posted hours |
| Has existing Telegram channel? | ✅ | Yes/No + channel name if yes |

### 2.4 Survey Route Plan

#### Piazza (Target: 150-250 shops)

```
Route 1: Main Piazza Commercial Street
├── Start: Piazza roundabout
├── Walk: South along main road
├── Focus: Electronics, jewelry, watch repair
├── Expected: 50-80 shops
└── Duration: 3-4 hours

Route 2: Piazza Side Streets
├── Start: Piazza roundabout
├── Walk: East side streets
├── Focus: Clothing, shoes, accessories
├── Expected: 40-60 shops
└── Duration: 2-3 hours

Route 3: Piazza Market Area
├── Start: Central market entrance
├── Walk: Through market sections
├── Focus: Mixed retail (food, household, clothing)
├── Expected: 60-100 shops
└── Duration: 3-4 hours
```

#### Bole (Target: 150-250 shops)

```
Route 4: Bole Road (Main Strip)
├── Start: Bole Medhanealem
├── Walk: Along Bole Road toward Bole Bridge
├── Focus: Fashion boutiques, electronics, restaurants
├── Expected: 60-80 shops
└── Duration: 3-4 hours

Route 5: Bole Side Streets & Atlas Area
├── Start: Bole Road junction
├── Walk: Side streets toward Atlas Hotel area
├── Focus: Services, beauty, small retail
├── Expected: 40-60 shops
└── Duration: 2-3 hours

Route 6: Bole Michael Area
├── Start: Bole Michael roundabout
├── Walk: Surrounding commercial blocks
├── Focus: Electronics, mobile accessories, clothing
├── Expected: 50-70 shops
└── Duration: 3-4 hours
```

### 2.5 Survey Data Entry Template

**Google Sheets columns:**

| Column | Example |
|--------|---------|
| timestamp | 2026-07-30 10:15 |
| surveyor_name | Dawit |
| shop_name | Selam Electronics |
| photo_filename | IMG_20260730_101523.jpg |
| phone | 0911234567 |
| telegram_handle | @SelamElectronics |
| has_telegram_channel | Yes |
| channel_name | @SelamElectronicsShop |
| category | Electronics |
| location | Piazza |
| address_detail | Near Piazza roundabout, 2nd floor, blue building |
| gps_lat | 9.0320 |
| gps_lng | 38.7468 |
| owner_name | Ato Selam |
| business_hours | 8:00 AM - 7:00 PM |
| notes | Large selection of phone accessories |

---

## 3. Verification Operations

### 3.1 Tier 1 — Digital Verification (Automated)

**Runs automatically when a shop is submitted or claimed.**

| Check | Method | Pass Criteria |
|-------|--------|--------------|
| Phone number valid | Regex: `+251[97]\d{8}` or `0[97]\d{8}` | Valid Ethiopian mobile format |
| Phone number active | Optional: TeleBirr/API check or SMS ping | Number is reachable |
| Telegram channel exists | Telegram API: check channel_username | Channel is public and accessible |
| Channel ownership | Verification bot: user messages from channel owner account | Bot confirms ownership |
| Not blacklisted | Check against known scam database | No prior reports |

**Automation:**
```
On shop submission:
1. Validate phone format → auto-fail if invalid
2. Check if Telegram channel exists → auto-fail if not found
3. If claimed: verify channel ownership via bot → auto-approve if confirmed
4. Flag for manual review if any check is ambiguous
```

### 3.2 Tier 2 — Physical Verification (Ground Team)

**Manual process. Ground operator visits or calls.**

| Step | Action | Tool |
|------|--------|------|
| 1 | Call the shop's phone number | Phone call |
| 2 | Confirm: "Is this [Shop Name] at [Address]?" | Script |
| 3 | Ask: "Do you have a shop at [Location]?" | Script |
| 4 | Request a photo of the storefront | WhatsApp/Telegram |
| 5 | Cross-reference with street survey data | Database check |
| 6 | If all checks pass → approve Tier 2 | Admin panel |

**Physical Visit Checklist (When Feasible):**

```
□ Arrive at recorded address
□ Confirm shop exists and matches name
□ Photograph storefront (with TeleDirectory QR sticker if available)
□ Note actual business hours
□ Speak with owner/manager
□ Confirm product categories match listing
□ Leave TeleDirectory promotional card
□ Record GPS coordinates (more accurate than survey estimate)
□ Note any discrepancies with database record
```

### 3.3 Verification Sticker/QR Template

**Print and distribute during Tier 2 visits.**

```
┌─────────────────────────────────┐
│                                 │
│    ✓ VERIFIED on TeleDirectory  │
│                                 │
│    ┌───────────────────────┐    │
│    │                       │    │
│    │      [QR CODE]        │    │
│    │   Links to shop       │    │
│    │   TeleDirectory       │    │
│    │   profile             │    │
│    │                       │    │
│    └───────────────────────┘    │
│                                 │
│    Find us on Telegram:         │
│    t.me/TeleDirectoryBot        │
│                                 │
└─────────────────────────────────┘

Size: 10cm x 10cm (sticker) or 8cm x 12cm (card)
Material: Waterproof vinyl sticker OR laminated card
Placement: Storefront window or counter
```

---

## 4. Merchant Outreach

### 4.1 "Claim This Shop" Outreach Script

**When:** After pre-populating the directory with scraped data, reach out to channel owners to claim their listings.

**Medium:** Telegram message (to channel admin or posted in channel)

#### Template 1 — Direct Message to Channel Owner

```
👋 Hello {Shop Name}!

Your shop has been listed on TeleDirectory — a new Telegram Mini App 
that helps customers in Addis Ababa find verified local shops.

📱 Your listing: {teleDirectory URL}
✓ You can claim and manage your shop profile for free.

To claim your shop:
1. Open TeleDirectory: {miniApp URL}
2. Tap "Claim This Shop"
3. Verify you own @{channel_username}

Benefits:
• Customers find you when searching for {category} in {location}
• Verified badge builds trust
• Free analytics: see how many people view your shop

Questions? Reply here or message @TeleDirectorySupport.
```

#### Template 2 — Channel Post (If Accessible)

```
📢 Attention Shop Owners!

TeleDirectory is launching — a Telegram Mini App where customers 
search for local shops by location and category.

If your shop is listed, you can claim your profile for free and get:
✓ Verified badge
✓ Direct customer leads
✓ View & contact analytics

Open TeleDirectory → tap "Claim This Shop" → verify your channel.

🔗 {miniApp URL}

#TeleDirectory #AddisAbaba #ShopLocal
```

#### Template 3 — In-Person (During Street Survey)

```
"Hello! I'm from TeleDirectory — it's a new feature inside Telegram 
that helps people find shops like yours. Customers can search for 
{category} in {location} and find your shop directly.

I'd like to add your shop to the directory. Can I take a photo and 
note your contact details? It's free.

Later, you can claim your profile and get a verified badge that shows 
customers you're a real, trusted shop. Would you like that?"
```

### 4.2 Outreach Tracking

**Google Sheet columns:**

| Column | Purpose |
|--------|---------|
| shop_name | Target shop |
| channel_username | Telegram channel |
| outreach_date | When contacted |
| outreach_method | DM / Channel post / In-person |
| response | No response / Interested / Claimed / Declined |
| claimed_date | When they claimed |
| notes | Follow-up notes |

### 4.3 Outreach Targets — Week 1

| Day | Target | Method | Volume |
|-----|--------|--------|--------|
| Day 1 | Top 10 scraped channels (by subscribers) | Telegram DM | 10 messages |
| Day 2 | Next 15 scraped channels | Telegram DM | 15 messages |
| Day 3 | Street survey shops with Telegram presence | In-person | 20 conversations |
| Day 4 | Follow up Day 1-2 non-responders | Telegram DM | 10 follow-ups |
| Day 5 | Street survey shops without Telegram | In-person | 20 conversations |
| Day 6-7 | Review claims, process verifications | Admin | All pending |

---

## 5. Launch Week Playbook

### Week 1-2: Pre-Launch Prep

```
□ Developer: Set up Telegram Bot + Mini App scaffold
□ Developer: Implement search + shop profile pages
□ Developer: Set up PostgreSQL + Redis
□ Ground: Complete first 20-channel scrape (200+ shops)
□ Ground: Begin street survey Route 1 (Piazza main)
□ Founder: Design logo, color scheme, basic UI mockups
□ Founder: Set up TeleDirectory Telegram bot account
```

### Week 3-4: Core Build + Data Ingestion

```
□ Developer: Implement contact buttons with pre-filled messages
□ Developer: Implement "Claim This Shop" flow
□ Developer: Implement "Add Your Shop" form
□ Ground: Complete street survey all routes (400+ shops)
□ Ground: Complete all 50-channel scrape
□ Ground: Begin merchant outreach (top 25 channels)
□ Founder: Create verification sticker/QR design
□ Founder: Print verification stickers (100 units)
```

### Week 5: Integration + Soft Launch

```
□ Developer: Connect all pages to live data
□ Developer: Implement favorites
□ Developer: Implement basic merchant dashboard
□ Ground: Continue merchant outreach (50 more)
□ Ground: Begin Tier 2 verification visits (top 20 shops)
□ Founder: Test full flow: search → profile → contact
□ Founder: Fix bugs, polish UI
□ Soft launch: Invite 50 merchants to claim profiles
□ Soft launch: Share with 100 test users
```

### Week 6: Public Launch

```
□ Developer: Monitor performance, fix issues
□ Developer: Optimize Redis caching based on real traffic
□ Ground: Continue verification visits
□ Ground: Onboard new self-submitted shops
□ Founder: Share Mini App link in major Telegram commerce groups
□ Founder: Post in Addis Ababa community channels
□ Founder: Collect feedback, prioritize fixes
□ Target: 300+ listed shops, 1000+ users
```

---

## 6. Budget Estimate (Phase 1 — 6 Weeks)

| Item | Cost (ETB) | Cost (USD) | Notes |
|------|-----------|-----------|-------|
| Cloud hosting (1 month) | — | $20-50 | DigitalOcean / AWS |
| Telegram API credentials | Free | Free | From my.telegram.org |
| Domain name | — | $10-15 | .com or .et |
| Street survey transport | 2,000-3,000 | $15-25 | Local transport for surveyor |
| Printing (QR stickers, cards) | 1,500-2,500 | $12-20 | 100 stickers + 200 cards |
| Surveyor compensation | 5,000-10,000 | $40-80 | 2 weeks of ground work |
| Mobile data (scraper + surveyor) | 500-1,000 | $4-8 | Data bundles |
| Miscellaneous | 1,000-2,000 | $8-16 | Unexpected expenses |
| **Total Phase 1** | **10,000-18,500** | **$80-150** | Excluding developer time |

---

## 7. Key Metrics to Track (Week 1-6)

| Metric | Week 1 Target | Week 4 Target | Week 6 Target |
|--------|--------------|---------------|---------------|
| Shops scraped | 200 | 500 | 500+ |
| Shops from street survey | 50 | 300 | 400+ |
| Channels contacted | 0 | 30 | 50 |
| Shops claimed | 0 | 20 | 50+ |
| Tier 1 verified | 100 | 300 | 400+ |
| Tier 2 verified | 0 | 10 | 20+ |
| Active users | 0 | 200 | 1,000+ |
| Searches performed | 0 | 500 | 2,000+ |
| Contact taps (leads) | 0 | 50 | 200+ |

---

*Pair this document with `teleDirectory-srs.md` (technical requirements) and `teleDirectory-unified-strategy.md` (product strategy) for the complete execution package.*
