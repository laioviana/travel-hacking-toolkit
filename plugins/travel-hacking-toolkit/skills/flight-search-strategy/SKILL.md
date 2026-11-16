---
name: flight-search-strategy
description: Canonical multi-source flight search strategy. Source priority (Ignav, Bilt portal, Google Flights, Skiplagged, Kiwi, Seats.aero), parallel workflow, market selection for international price arbitrage.
category: reference
summary: The canonical multi-source search workflow. Source priority (Ignav > Bilt portal > Google Flights > others), market selection for international routes, source accuracy hierarchy, common failure modes.
---

# Flight Search Strategy

## Search ALL Sources for EVERY Flight Search

This is not a pick-one list. Each source returns different results, different prices, and different airlines. Missing a source means missing options. The priority order determines which price to trust when sources disagree, not which sources to skip.

| Priority | Source | Strengths | Blind Spots |
|----------|--------|-----------|-------------|
| 1 | **Ignav** (skill) | Fast REST API. Verified bookable fares with booking links. Market selection for price arbitrage. Free, no credit card. | No award pricing. |
| 2 | **Bilt portal** (`bilt` skill, flights endpoint) | Real GDS per-fare-class data (Duffel-backed). Public API, no key, no credit card. | No award pricing. No market selection or multi-city. Offers expire in 15-30 min. |
| 3 | **Google Flights** (skill, agent-browser) | Covers ALL airlines cash prices. Free. Economy/business comparison. | Prices can be inflated vs GDS. No points pricing. |
| 4 | **Skiplagged** (MCP) | Hidden city fares. Zero config. | Can be noisy on small markets. |
| 5 | **Kiwi.com** (MCP) | Virtual interlining (creative cross-airline routings). Zero config. | Returns garbage on small markets. |
| 6 | **Seats.aero** (skill + MCP) | Award flight availability across 25+ programs. The crown jewel for points. Partner API with a key, official MCP without one. | Cached data, not live. No cash prices. Keyless MCP only covers the next 60 days. |
| 7 | **SerpAPI** (skill, optional) | Google Hotels search. Destination discovery (Google Travel Explore). | NOT for flights (inflated prices). Hotels and "where should I go?" only. |

## The Standard Flight Search Workflow

**Run ALL of these in parallel:** Ignav + Bilt portal + Google Flights + Skiplagged + Kiwi.

Skiplagged and Kiwi are keyless MCP servers — they are available in every properly launched session. Attempt the tool call before ever claiming MCP is unavailable, and never substitute improvised browser scraping for these sources (see `fallback-and-resilience`).

Always add Seats.aero for award comparison. Use the Partner API skill when `SEATS_AERO_API_KEY` is set. Without a key, use the `seats-aero` MCP (`get_flights`), which covers flights departing in the next 60 days. See the `seats-aero` skill for the routing table. Always run the Southwest skill if SW flies the route.

Don't skip sources. Don't assume one source has everything. Present the combined results with the best options highlighted regardless of which source found them.

**For a single unified comparison, use the `compare-flights` skill** which orchestrates all of the above in parallel and applies transfer partner optimization.

## Round Trip vs One-Way Construction

When the trip has a return date, price BOTH constructions — proactively, without being asked:

1. **The round-trip fare** on every source (Ignav, Bilt portal, Kiwi, Skiplagged, and Google Flights all quote returns).
2. **Two one-ways**, searched independently — which also surfaces the mixed construction (outbound on carrier A, return on carrier B) that round-trip searches can't see.

Run all of it in the same parallel batch; it's two extra searches, not a second pass.

Which wins is route-dependent, so never assume:

- **Round trips often win internationally** on legacy carriers, where return fares are discounted relative to two one-ways.
- **One-way pairs often win domestically**, on ULCCs. They also buy flexibility: each leg can be changed or canceled independently.
- **Mixed-carrier pairs** frequently beat both when outbound and return are priced by different airlines' sale calendars.

Present the verdict explicitly with the delta: "Round trip $842 vs best one-way pair $918 — book the round trip, saves $76" (or the reverse). If the gap is under ~$50, mention the flexibility advantage of separate tickets before recommending the round trip.

## Market Selection Strategy

Different country markets return different prices for the same route. Searching from Thailand (`&gl=TH`) vs the US (`&gl=US`) can save hundreds of dollars.

**Always try multiple markets for international flights:**

1. **Departure country market first** (e.g., `&gl=US` for flights from the US)
2. **Destination country market** (e.g., `&gl=JP` for flights to Japan)
3. **Ask the user before trying more** (e.g., third countries, VPN markets)

This applies to:
- **google-flights** via the `&gl=XX` URL parameter
- **ignav** via the `market` field in the search payload

**The Bilt portal and SerpAPI don't support market selection.**

## Source Accuracy Hierarchy

When sources disagree on cash prices:

**Bilt portal / Ignav > Airline website > SerpAPI > Skiplagged/Kiwi**

1. **The Bilt portal (Duffel-backed) returns real GDS prices per fare class.** These are bookable. Tested with Duffel directly: it showed $271 basic / $325 main. SerpAPI showed $541 for the same flight. The gap was consistent across multiple itineraries.
2. **SerpAPI (Google Flights) inflates prices.** Often shows "main cabin" or bundled fares, not the cheapest bookable fare class. Useful for Google Hotels and destination discovery, but do not trust it as the sole source for flight cash prices.
3. **Kiwi returns garbage on small markets.** Filter hard or skip Kiwi for domestic routes to small airports.

## Common Failure Modes

- Running only one source and missing better options on others.
- Trusting SerpAPI prices as bookable (they're often inflated).
- Skipping Seats.aero because the user "doesn't have those points" — they may have them via transfer, see the `partner-awards` skill.
- Single-market search on international routes (always try at least 2 markets).

## This User: Markets, Currency, Positioning

Defaults come from `data/my-profile.json` (read via `my-points`), not from the examples above.

- **Markets:** use the profile's `search_markets`, in order. For this user that is **NL first, then BR**. The BR market sometimes returns lower fares for Brazil-bound trips, and the fare is then payable in BRL with a Brazilian card. Ask before trying a third market.
- **Currency:** show every price in R$. Convert EUR and USD with `python3 scripts/fx.py <amount> EUR`. State the rate date. Card FX adds roughly 1 to 3%.
- **Positioning:** also search the profile's `positioning_airports` (EIN, RTM, BRU, DUS, CGN). Add the cost and time of getting there (rail via `deutsche-bahn` for DUS and CGN) before calling a positioning fare cheaper. Taxes on awards by departure airport are UNVERIFIED, so test each airport on the booking engine rather than assuming (see `flying-blue`).
- **Party:** search `party.default_seats` seats, with the child counted at the age on the travel date.
- **Brazil-bound trips:** run `ams-for` for Fortaleza. Load `flying-blue` and `avios` for Air France and Iberia awards.
