---
name: brazil-programs
description: How the Brazilian points ecosystem works for this user. Livelo and Esfera bought in promos, transfers to Smiles, LATAM Pass and Azul Fidelidade, cost-basis math in R$ per milheiro, Clube subscriptions, booking for family members with a CPF, and when each program is the right one. Use whenever Livelo, Esfera, Smiles, LATAM Pass, Azul, milhas, milheiro or bonificada comes up, or when a trip touches Brazil.
category: reference
summary: Livelo, Esfera, Smiles, LATAM Pass and Azul. Cost basis in R$ per milheiro and when each program wins.
api_key: None (local data)
---

# Brazilian Programs

Reference for the Brazilian side of this user's points. Data lives in:
- **`data/transfer-partners.json`** (`livelo`, `esfera`): base ratios and minimums.
- **`data/points-valuations.json`** → `brl_milheiro`: market value floors and ceilings in R$.
- **`data/point-costs.json`**: purchase price references and the bonus formula.
- **`data/family-booking.json`**: child pricing and booking-for-others limits.
- **`data/my-balances.json`**: the user's balances and their own `avg_cost_per_milheiro_brl`.
- **`bonificadas` skill**: what's on sale or bonused right now.

## How this user plays it

- **No Brazilian earning card.** Livelo and Esfera points are **bought in promotions**. Their value is what was paid, not a published valuation.
- **Points stay in Livelo or Esfera** until a specific award is found. Then they move with a bonus.
- **The user is Brazilian with a CPF.** Smiles, LATAM Pass and Azul accept Brazilian payment for taxes and fees, so all three are real booking options, not just signals.
- **All prices are in R$.**

## Unit: R$ per milheiro

Brazilians value miles per 1,000 ("milheiro"), in BRL. For any redemption:

```
value_per_milheiro = (cash fare in R$ − taxes paid on the award in R$) / miles × 1000
```

Convert EUR/USD fares first: `python3 scripts/fx.py <amount> EUR`.

**Verdict**, comparing the value per milheiro against the user's cost basis:
- **Below cost basis:** losing money vs. what was paid. Say "pay cash."
- **Between cost basis and the `brl_milheiro` floor:** acceptable only if the cash alternative is painful.
- **Above the ceiling:** an exceptional redemption. Say so.

## The programs

### Livelo (bank currency)
- **Where it goes:**
  - 1:1 to Smiles (min 10,000), LATAM Pass (min 12,000) and Azul (min 1,000)
  - 3:1 to Qatar Avios, which beats Iberia direct at 3.5:1. Combine into Iberia via `data/avios-family.json`.
  - 3.5:1 to Flying Blue, BA and Accor
- **Timing:** credit takes up to 7 business days.
- **Clube Livelo** lowers the LATAM/Smiles minimums and unlocks higher bonus tiers.

### Esfera (bank currency)
- **Where it goes:**
  - 1:1 to Smiles, LATAM Pass and Azul
  - **2:1 to Iberia**, the cheapest Avios from any currency this user has
  - 2.7:1 to TAP (2.2:1 with Clube Esfera)
- Some partner bonuses exclude Esfera ("exceto Esfera").

### LATAM Pass
- **Often the cheapest miles to hold,** when bought in promos. Check the user's `avg_cost_per_milheiro_brl`.
- **Own flights are dynamically priced** and searchable on the site. **Partner flights use a fixed table** and are bookable by phone or WhatsApp only.
- Not on Seats.aero.
- Details in the `latam-pass` skill.

### Smiles (GOL)
- **The main value is partner awards on Air France/KLM and others,** plus frequent Smiles "promo" award sales.
- **On Seats.aero** (`smiles`), with seat counts.
- **No child discount on awards.** The infant fee is paid in cash.
- **Booking for others:** 25 people per calendar year.

### Azul Fidelidade (formerly TudoAzul)
- **Covers Azul flights and TAP via Lisbon.**
- **On Seats.aero** (`azul`), without seat counts. Mark any 3-seat result "unverified."
- **Beneficiaries:** passengers must be on a pre-registered list, and a fee applies when booking under 120 days out without the account holder on the booking.
- **Keep the balance low.** Azul went through a restructuring in 2025–2026.

## Family bookings

When one person holds all the points, every award for the other travellers is a booking for someone else:
- **Limits and fees:** see `data/family-booking.json` → `booking_for_others`.
- **Children 2–11:** the Brazilian programs charge full miles. Flying Blue gives 25% off.
- **Price the whole party** from the profile.

## When each program wins (AMS ⇄ Brazil)

| Situation | Program |
|---|---|
| Air France via CDG | Flying Blue (direct balance) vs. Smiles fed by bonused Livelo/Esfera. Compare R$ after the child discount. |
| Iberia via MAD | Iberia Avios. Top up from Esfera at 2:1, or Livelo via Qatar at 3:1. |
| LATAM via LIS or GRU | LATAM Pass |
| TAP via LIS | Azul Fidelidade or TAP Miles&Go (via Esfera) |
| Domestic Brazil leg | LATAM Pass, Smiles or Azul. Often cheap in promos. |

## Never

- **Recommend a transfer without checking `bonificadas`.**
- **Recommend buying points without a redemption in sight.**
- **Treat Smiles or Azul results as signal-only for this user.**
