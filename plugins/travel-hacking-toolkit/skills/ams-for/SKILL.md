---
name: ams-for
description: One-command search for the priority route Amsterdam to Fortaleza (AMS-FOR, either direction or round trip). Searches every gateway (CDG Air France, MAD Iberia, LIS TAP and seasonal LATAM, Brazilian hubs), cash and awards in parallel, prices the whole travelling party from the profile in R$, and ranks options against the user's cost basis. Use for any trip between the Netherlands or Europe and Fortaleza or Northeast Brazil.
category: orchestration
summary: AMS to Fortaleza family search across every gateway. Cash and awards priced in BRL against cost basis.
api_key: Uses individual skill keys
---

# AMS ⇄ FOR

A priority route in `data/home-routes.json`. The usual picks are AMS–MAD–FOR on Iberia or AMS–CDG–FOR on Air France, but the goal is to find the best option across **every** gateway.

Reads:
- `data/home-routes.json` → `AMS-FOR` for gateways and programs
- `data/my-profile.json` for the party, markets and currency
- `data/my-balances.json` for balances and cost basis
- `data/family-booking.json` for child pricing and booking-for-others rules

## 0. Inputs

- **Dates.** If the user didn't give any, ask once: outbound, return, and flexibility (± days).
- **Cabin.** Default economy, plus a business check if balances allow.
- **Party.** From the profile (`party`). Work out each child's age on each travel date from their birth month:
  - under 2 = lap infant
  - 2–11 = child seat
- **Load these first:** `lessons-learned`, then `flight-search-strategy`, then `my-points`.

## 1. Search in parallel

**Cash, in R$:**
- **Kiwi MCP and Skiplagged MCP:** AMS→FOR, the return, and positioning from BRU and DUS.
- **Ignav** with `market: "NL"`, then `market: "BR"` (skip silently if there's no key).
- **Convert every price** with `python3 scripts/fx.py <amount> <CUR>`.
- **Record the full family total.** Cash child fares exist, so don't just multiply the adult fare by 3. If a tool can't price a child, say the total is approximate.

**Awards (Seats.aero MCP / API):**
- **Search all programs first.** Don't filter by program upfront.
- **Routes:** AMS–FOR, CDG–FOR, MAD–FOR and LIS–FOR, plus the short legs AMS–CDG, AMS–MAD and AMS–LIS, both directions.
- **Keep only results with ≥ `party.default_seats`** where seat counts are reported.
- **Programs that hide seat counts** (`azul`, `qatar`): keep the result, marked "the party's seat count unverified."
- **`qatar` results on Iberia flights** stand in for Iberia Avios availability. Price the real award on iberia.com, since off-peak Avios can differ.

**LATAM Pass** (not on Seats.aero): follow the `latam-pass` skill for LIS–FOR (seasonal) and Europe–GRU–FOR.

**Status match check:** run the `status-matcher` skill (`python3 scripts/statusmatcher.py --profile`) and, for the carriers in play, `--to "flying blue"`, `--to iberia`, `--to tap`, `--to latam`. Status on the carrier flown can mean free bags and seats together for the whole family.

**Bonus check:** run the `bonificadas` skill, i.e. refresh and filter. A running Livelo or Esfera bonus into Smiles, Azul or LATAM changes which program wins.

## 2. Build the options

For every combination that works:
- **Award on both legs, same program.**
- **Mixed one-ways.** For example, Flying Blue out (AMS–CDG–FOR) and Iberia Avios back (FOR–MAD–AMS).
- **Award long-haul plus a cash positioning leg.** For example, cash AMS–LIS plus LATAM Pass LIS–FOR.
- **All cash,** as the baseline.

**Price per program for the family:**
- **Adults:** award miles × 2.
- **Child, Flying Blue:** 25% off (may require a Flying Blue Family link).
- **Child, Smiles / Azul / LATAM:** full miles.
- **Child, Iberia:** check the booking engine, since the child rate is unverified.
- **Infant, if under 2 on any leg:** see `family-booking.json`.
- **Taxes and surcharges in R$,** for all 3 travellers.

**Can the user pay for it?**
- Use the effective balance: direct balance plus transfers, at the ratios in `transfer-partners.json`.
- Apply any bonificada, and route Avios via `avios-family.json` (Esfera 2:1, Livelo→Qatar 3:1, Amex NL→BA 5:4).
- If the balance is short, show the top-up cost in R$.

**Value:**

```
value per milheiro = (family cash total R$ − family award taxes R$) / total miles × 1000
```

Compare it to the cost basis of the miles used, and to the `brl_milheiro` floor.

## 3. Output

One table with these columns:
- Option
- Routing / flights
- Family cash R$
- Miles (family)
- Award taxes R$
- R$/milheiro vs. cost basis
- Seats confirmed?
- Notes

Then:
- **Recommendation.** One option, and why, in R$. For example: "Saves R$ 6,200 vs cash using 180k LATAM Pass, R$ 34/milheiro against your cost basis of R$ X."
- **Runner-up and cheapest cash,** one line each.
- **Family flags:**
  - connection times with a toddler
  - seat-selection cost to sit together
  - risk of split tickets, if the seats are on different bookings (`split_ticket_warning`)
- **Deadlines:**
  - promos ending soon
  - the LATAM partner table increase on 2026-11-23, if relevant
  - seats.aero data older than 24h
- **Status match:** one line if `status-matcher` found a match on the recommended carrier that's worth applying for before this trip (with its lifetime limit from `status-match`). Skip the line if none.
- **Next step:** what to transfer (amount, path, expected arrival time) and where to book. Load `booking-guidance` and `award-holds` before telling the user to transfer.

## Rules

- **Never show a 1-seat price as the answer** when the party is larger.
- **Every number in R$.** Show the EUR source price in brackets only when it helps.
- **Don't drop an option just because the user doesn't usually fly it.** The LIS gateways and positioning from BRU or DUS often win.
