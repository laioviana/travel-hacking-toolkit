---
name: compare-hotels
description: Unified hotel comparison across metasearch (Trivago, Google Hotels), Airbnb and chain award rates. Accor first, prices in BRL, family occupancy from the profile.
category: orchestration
summary: Unified hotel comparison across portals, metasearch, and Airbnb. FHR/Edit stacking detection.
api_key: Uses individual skill keys
---

**Companion reference skills.** Load these for deeper context:
- `hotel-chains` for the brand to loyalty program mapping
- `points-valuations` for hotel point values (Accor ALL is fixed at 2,000 points = EUR 40)
- `my-points` for balances, status and the party (occupancy)
- `fallback-and-resilience` for recovery when a hotel source fails

# Compare Hotels

Search every available source for accommodation and present one unified comparison in R$ (convert EUR or USD with `python3 scripts/fx.py`). This is an orchestration skill: it tells the agent which tools to run and how to combine results. No standalone script.

The US portal programs (Amex FHR/THC, Chase Edit) do not apply to this user and are archived in `skills/_archive/premium-hotels`. Do not suggest them.

## When to Use

- "Find me a hotel in Lisbon for a weekend"
- "Is it worth paying with Accor points for this hotel?"
- "Compare hotels vs Airbnb in Fortaleza"
- Any accommodation search where the user wants the full picture

## Sources

Run these in parallel where possible. **Never fail silently.**

| Source | Skill/Tool | What It Finds |
|--------|------------|---------------|
| Trivago | `trivago-accommodation-radius-search` MCP | Metasearch across OTAs. Set country NL and currency BRL or EUR if listed. Cheapest OTA rate per hotel. |
| Skiplagged hotels | `sk_hotels_search` MCP | Second cash opinion. |
| SerpAPI | `serpapi` | Google Hotels cash prices, ratings and review counts. |
| Airbnb | `airbnb_search` MCP | Entire homes and apartments with total pricing. Best for families and 5+ nights. |
| RapidAPI | `rapidapi` | Booking.com inventory. Only when the user asks for Booking.com. |
| Accor award rate | `hotel-chains` plus the Accor site | ALL points price. Fixed 2,000 points = EUR 40, so compare cash price with points needed. |

Occupancy comes from the profile party (adults plus the child). Prefer family rooms, apartments and kids-stay-free policies, and say when a rate only fits two guests.

## Workflow

### Step 1: Search all sources in parallel

For each source capture the source name, status ("ok", "error: reason", "skipped: reason"), result count and data.

### Step 2: Chain trigger

If any result is a branded chain property, load `hotel-chains` and check award rates. Accor first: mention the user's ALL status benefits from the profile on Accor properties (they usually apply to the member's own room only). Hilton at a 0.4 cpp floor is almost always worse than cash. Say so.

### Step 3: Value points in R$

For award stays: R$ value of the points used (see `data/point-costs.json` and the cost basis in the balances file) against the cash rate in R$. Use R$ per milheiro, never cents per point. Accor: 2,000 points = EUR 40 means 1,000 points = EUR 20, converted to R$ with `scripts/fx.py`.

### Step 4: Present one table

Always a markdown table, sorted by total stay price in R$ for the whole party.

| # | Hotel | Source | Stars | Google | Per night (R$) | Total (R$) | Points | Notes |
|---|-------|--------|-------|--------|----------------|------------|--------|-------|

Add the Google rating and review count when SerpAPI has it. Airbnb listings show their own rating, labeled as such.

List sources checked, with status, under the table.

### Step 5: Recommendation

1. Best value overall and why.
2. Best for the family (space, kitchen, breakfast included).
3. Points vs cash, with R$ numbers.
4. Direct vs OTA price when different.
5. Rail or flight context for the trip is handled by `europe-rail` and `compare-flights`.

## Airbnb Integration

```
airbnb_search(location="Lisbon, Portugal", checkin="2026-08-11", checkout="2026-08-15", adults=2, children=1, propertyType="entire_home")
```

Extract name, total price, rating, reviews, property type, key amenities (kitchen, washer, wifi, AC) and the listing link. Airbnb wins for 5+ nights, families needing space and when a kitchen matters. Hotels win for 1 to 2 nights, when status or points give clear value, or when breakfast is included.

## Error Handling

Report every source status. Example: "Airbnb: no results for these dates", "Trivago: error, used Skiplagged hotels instead".

## Data Files Used

| File | Purpose |
|------|---------|
| `data/hotel-chains.json` | Hotel chain to loyalty program mapping |
| `data/points-valuations.json` | Point valuations, including Accor ALL |
| `data/point-costs.json` | Typical purchase cost of bought points |

## Limitations

- Airbnb MCP must be available. Skip gracefully if not.
- Hotel award prices are variable except Accor. Use the live points price shown by the program.
- Direct booking prices may differ from OTA prices for the same hotel.
