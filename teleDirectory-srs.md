# TeleDirectory — Software Requirements Specification (SRS)

**Version:** 1.0
**Date:** 2026-07-29
**Platform:** Telegram Mini App (TMA)
**Stack:** Node.js/Python + PostgreSQL + Redis + Telegram WebApp SDK

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────┐
│                  Telegram Client                     │
│  ┌───────────────────────────────────────────────┐  │
│  │           TeleDirectory Mini App              │  │
│  │  (Telegram WebApp SDK + React/Vue + Tailwind) │  │
│  └──────────────────┬────────────────────────────┘  │
└─────────────────────┼───────────────────────────────┘
                      │ HTTPS (JSON API)
                      ▼
┌─────────────────────────────────────────────────────┐
│                  API Server                          │
│         (Node.js Express / Python FastAPI)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Auth     │  │ Search   │  │ Merchant         │  │
│  │ Module   │  │ Engine   │  │ Module           │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└───────┬──────────────┬──────────────────┬───────────┘
        │              │                  │
        ▼              ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│  PostgreSQL  │ │    Redis     │ │  Telegram Bot    │
│  (Primary DB)│ │  (Cache +    │ │  API             │
│              │ │   Search     │ │  (Notifications, │
│              │ │   Index)     │ │   Claim Flow)    │
└──────────────┘ └──────────────┘ └──────────────────┘

