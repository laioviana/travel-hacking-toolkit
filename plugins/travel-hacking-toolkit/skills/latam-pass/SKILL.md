---
name: latam-pass
description: LATAM Pass award search and rules. Own-metal dynamic pricing, the fixed partner award table (Brazil to Europe), the 20 percent partner table increase from 2026-11-23, phone and WhatsApp booking, infant pricing and booking for others. LATAM Pass is not on Seats.aero, so use this whenever a LATAM flight or LATAM Pass miles are part of an option, including LATAM Lisbon to Fortaleza.
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

### 2. Partner flights: fixed table
- **Booking:** phone (4002-5700) or WhatsApp only. Not bookable online.
- **Pricing:** depends on the cabin and the regions travelled, not on the number of connections. Availability is not guaranteed.
- **Brazil–Europe, one way**, per the official table in force since 2026-03-02:

| Cabin | Until 2026-11-22 | From 2026-11-23 (+20%) |
|---|---|---|
| Economy | 80,700 | ≈ 96,840 (computed: +20%, not yet published) |
| Premium Economy | 90,700 | ≈ 108,840 (computed) |
| Business | 201,600 | 241,920 |
| First | 336,000 | 403,200 |

- **Partner bookings made by 2026-11-22 use the old table.** For any partner award the user is considering, mention this deadline.
- **Partner economy to Europe is poor value for this user.** 80,700 miles is about R$ 1,775 per person at a typical R$ 22/milheiro cost, so it rarely beats cash from Europe. LATAM's own metal (dynamic) is usually the better use.

Sources:
- [LATAM table, economy](https://web.latampass.latam.com/pt_br/viagem/usar-milhas-para-voar/regras-de-resgate/latam/classe-economica)
- [Melhores Destinos on the November 2026 increase](https://www.melhoresdestinos.com.br/milhas/aumento-tabela-fixa-latam-nov26)
- [Seu Crédito Digital](https://seucreditodigital.com.br/latam-pass-aumenta-resgate-novembro-2026/)

Confidence: LIKELY.

## Family rules

From `data/family-booking.json`:
- **Infant under 2 (all segments):** about 10% of the adult miles plus taxes.
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
