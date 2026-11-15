---
name: lessons-learned
description: Mandatory pre-flight-search reference. Contains the Seats.aero workflow (pull ALL programs first), source accuracy hierarchy, small-market caveats, and Bilt portal limitations.
category: reference
summary: Hard-won knowledge from real searches. The mandatory Seats.aero workflow, source accuracy, small-market caveats, Bilt portal limitations. Load before any award flight search.
---

# Lessons Learned

Hard-won knowledge from actual searches. Reference these before making the same mistakes.

## Seats.aero: Search ALL Sources, Show ALL Results

When searching Seats.aero, **NEVER filter by source on the initial search.** Always pull ALL programs first.

### The Mandatory Workflow

For any route:

1. **Search Seats.aero with NO source filter.** Pull ALL programs. Show full results sorted by cheapest.
2. **For EVERY program in results, trace the full reachability chain:**
   a. Direct balance? (Check AwardWallet if connected)
   b. Transfer path? (Check `data/transfer-partners.json` for EVERY currency: Amex MR, Chase UR, Bilt, Capital One)
   c. Alliance chain? Identify the operating airline's alliance (`data/alliances.json`), then find ALL programs in that alliance or with bilateral partnerships (`data/partner-awards.json`), then check which of THOSE programs are reachable via transfer.
   d. Cross-alliance? Check `data/partner-awards.json` `cross_alliance_highlights` and bilateral partners.
3. **For reachable programs with NO cached Seats.aero data,** check the program's website directly (airfrance.com, united.com, etc.)
4. **Present the COMPLETE picture:** every option, reachable or not, with the transfer chain spelled out.
5. **Only THEN compare award vs cash.**

### Common Failure Mode

Seeing an airline in results, checking one or two obvious programs, declaring awards "unreachable" or "bad value," and recommending cash. You MUST trace every possible chain through alliances and bilateral partnerships. If the operating airline is in an alliance, EVERY program that books that alliance is a potential path.

### "No Cached Availability" Is Not the Final Word

It means Seats.aero hasn't scraped it recently. When a reachable program shows no cached results, search the airline's website directly before declaring awards dead.

## Never Trust Data Files Over Reality

Data files are reference material, not gospel. Airline partnerships change constantly. When a user says a booking path works that your data doesn't show, verify on the actual booking website FIRST before pushing back. The website is the source of truth. Your files are a cache. If the data file disagrees with reality, update the data file.

## Source Accuracy Hierarchy

**Bilt portal / Ignav > Airline website > SerpAPI > Skiplagged/Kiwi**

1. **The Bilt portal (Duffel-backed) returns real GDS prices per fare class.** These are bookable. Tested with Duffel directly: it showed $271 basic / $325 main. SerpAPI showed $541 for the same flight. The gap was consistent across multiple itineraries.
2. **SerpAPI (Google Flights) inflates prices.** Google Flights often shows "main cabin" or bundled fares, not the cheapest bookable fare class. Useful for Google Hotels and destination discovery, but do not trust it as the sole source for flight cash prices.
3. **Kiwi returns garbage on small markets.** Filter hard or skip Kiwi for domestic routes to small airports.

## Small Market Airports

Small airports have limited award availability. Seats.aero cached data will be sparse. When searching small markets:

1. **Ignav and the Bilt portal for cash prices** (work fine, GDS has the inventory)
2. **Don't bother with Seats.aero cached search** (data too sparse)
3. **Check airline-specific award pricing** via the program's website if needed

## Layover and Time Preferences

Ask the user for their preferences on the first search. Key questions:

- Minimum and maximum layover time
- Earliest acceptable departure time
- Red-eye tolerance
- Lounge access (changes how long layovers feel)

Store their answers and apply to all subsequent searches in the session.

## Bilt Portal Limitations

- **No award pricing.** The Bilt flights endpoint shows cash fares only. Use Seats.aero for award availability.
- **Offers expire in 15-30 minutes.** Don't cache Bilt results across sessions.
- **Unofficial public endpoint.** No documented rate limit, so keep request volume polite and fall back to Ignav if it errors.
- **Returns multiple fare classes for the same flight.** This is a feature. You'll see basic economy at one price and main cabin at another for the same routing. Use the cheapest bookable class for cpp comparison unless the user specifies a fare preference.

## Related Reference Skills (Load When Relevant)

These are not required for every search but should be loaded when the conversation context suggests them:

- **`transfer-bonuses`** — Load before recommending any credit card → loyalty program transfer. Live weekly data on currently active bonuses (e.g., Amex MR → Hilton 20%, Chase UR → Aeroplan 20% with stackable cardholder bonus). A 30% bonus changes which currency is cheapest in the transfer-partners optimization.
- **`stopovers`** — Load when the trip has a layover near 24h, or when the user wants to "stop in X on the way." 17 programs documented with primary citations: Aeroplan (1 stopover, 5K surcharge), TAP (1 on partner awards), Turkish (free Istanbul stopover), Etihad (Abu Dhabi), Icelandair (Reykjavík free up to 7 days, the legendary one), Alaska (free, phone only), Flying Blue (free, possibly unlimited), JAL multi-carrier (up to 3), Singapore Saver/Advantage tiers, AF/KLM, Cathay (2+2). Also documents which programs DO NOT allow stopovers (BA Avios, AA AAdvantage, Delta SkyMiles, JetBlue, Virgin Atlantic, Iberia Avios) — that's a critical negative finding.
- **`award-holds`** — Load before any "transfer points first" recommendation. Hold landscape per current data: AA allows 24h self-service hold online (the only program with online holds; the previous 5-day version was discontinued in late 2024). Virgin Atlantic Flying Club holds 1-2 days by phone, free. Flying Blue holds up to 3 days by phone with a $25 phone-booking fee at ticketing. Lufthansa M&M up to 5 days. Cathay ~2 days. Singapore agent-discretionary. The major Western programs that DO NOT allow holds: United, Alaska, Delta, BA, Aeroplan. Always check the data file rather than relying on this one-line summary.
- **`round-the-world`** — Load when the trip implies 3+ stops or multiple regions. 13 active + 4 discontinued products documented. The RTW universe is collapsing (4 killed in last 18 months), but Star Alliance + oneworld + Lufthansa M&M + Qantas remain solid. Special Business RTW at 26,000 miles is the steal. Includes Iberia Plus intra-Europe sweet spots and Aeroplan distance-based regional awards.
- **`status-match`** — Load when the user asks about elite status shortcuts, status match, status challenge, "switching loyalty programs," or mentions a once-in-a-while opportunity (Hyatt Globalist Challenge, Marriott Platinum Challenge). Critical lifetime/once-per-N-years warnings: Alaska Atmos = once per lifetime, AA = once every 2 years, Delta/United = once every 3 years, Hyatt Globalist Challenge = once per lifetime. The skill distinguishes free direct matches from paid concierge (statusmatch.com is real but charges fees) from card-granted renewable status (Amex Platinum = Hilton Gold + Marriott Gold automatic).
