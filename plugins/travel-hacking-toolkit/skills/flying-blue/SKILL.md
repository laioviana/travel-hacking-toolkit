---
name: flying-blue
description: Air France KLM Flying Blue awards. Monthly Promo Rewards, dynamic pricing, Light Standard Flex fares, taxes and surcharges on awards from AMS vs BRU or DUS, phone holds, the 25 percent child discount, Flying Blue Family pooling, and cheapest ways in from Amex NL MR, Livelo and Esfera. Use for any Air France or KLM award, including AMS to Fortaleza via CDG.
category: loyalty
summary: Flying Blue awards. Promo Rewards, dynamic pricing, taxes, holds, child discount, Family pooling, Amex NL 2 to 1.
api_key: None (Seats.aero source flyingblue)
---

# Flying Blue

Air France and KLM program. Priority use for this user: **AMS or CDG to Fortaleza on Air France** (see `ams-for`), plus Promo Rewards to anywhere else.

Every fact below carries a confidence level. Sources are secondary blogs unless stated. Confirm on flyingblue.com before transferring anything. Never fill a price from memory.

## Search

- **Seats.aero source: `flyingblue`.** Cached data. Use the `seats-aero` skill and pull ALL programs first, per `lessons-learned`.
- **Party:** search `party.default_seats` from the profile. Seats.aero shows counts for Flying Blue, so drop results under the party size.
- **Final price check** is on airfrance.com or klm.com (award search). Seats.aero does not know about Promo Rewards discounts or the child discount.
- **One-way awards.** Mix freely with other programs, for example Flying Blue out and Iberia back (`avios`).

## Pricing (dynamic)

- Award prices are dynamic and vary by date. Partner airlines (Delta, Korean, etc.) are priced differently from AF/KL metal.
- **Fare tiers since 2026-09-08:** Light, Standard, Flex. The Promo Rewards price is the Light fare. Light in Economy and Premium Economy has no checked bag and cannot be changed or refunded. Standard costs EUR 70 to change or cancel, Flex is free. Tickets issued before that date keep the old conditions. Confidence: LIKELY (one detailed secondary page). Source: https://skystatus.pro/guide/md/en/flying-blue-promo-rewards.md
- **Always compare Light vs Standard** for a family with a young child. A non-refundable ticket for three is a real risk.

## Promo Rewards (monthly)

- Up to 25% off the minimum rate on selected **Air France and KLM** routes. Partner airlines excluded. The discount applies to the lowest price tier, so it only helps on dates where the saver price is available.
- New list appears around the **1st of each month**. Check on the 1st, popular business routes sell out within days.
- Each month states its own travel window, for example November 2026 bookings could fly until 2027-04-30. Book on the Air France or KLM site.
- Long-haul includes South America, but whether Brazil or Fortaleza is in a given month changes monthly. Check the current list every time.
- **Does not necessarily stack with the child discount.** Sources conflict (older: no stacking, a later one: stacks). UNVERIFIED. Price the child both ways on the booking engine.
- Confidence: LIKELY. Sources: https://skystatus.pro/guide/md/en/flying-blue-promo-rewards.md , https://onemileatatime.com/airfrance-klm-discounted-awards , https://milesopedia.com/en/rewards/special-offers/flying-blue-promo-rewards/

## Taxes and surcharges

- Taxes and carrier surcharges (YQ) are **always paid in cash**, in EUR. Convert with `python3 scripts/fx.py` and compute R$ per milheiro on the total out of pocket.
- Air France KLM raised surcharges on Flying Blue awards from June 2025. LIKELY. Source: https://milesopedia.com/en/news/programs/flying-blue-surcharges-on-the-rise-real-cost-for-canadians/
- **AMS vs BRU vs DUS departure:** carrier surcharges are generally the same, the difference comes from government airport taxes (Germany reported as the most expensive departure country outside UK and France). No source gives current AMS, BRU and DUS totals. **UNVERIFIED.** Do not recommend positioning to BRU or DUS for taxes alone. Instead price the same date from each airport on the booking engine and compare the tax line, then add the positioning cost (`deutsche-bahn` for DUS).
- Delta-operated partner awards are reported to carry no fuel surcharges. UNVERIFIED single source.

## Holds

From `data/award-holds.json` (VERIFIED there): holds exist but need a **phone call**, up to about 3 days, with a phone booking fee of about USD 25 when finalising. Partner holds are agent-discretionary. Hold first, then transfer Amex NL MR. See `award-holds`.

## Children and infants

From `data/family-booking.json`:
- **Child 2 to 11: 25% off the award in miles**, any cabin, book on the AF or KL site. One source says up to 12, most say 11. LIKELY.
- **Does the child need to be in a Flying Blue Family pool?** One 2026 guide says the site names no such condition, another source says it may now be required. **UNVERIFIED.** Run the booking engine with the child's age and see whether the discount appears before transferring miles. If it does not, create the Family link and retry.
- **Infant under 2:** book via Flying Blue customer service. Price not verified.
- Work out the child's age on every segment date.

## Flying Blue Family (pooling)

- Max 8 members: 2 adults plus up to 6 children. Only the **leader** (18+) transfers and books. Transfers go one way, member to leader, are free and cannot be reversed.
- Each member needs to have been in Flying Blue at least 7 days (another source says 24 hours for a new account). First transfer can take up to 72 hours. Commitment of at least 6 months. Miles pooled are valid 2 years after each transfer.
- XP is not shared.
- Useful when the points holder is the leader and the other adult also holds Flying Blue miles.
- Confidence: LIKELY. Sources: https://skystatus.pro/guide/md/en/flying-blue-family-account.md , https://www.flyingblue.com/en/landing-page/informative/family-youngs (official, not fetched)

## Getting miles in

Ratios from `data/transfer-partners.json`:

| From | Ratio | Notes |
|---|---|---|
| Amex NL MR | 2 MR : 1 mile | Dropped from 5:4 on 2026-07-01. LIKELY. Instant. Run `transfer-bonuses` for NL promos. |
| Livelo | 3.5 : 1 | Minimum 3,500 Livelo. LIKELY. |
| Esfera | 3.5 : 1 | LIKELY. |

- Check `bonificadas` for Livelo/Esfera bonus to Flying Blue before moving points. At base ratio these are expensive: 3.5 Livelo per mile means a mile costs 3.5 times the Livelo cost basis.
- **Cheapest currency first.** Compare cost per Flying Blue mile from each currency (ratio times the cost basis in `data/my-balances.json`), then against the same seat on Smiles or LATAM Pass.
- Never move points without an award found. See `award-holds`.

## Output

For each option: miles per person and for the family, child discount applied or not, cash taxes in R$, R$ per milheiro against the cost basis and the `brl_milheiro` reference, fare tier (Light or Standard), and whether it came from a live booking page or Seats.aero cache.
