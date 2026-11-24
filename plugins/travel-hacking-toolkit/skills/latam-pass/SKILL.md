---
name: latam-pass
description: LATAM Pass award search and rules. Own-metal dynamic pricing (the fixed partner chart is in latam-tabela-fixa), phone and WhatsApp booking, infant pricing and booking for others. LATAM Pass is not on Seats.aero, so use this whenever a LATAM flight or LATAM Pass miles are part of an option, including LATAM Lisbon to Fortaleza.
category: loyalty
summary: LATAM Pass awards. Dynamic own-metal pricing, fixed partner table, booking rules. Not on Seats.aero.
api_key: None (requires browser)
---

# LATAM Pass

Check the user's LATAM Pass balance and `avg_cost_per_milheiro_brl` in `data/my-balances.json`. When it's a large, cheaply bought balance, LATAM Pass is the first program to check for any LATAM-operated flight.

**Seats.aero does not cover LATAM Pass.** Availability has to come from LATAM's own site.

## Two kinds of awards

### 1. LATAM-operated flights: dynamic pricing
- **Price varies by date, demand and fare.** Search on latampass.latam.com: choose "Usar milhas" (use miles), then the route, dates and passengers.
- **Relevant routes for this user:**
  - LIS–FOR, seasonal nonstop (see `data/home-routes.json`)
  - Europe–GRU, then GRU–FOR
- **Search with the profile's party** so the price covers everyone.

**How to search:**
- **If `agent-browser` is installed,** drive the site like the `google-flights` skill does.
- **Otherwise,** use the built-in browser pane.
- **If both fail** (bot wall, login needed), give the user the exact search to run: route, dates, passengers, "Usar milhas." Never guess a miles price.

### 2. Partner flights: fixed table (tabela fixa)
**Use the `latam-tabela-fixa` skill.** It has the full official chart for all region pairs and cabins, a calculator (`scripts/latam_tabela_fixa.py`), the region table and the booking flow.

The essentials:
- **Booking:** phone or WhatsApp only.
- **Price:** set by cabin and region pairs.
- **20% increase in force since 2026-11-23:** Brazil–Europe economy is now 96,840 and business 241,920, one way.
- **Infants under 2 can't be issued on partner awards.**
- **Partner economy to Europe is poor value for this user.** LATAM's own metal (dynamic) is usually the better use.

## Family rules

From `data/family-booking.json`:
- **Infant under 2 (all segments):** about 10% of the adult miles plus taxes, on LATAM-operated flights only. Partner awards (tabela fixa) don't allow infants under 2.
- **Child 2–11:** assume full miles.
- **Booking for others:** about 24–25 distinct people per rolling 12 months. No fee reported.

## Getting miles in

- **Livelo:** 1:1, minimum 12,000 (1,000 with Clube Livelo Especial or Premium).
- **Esfera:** 1:1.
- **Always check `bonificadas` first.** LATAM Pass also runs purchase promos ("compre milhas com até X% de desconto"). They're only worth it below the user's LATAM cost basis and with a booking in sight.

## Output

For each LATAM Pass option, give:
- **Miles per person and for the family**, then **taxes in R$**
- **R$ per milheiro achieved,** vs. the user's cost basis and the `brl_milheiro.latam_pass` floor
- **Where the price came from:** a live site search (with date and time) or the fixed table
