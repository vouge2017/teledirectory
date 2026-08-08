# TeleDirectory Phase 0 — Operator Run-Book

You are the operator. Your job is to keep the bot fed with fresh listings
from the cooperating electronics channels. This takes ~15–30 min/day.

---

## Daily Routine

### 1. Check cooperating channels (5 min)
Open each cooperating channel in Telegram. Scroll through the last 24h of posts.
Look for:
- New product listings (phones, laptops, accessories)
- Price drops or promotions
- Items that haven't been added yet

### 2. Add new listings (10 min)

**Method A — Forward (fastest)**
1. Tap & hold the channel post → Forward
2. Send it to the TeleDirectory bot
3. Reply to your forwarded message with: `/forward_add`
4. Bot extracts channel, message ID, title, and price automatically
5. Done. Bot notifies any matching watchers.

**Method B — Manual /add**
If the forward doesn't parse cleanly:
```
/add @ChannelUsername 12345 iPhone 15 Pro Max 256GB 85000 Birr
```
- `@ChannelUsername` — channel handle (without @ also works)
- `12345` — the message ID (visible in the post URL: t.me/ChannelUsername/12345)
- Everything after = title + optional price at the end

### 3. Clean up stale listings (5 min)
```
/list
```
Check the list. If something is sold or no longer available:
```
/sold 42
```
If something is spam or wrong:
```
/remove 42
```

### 4. Check stats (1 min)
```
/stats
```
Look at:
- **Active listings** — should grow week over week
- **Searches** — are buyers using the bot?
- **Clicks** — are they clicking through to original posts?
- **Watches** — are buyers setting alerts?

---

## What makes a good listing

✅ **Add these:**
- Fresh posts (< 48h old) with clear product + price
- Posts from cooperating channels you've agreed to index
- Items with photos (buyers want to see what they're getting)

❌ **Skip these:**
- Posts older than a week (likely sold)
- Vague "DM for price" posts (no value without a price)
- Non-electronics (unless that's your category)
- Posts from channels you haven't gotten permission to index

---

## Deep link is the core value

Every listing must have a working deep link back to the original post.
When you `/add`, make sure the channel username and message ID are correct.

Test: after adding, tap the "View Original Post" button. Does it open the right post?
If not, `/remove` and re-add with the correct info.

---

## Troubleshooting

**"Already added" error:**
That channel + message_id combo is already in the database. Use `/list` to find it.

**Bot didn't notify watchers:**
Check `/stats` — are there active watches? The bot only notifies if the listing
title/price/category contains the watch keyword.

**Forward doesn't parse:**
Some forwards lose channel metadata. Fall back to manual `/add`.

**Buyer says link is broken:**
Double-check the channel username and message ID. The format must be exact:
`t.me/ChannelUsername/MessageID`