┌──────────────────────────────────────────────────────┐
│              Data Ingestion Pipeline                  │
│  Telethon/Pyrogram Scraper → ETL → PostgreSQL        │
└──────────────────────────────────────────────────────┘
```

---

## 2. Database Schema (PostgreSQL)

### 2.1 Core Tables

```sql
-- ============================================
-- LOCATIONS
-- ============================================
CREATE TABLE locations (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,       -- "Piazza", "Bole", "Kazanchis"
    slug            VARCHAR(100) UNIQUE NOT NULL, -- "piazza", "bole"
    parent_city     VARCHAR(100) DEFAULT 'Addis Ababa',
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    is_active       BOOLEAN DEFAULT TRUE,
    display_order   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Seed: INSERT INTO locations (name, slug, display_order) VALUES
--   ('Piazza', 'piazza', 1),
--   ('Bole', 'bole', 2),
--   ('Kazanchis', 'kazanchis', 3),
--   ('Merkato', 'merkato', 4);

-- ============================================
-- CATEGORIES
-- ============================================
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,       -- "Electronics", "Clothing"
    slug            VARCHAR(100) UNIQUE NOT NULL, -- "electronics", "clothing"
    icon_emoji      VARCHAR(10),                 -- "📱", "👕"
    parent_id       INTEGER REFERENCES categories(id), -- for subcategories
    is_active       BOOLEAN DEFAULT TRUE,
    display_order   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Seed: INSERT INTO categories (name, slug, icon_emoji, display_order) VALUES
--   ('Electronics', 'electronics', '📱', 1),
--   ('Clothing & Fashion', 'clothing', '👕', 2),
--   ('Jewelry & Watches', 'jewelry', '💍', 3),
--   ('Food & Grocery', 'food', '🛒', 4),
--   ('Services', 'services', '🔧', 5),
--   ('Home & Furniture', 'home', '🏠', 6);

-- ============================================
-- SHOPS (Core Entity)
-- ============================================
CREATE TABLE shops (
    id              SERIAL PRIMARY KEY,
    
    -- Identity
    name            VARCHAR(200) NOT NULL,
    slug            VARCHAR(200) UNIQUE NOT NULL,
    description     TEXT,
    logo_url        VARCHAR(500),
    cover_image_url VARCHAR(500),
    
    -- Location
    location_id     INTEGER REFERENCES locations(id),
    address_detail  VARCHAR(300),               -- "Near Hotel XYZ, 2nd floor"
    latitude        DECIMAL(10, 8),
    longitude       DECIMAL(11, 8),
    
    -- Contact
    phone_number    VARCHAR(20),
    telegram_username VARCHAR(100),             -- @StoreName
    telegram_channel_id VARCHAR(100),           -- t.me/StoreName channel
    telegram_user_id BIGINT,                   -- Owner's Telegram User ID (after claim)
    
    -- Category
    primary_category_id INTEGER REFERENCES categories(id),
    
    -- Verification
    verification_tier SMALLINT DEFAULT 0,       -- 0=none, 1=digital, 2=physical, 3=community
    verified_at     TIMESTAMP,
    verification_notes TEXT,
    
    -- Status
    status          VARCHAR(20) DEFAULT 'pending', -- pending, active, suspended, claimed
    claimed_at      TIMESTAMP,
    claimed_by_telegram_id BIGINT,
    
    -- Analytics (denormalized for fast reads)
    view_count      INTEGER DEFAULT 0,
    contact_count   INTEGER DEFAULT 0,
    weekly_views    INTEGER DEFAULT 0,
    weekly_contacts INTEGER DEFAULT 0,
    last_active_at  TIMESTAMP,
    
    -- Source
    source          VARCHAR(50),               -- 'scraped', 'self_submitted', 'claimed'
    source_channel  VARCHAR(100),              -- which Telegram channel it was scraped from
    
    -- Timestamps
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for search
CREATE INDEX idx_shops_location ON shops(location_id);
CREATE INDEX idx_shops_category ON shops(primary_category_id);
CREATE INDEX idx_shops_status ON shops(status);
CREATE INDEX idx_shops_verification ON shops(verification_tier);
CREATE INDEX idx_shops_active ON shops(last_active_at DESC);
CREATE INDEX idx_shops_slug ON shops(slug);

-- Full-text search index
ALTER TABLE shops ADD COLUMN search_vector tsvector;
CREATE INDEX idx_shops_search ON shops USING GIN(search_vector);

-- Trigger to auto-update search_vector
CREATE OR REPLACE FUNCTION update_shop_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('simple', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.address_detail, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_shop_search_vector
    BEFORE INSERT OR UPDATE ON shops
    FOR EACH ROW EXECUTE FUNCTION update_shop_search_vector();

-- ============================================
-- CATALOG ITEMS (Products/Services from shops)
-- ============================================
CREATE TABLE catalog_items (
    id              SERIAL PRIMARY KEY,
    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
    
    -- Content
    title           VARCHAR(300) NOT NULL,
    description     TEXT,
    price           DECIMAL(12, 2),
    price_currency  VARCHAR(3) DEFAULT 'ETB',
    image_urls      TEXT[],                     -- Array of image URLs
    
    -- Metadata
    category_id     INTEGER REFERENCES categories(id),
    is_available    BOOLEAN DEFAULT TRUE,
    
    -- Source (for channel-imported items)
    source_type     VARCHAR(20) DEFAULT 'manual', -- 'manual', 'channel_import'
    source_message_id BIGINT,                   -- Original Telegram message ID
    
    -- Search
    search_vector   tsvector,
    
    -- Timestamps
    posted_at       TIMESTAMP DEFAULT NOW(),    -- When the merchant posted it
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_catalog_shop ON catalog_items(shop_id);
CREATE INDEX idx_catalog_category ON catalog_items(category_id);
CREATE INDEX idx_catalog_available ON catalog_items(is_available);
CREATE INDEX idx_catalog_posted ON catalog_items(posted_at DESC);
CREATE INDEX idx_catalog_search ON catalog_items USING GIN(search_vector);

-- Full-text trigger for catalog items
CREATE OR REPLACE FUNCTION update_catalog_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_catalog_search_vector
    BEFORE INSERT OR UPDATE ON catalog_items
    FOR EACH ROW EXECUTE FUNCTION update_catalog_search_vector();

-- ============================================
-- SHOP UPDATES (Feed posts)
-- ============================================
CREATE TABLE shop_updates (
    id              SERIAL PRIMARY KEY,
    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
    content         TEXT,
    image_urls      TEXT[],
    source_type     VARCHAR(20) DEFAULT 'manual', -- 'manual', 'channel_import'
    source_message_id BIGINT,
    posted_at       TIMESTAMP DEFAULT NOW(),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_updates_shop ON shop_updates(shop_id);
CREATE INDEX idx_updates_posted ON shop_updates(posted_at DESC);

-- ============================================
-- USER FAVORITES
-- ============================================
CREATE TABLE user_favorites (
    id              SERIAL PRIMARY KEY,
    telegram_user_id BIGINT NOT NULL,
    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(telegram_user_id, shop_id)
);

CREATE INDEX idx_favorites_user ON user_favorites(telegram_user_id);

-- ============================================
-- SHOP ANALYTICS (Daily snapshots)
-- ============================================
CREATE TABLE shop_analytics (
    id              SERIAL PRIMARY KEY,
    shop_id         INTEGER REFERENCES shops(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    views           INTEGER DEFAULT 0,
    contacts        INTEGER DEFAULT 0,
    favorites_added INTEGER DEFAULT 0,
    UNIQUE(shop_id, date)
);

CREATE INDEX idx_analytics_shop_date ON shop_analytics(shop_id, date DESC);

-- ============================================
-- VERIFICATION REQUESTS
-- ============================================
CREATE TABLE verification_requests (
    id              SERIAL PRIMARY KEY,
    shop_id         INTEGER REFERENCES shops(id),
    requested_by_telegram_id BIGINT NOT NULL,
    tier            SMALLINT NOT NULL,           -- 1, 2, or 3
    status          VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    evidence_urls   TEXT[],                      -- Photos, documents
    notes           TEXT,
    reviewed_by     VARCHAR(100),
    reviewed_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TELEGRAM CHANNEL LINKS (For "Claim This Shop")
-- ============================================
CREATE TABLE channel_links (
    id              SERIAL PRIMARY KEY,
    shop_id         INTEGER REFERENCES shops(id),
    channel_username VARCHAR(100) NOT NULL,      -- @ChannelName
    channel_id      BIGINT,                     -- Telegram channel ID
    owner_telegram_id BIGINT,                   -- Who claimed it
    claim_status    VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected
    claimed_at      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_channel_links_channel ON channel_links(channel_username);
```

### 2.2 Entity Relationship Summary

```
locations (1) ──────── (N) shops
categories (1) ──────── (N) shops
categories (1) ──────── (N) catalog_items
shops (1) ───────────── (N) catalog_items
shops (1) ───────────── (N) shop_updates
shops (1) ───────────── (N) user_favorites
shops (1) ───────────── (N) shop_analytics
shops (1) ───────────── (N) verification_requests
shops (1) ───────────── (1) channel_links
```

---

## 3. Redis Caching Architecture

### 3.1 Key Strategy

```
# ============================================
# SEARCH RESULTS CACHE
# ============================================

# Cache key pattern: search:{location_slug}:{category_slug}:{query_hash}
# TTL: 5 minutes (frequent updates expected)

search:bole:electronics:abc123     → JSON array of shop IDs
search:piazza::def456              → JSON array (no category filter)
search:::ghi789                    → JSON array (no filters, keyword only)

# ============================================
# SHOP PROFILE CACHE
# ============================================

# Cache key: shop:{shop_id}
# TTL: 15 minutes

shop:42                            → Full shop JSON (name, location, category, 
                                      verification, contact, latest updates)

# ============================================
# SHOP CATALOG CACHE
# ============================================

# Cache key: catalog:{shop_id}:{page}
# TTL: 10 minutes

catalog:42:1                       → Paginated catalog items JSON

# ============================================
# LOCATION + CATEGORY METADATA
# ============================================

# Cache key: meta:locations, meta:categories
# TTL: 1 hour (rarely changes)

meta:locations                     → Array of {id, name, slug}
meta:categories                    → Array of {id, name, slug, icon}

# ============================================
# ANALYTICS COUNTERS (Real-time)
# ============================================

# Cache key: stats:{shop_id}:views, stats:{shop_id}:contacts
# TTL: None (persisted to PostgreSQL periodically)

stats:42:views                     → Integer (incremented on each view)
stats:42:contacts                  → Integer (incremented on each contact tap)

# ============================================
# LEADERBOARD (For competitive intelligence)
# ============================================

# Cache key: leaderboard:{location}:{category}
# TTL: 1 hour

leaderbole:electronics             → Sorted set of (shop_id, view_count)
```

### 3.2 Cache Invalidation Rules

| Event | Keys Invalidated |
|-------|-----------------|
| Shop profile updated | `shop:{id}`, all `search:*` containing this shop |
| New catalog item posted | `catalog:{id}:*`, `search:*` |
| Shop verified | `shop:{id}`, `search:*`, `leaderboard:*` |
| Location/category changed | `meta:locations` or `meta:categories` |

### 3.3 Search Query Flow

```
User searches "iPhone 15 Bole"
    │
    ▼
┌─────────────────────────────┐
│ 1. Check Redis cache        │
│    key: search:bole::{hash} │
└──────────┬──────────────────┘
           │ Cache HIT → Return cached shop IDs → fetch details
           │ Cache MISS ↓
┌──────────▼──────────────────┐
│ 2. PostgreSQL Full-Text     │
│    SELECT * FROM shops      │
│    WHERE search_vector @@   │
│    plainto_tsquery('iPhone  │
│    15')                     │
│    AND location_id = 2      │
│    AND status = 'active'    │
│    ORDER BY                 │
│      verification_tier DESC,│
│      last_active_at DESC    │
│    LIMIT 20                 │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 3. Cache results in Redis   │
│    TTL: 300s                │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ 4. Also search catalog_items│
│    for item-level matches   │
│    Merge & deduplicate      │
└──────────┬──────────────────┘
           │
           ▼
      Return ranked results
```

---

## 4. API Endpoints

### 4.1 Authentication

```
POST /api/auth/telegram-login
├── Payload: Telegram WebApp initData (signed by Telegram)
├── Server validates hash using BOT_TOKEN
├── Extracts: telegram_user_id, first_name, last_name, username
├── Returns: JWT token + user profile
└── Response: { token, user: { id, telegram_id, name, username } }
```

### 4.2 Search & Discovery

```
GET /api/search
├── Query params:
│   ├── q=string          (keyword search)
│   ├── location=slug     (filter by location)
│   ├── category=slug     (filter by category)
│   ├── page=1            (pagination)
│   └── limit=20          (results per page)
├── Returns: { shops: [...], total, page, has_more }
└── Each shop: { id, name, slug, logo_url, location, category,
                 verification_tier, last_active_at, snippet }

GET /api/discover
├── Returns: { featured_shops, recent_updates, popular_categories }
└── For home screen / default view
```

### 4.3 Shop Profile

```
GET /api/shops/:slug
├── Returns: Full shop profile + latest updates + catalog preview
├── Increments view counter (async, via Redis)
└── Response: { shop: { ...all fields }, updates: [...], catalog_preview: [...] }

GET /api/shops/:slug/catalog
├── Query params: page, limit
├── Returns: Paginated catalog items
└── Response: { items: [...], total, page, has_more }

GET /api/shops/:slug/analytics
├── Auth required (must be shop owner)
├── Returns: { weekly_views, weekly_contacts, daily_breakdown: [...] }
└── For merchant dashboard
```

### 4.4 Contact & Attribution

```
POST /api/shops/:id/contact
├── Auth required
├── Records contact event for analytics
├── Returns: { message_text }
└── message_text = "Hi, I found your shop {name} on TeleDirectory regarding your post about {item}!"

# Frontend then opens: tg://resolve?domain={username}&text={encoded_message_text}
```

### 4.5 User Favorites

```
POST /api/favorites/:shop_id
├── Auth required
├── Adds shop to user's favorites
└── Response: { success: true }

DELETE /api/favorites/:shop_id
├── Auth required
└── Response: { success: true }

GET /api/favorites
├── Auth required
├── Returns: User's saved shops
└── Response: { shops: [...] }
```

### 4.6 Merchant — Claim This Shop

```
POST /api/merchant/claim
├── Auth required
├── Payload: { shop_id, channel_username }
├── Flow:
│   1. Create verification bot link
│   2. User messages bot from channel owner account
│   3. Bot verifies channel ownership via Telegram API
│   4. If verified: shop.claimed_by_telegram_id = user.id, status = 'claimed'
├── Returns: { claim_id, bot_link, status: 'pending' }
└── Webhook/callback when verification completes

GET /api/merchant/claim/status/:claim_id
├── Auth required
└── Returns: { status: 'pending' | 'verified' | 'rejected' }
```

### 4.7 Merchant — Profile Management

```
PUT /api/merchant/shop
├── Auth required (must be claimed shop owner)
├── Payload: { name, description, logo_url, cover_image_url, phone, address_detail }
├── Returns: Updated shop profile
└── Invalidates: shop cache, search cache

POST /api/merchant/shop/update
├── Auth required
├── Payload: { content, image_urls }
├── Creates new shop_update entry
├── Invalidates: shop cache
└── Returns: { update: { id, content, image_urls, posted_at } }
```

### 4.8 Merchant — Add Your Shop

```
POST /api/merchant/register
├── Auth required
├── Payload: { name, description, phone, location_id, category_id,
│              address_detail, logo_url, telegram_username }
├── Creates shop with status='pending', source='self_submitted'
├── Triggers Tier 1 verification (phone + username check)
└── Returns: { shop: { id, slug, status } }
```

### 4.9 Admin / Internal

```
POST /api/admin/shops/:id/verify
├── Admin auth required
├── Payload: { tier, notes }
├── Updates verification_tier, verified_at
└── Invalidates all related caches

GET /api/admin/shops/pending
├── Admin auth required
├── Returns: Shops awaiting verification
└── For review queue
```

---

## 5. Telegram WebApp SDK Integration

### 5.1 Initialization

```javascript
// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;

// Expand to full height
tg.expand();

// Set theme parameters
tg.setHeaderColor('#ffffff');
tg.setBackgroundColor('#f5f5f5');

// Enable closing confirmation for unsaved changes
tg.enableClosingConfirmation();

// Get user data (for auth)
const user = tg.initDataUnsafe?.user;
// { id: 123456, first_name: "Abebe", last_name: "Kebede", username: "abebe_k" }

// Validate initData on backend
// POST /api/auth/telegram-login with { initData: tg.initData }
// Backend validates hash using HMAC-SHA256 with BOT_TOKEN
```

### 5.2 MainButton Usage

```javascript
// Search results → View shop profile
const mainButton = tg.MainButton;
mainButton.text = "View Shop Profile";
mainButton.show();
mainButton.onClick(() => {
    navigateToShop(shopId);
});

// Shop profile → Contact merchant
mainButton.text = "💬 Message on Telegram";
mainButton.show();
mainButton.onClick(() => {
    // Record contact event
    fetch(`/api/shops/${shopId}/contact`, { method: 'POST' });
    
    // Open Telegram chat with pre-filled message
    const message = encodeURIComponent(
        `Hi, I found your shop ${shopName} on TeleDirectory regarding your post about ${itemName}!`
    );
    window.open(`tg://resolve?domain=${username}&text=${message}`);
});
```

### 5.3 Viewport Handling

```javascript
// Handle viewport changes (keyboard open/close)
tg.onEvent('viewportChanged', (event) => {
    if (event.isStateStable) {
        // Adjust layout for new viewport height
        adjustLayout(tg.viewportHeight);
    }
});

// Safe area insets for notched devices
const safeTop = tg.contentSafeAreaInset?.top || 0;
const safeBottom = tg.contentSafeAreaInset?.bottom || 0;
```

### 5.4 Haptic Feedback

```javascript
// On successful search
tg.HapticFeedback.notificationOccurred('success');

// On tap (filter chips, buttons)
tg.HapticFeedback.impactOccurred('light');

// On error
tg.HapticFeedback.notificationOccurred('error');
```

---

## 6. Data Ingestion Pipeline (Scraper Specifications)

### 6.1 Telethon Scraper Script

```python
"""
TeleDirectory — Public Channel Scraper
Parses public Telegram commerce channels to extract shop/product data.

Dependencies: telethon, psycopg2, python-dotenv
Usage: python scraper.py --channels channels.txt --output db
"""

# Target data extraction per message:
# - channel_username (source)
# - message_id (deduplication)
# - message_text (product description)
# - image_urls[] (product photos)
# - price (regex extraction from text)
# - phone_number (regex extraction from text)
# - telegram_handle (regex extraction from text)
# - posted_at (message date)

# Regex patterns for Ethiopian commerce posts:
PRICE_PATTERNS = [
    r'(?:price|ዋጋ|ብር)[:\s]*([\d,]+)\s*(?:etb|birr|ብር)?',
    r'([\d,]+)\s*(?:etb|birr|ብር)',
    r'(?:ETB|Birr)\s*([\d,]+)',
]

PHONE_PATTERNS = [
    r'(?:\+251|0)[97]\d{8}',           # Ethiopian mobile numbers
    r'@\w+',                            # Telegram handles
]

# Extraction pipeline:
# 1. Connect to Telegram via Telethon (user account or bot)
# 2. Iterate target channels
# 3. For each message:
#    a. Extract text, images, date
#    b. Regex-extract price, phone, handle
#    c. Deduplicate by (channel, message_id)
#    d. Insert into staging table
# 4. ETL: staging → shops + catalog_items tables
```

### 6.2 Scraper Output Schema (Staging)

```sql
CREATE TABLE scraped_messages (
    id              SERIAL PRIMARY KEY,
    channel_username VARCHAR(100) NOT NULL,
    message_id      BIGINT NOT NULL,
    message_text    TEXT,
    image_urls      TEXT[],
    extracted_price DECIMAL(12, 2),
    extracted_phone VARCHAR(20),
    extracted_handle VARCHAR(100),
    posted_at       TIMESTAMP,
    processed       BOOLEAN DEFAULT FALSE,
    shop_id         INTEGER,                  -- Linked after ETL
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(channel_username, message_id)
);
```

### 6.3 ETL Rules

```
Scraped Messages → Shop Creation:
├── Group by channel_username
├── Each unique channel = 1 potential shop
├── Shop name = channel title
├── Shop phone = most frequent extracted_phone
├── Shop telegram_username = channel username
├── Location = manually tagged per channel (or regex from text)
└── Category = manually tagged per channel (or keyword matching)

Scraped Messages → Catalog Items:
├── Each message with a product = 1 catalog item
├── title = first line of message (or extracted product name)
├── description = full message text
├── price = extracted_price
├── image_urls = message images
└── posted_at = message date
```

---

## 7. Frontend Page Structure

### 7.1 Pages

| Page | Route | Description |
|------|-------|-------------|
| **Home/Discover** | `/` | Default view: location chips + category chips + featured shops + recent updates |
| **Search Results** | `/search?q=&location=&category=` | Filtered shop list with result cards |
| **Shop Profile** | `/shop/:slug` | Full shop profile, updates feed, catalog grid |
| **Favorites** | `/favorites` | User's saved shops |
| **Add Your Shop** | `/merchant/register` | Self-submission form |
| **Merchant Dashboard** | `/merchant/dashboard` | Analytics, profile edit, post updates |
| **Claim This Shop** | `/merchant/claim` | Channel verification flow |

### 7.2 Component Architecture

```
App
├── Layout
│   ├── Header (logo, search bar, user avatar)
│   ├── Navigation (bottom tab bar)
│   └── MainButton (context-dependent)
│
├── Pages
│   ├── HomePage
│   │   ├── LocationChips (horizontal scroll)
│   │   ├── CategoryChips (horizontal scroll)
│   │   ├── FeaturedShopsCarousel
│   │   └── RecentUpdatesFeed
│   │
│   ├── SearchPage
│   │   ├── SearchBar (auto-focus, instant results)
│   │   ├── FilterChips (location + category)
│   │   └── ShopResultList
│   │       └── ShopResultCard (name, logo, area, badge, last active)
│   │
│   ├── ShopProfilePage
│   │   ├── ShopHeader (cover, logo, name, badge, location)
│   │   ├── ContactButtons (call, message, directions)
│   │   ├── UpdatesFeed (latest posts with images)
│   │   └── CatalogGrid (product cards with prices)
│   │
│   ├── FavoritesPage
│   │   └── SavedShopList
│   │
│   ├── MerchantRegisterPage
│   │   └── RegistrationForm (name, category, location, phone, photo)
│   │
│   ├── MerchantDashboardPage
│   │   ├── StatsCard (views, contacts, weekly trend)
│   │   ├── QuickPost (text + image → update)
│   │   └── ProfileEditor
│   │
│   └── ClaimShopPage
│       ├── ShopSearch (find pre-indexed shop)
│       └── VerificationFlow (bot message → confirm)
│
└── Shared Components
    ├── ShopCard
    ├── VerificationBadge (✓, ✓✓, ✓✓✓ by tier)
    ├── PriceTag
    ├── LocationTag
    ├── CategoryTag
    ├── ImageCarousel
    └── LoadingSkeleton
```

---

## 8. Security Considerations

### 8.1 Authentication
- All Telegram WebApp `initData` validated server-side using HMAC-SHA256 with `BOT_TOKEN`.
- JWT tokens issued after validation. Short-lived (24h) with refresh capability.
- No passwords stored. Telegram User ID is the identity anchor.

### 8.2 Authorization
- Shop profile editing restricted to `claimed_by_telegram_id` owner.
- Admin endpoints protected by separate admin auth layer.
- Analytics endpoints require shop ownership.

### 8.3 Rate Limiting
- Search API: 60 requests/minute per user.
- Contact endpoint: 10 requests/hour per user per shop (prevent spam).
- Registration: 3 shops per Telegram account.

### 8.4 Data Protection
- Phone numbers displayed via tap-to-call only (not exposed in API responses as plain text).
- No private message scraping. Public channels only.
- Immediate data deletion on merchant request.

---

## 9. Performance Targets

| Metric | Target | How |
|--------|--------|-----|
| Search response time | < 500ms (p95) | Redis cache + PostgreSQL full-text index |
| Shop profile load | < 300ms (p95) | Redis-cached shop data |
| Initial app load | < 2s | Lazy loading, code splitting, CDN images |
| Concurrent users | 1000+ | Redis caching reduces DB load by 80%+ |
| Data freshness | < 15 min | Cache TTLs aligned with update frequency |

---

*This SRS is the developer-ready blueprint. Pair with `teleDirectory-ground-operations.md` for the operational playbook.*
