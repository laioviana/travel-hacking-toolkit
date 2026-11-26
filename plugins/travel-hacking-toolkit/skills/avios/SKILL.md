---
name: avios
description: Avios across Iberia Club, British Airways, Qatar Privilege Club, Aer Lingus and Finnair. Iberia off-peak pricing, Combine Avios rules, cheapest paths in from Esfera, Livelo and Amex NL MR, reading Seats.aero qatar results as a stand-in, Iberia infant and child pricing, Iberia Madrid to Fortaleza, and Finnair Plus fixed chart for LATAM flights (6,000 Avios one way for any domestic Brazil flight). Use for any Iberia, BA or Avios award, including AMS to Fortaleza via MAD, and for any LATAM flight inside Brazil.
category: loyalty
summary: Avios and Iberia Club. Off-peak pricing, Combine Avios, cheapest paths in, Qatar stand-in, MAD-FOR, Finnair fixed chart for LATAM Brazil.
api_key: None (Seats.aero source qatar as stand-in)
---

# Avios (Iberia first)

One currency across Iberia Club, British Airways, Qatar, Aer Lingus, Vueling, Finnair. Account and link data lives in `data/avios-family.json`. For this user the point is **Iberia metal, Madrid to Fortaleza**, with Avios moved into Iberia by the cheapest path.

Every fact has a confidence level. Never fill a price from memory. Mark gaps UNVERIFIED.

## Iberia pricing

- Iberia Club (renamed from Iberia Plus in June 2025) prices its **own flights by distance, with peak and off-peak** dates. A devaluation of roughly 19% landed in June 2025. LIKELY. Source: https://princeoftravel.com/points/iberia-club/
- **Partner awards (BA, etc.) booked with Iberia use BA pricing, no off-peak.** So Iberia Avios are best used on Iberia metal.
- Iberia publishes its peak calendar. Check it on iberia.com. The exact page and the Fortaleza peak dates are **UNVERIFIED**. Use the booking calendar view and read the price for the actual date.
- Booking window about 360 days. Cancelling Iberia metal costs about EUR 25 per booking. LIKELY, single source.
- Iberia metal surcharges are far lower than BA's. Taxes are paid in cash on top. Convert with `scripts/fx.py`.
- Iberia runs periodic discount weeks (10 to 20% off Iberia-operated awards) and Esfera to Iberia bonuses. Check `bonificadas` first. Example found: promotion to 2027-03-18 travel, ended 2026-09-23. Source: https://www.melhoresdestinos.com.br/milhas/iberia-voos-avios-20-desconto-set26

## Madrid to Fortaleza (key route)

Iberia launched MAD-FOR in January 2026 on the A321XLR (3 weekly, 4 from March 2026). LIKELY. Source: https://aviacionaldia.com/en/2026/01/iberia-launches-new-madrid-fortaleza-route-with-airbus-a321xlr.html

Observed award prices (one way, Avios, taxes extra). **These are dated promo or alert prices, not a chart.** Re-check live:

| Cabin | Observed | Source and date | Confidence |
|---|---|---|---|
| Economy | from 13,600 (Sept 2026 discount) | https://www.melhoresdestinos.com.br/milhas/iberia-voos-avios-20-desconto-set26 | LIKELY |
| Economy | from 16,000 (Nov to Dec dates, Feb 2026 article) | https://www.melhoresdestinos.com.br/milhas/passagens-iberia-madri-fev26 | LIKELY |
| Business | 34,000 to 40,500 (about USD 121 taxes in one example) | https://pontospravoar.com/alerta-passagens-ppv-classe-executiva-iberia-madri-partir-34000-avios/ | UNVERIFIED |

The Fortaleza off-peak vs peak price is **UNVERIFIED**.

For AMS to FOR, the AMS to MAD leg is separate: Iberia, KLM, Vueling, Transavia or cash. Alternatively Iberia sells AMS-MAD-FOR on one award. Search the full itinerary on iberia.com.

## Finnair Plus: LATAM flights inside Brazil

Finnair Plus prices LATAM-operated flights on a **fixed chart**, while LATAM Pass prices its own flights dynamically. On expensive domestic dates (GRU–FOR in high season, last-minute) the fixed price can win by a wide margin. Data lives in `data/avios-family.json` under `finnair_latam_chart`.

| LATAM Brazil, one way, per person | Economy | Business | Confidence |
|---|---|---|---|
| Domestic Brazilian flights | 6,000 | 14,000 | VERIFIED |
| Brazil to South America | 13,000 | 20,000 | LIKELY |
| Brazil to Central and North America | 28,500 | 74,500 | LIKELY |
| Brazil to Europe | 33,500 | 90,000 | LIKELY |

Source: finnair.com partner award page, checked 2026-11-25. Taxes extra in cash. Re-check the page before transferring.

**When to use it:** any LATAM flight inside Brazil, including the domestic leg of AMS–FOR via GRU or the positioning leg of a trip from Fortaleza. Always price LATAM Pass for the same flight (`latam-pass` skill) and compare the R$ cost of 6,000 Avios with the LATAM Pass miles at their cost basis.

**How to book:**
1. Find LATAM saver space first in **Iberia Club or BA** search (award space is shared across partners). Seats.aero does not show LATAM domestic space.
2. Move enough Avios into Finnair Plus **before** asking. Since about November 2026 the chat agent only checks partner space when the balance already covers the award. LIKELY.
3. Ask the Finnair Plus **chat** (English) or phone to book it. LATAM awards can't be booked on finnair.com. Ticketing happens within a day.

**Rules (finnair.com terms, VERIFIED unless marked):**
- Price is per person, one way or round trip. LATAM-operated flights only, no mixing two partners on one award.
- Mixed cabins price at the highest cabin. Change and cancellation fees apply. No waitlist.
- Connections must be the first possible flight, no stopovers. Whether a connecting domestic itinerary (e.g. GRU–BSB–FOR) is still one 6,000 award is **UNVERIFIED**. Ask the agent to price the full itinerary.
- **Business:** a July 2026 test found LATAM business space that Iberia and BA could book but Finnair could not. Plan on economy. UNVERIFIED.
- **Children and infants:** no child discount published. Infant pricing on LATAM through Finnair is **UNVERIFIED**. Ask the agent before moving Avios for a party with a lap infant.

**Getting Avios into Finnair Plus** (`cheapest_paths_into_finnair`):

| From | Path | Source points per Avios | Confidence |
|---|---|---|---|
| Rove | Rove to Finnair direct 1:1 | 1.0 | LIKELY |
| Amex NL MR | MR to BA 5:4, then BA to Finnair combine | 1.25 | UNVERIFIED |
| Esfera | Esfera to Iberia 2:1, then Iberia to BA to Finnair combine | 2.0 | LIKELY |
| Livelo | Livelo to Qatar 3:1, then Qatar to BA to Finnair combine | 3.0 | LIKELY |

The combine rules above apply (1:1, matching names, 30-day account age). Open the Finnair Plus account early so it clears the 30-day rule before you need it.

## Availability: Seats.aero `qatar` as stand-in

- Iberia is **not on Seats.aero**. Qatar Privilege Club is, and Qatar can book oneworld partners, so Qatar results hint at space on Iberia-operated flights. Treat as a **hint, not proof**: LIKELY at best. Always confirm on iberia.com with the calendar view.
- Qatar does not show Iberia's off-peak price. Price only from Iberia's own page.
- Qatar results do not hide seat counts for the party reliably. Mark "3 seats unverified" (see `seats-aero`).

## Getting Avios into Iberia

From `data/avios-family.json` and `data/transfer-partners.json`:

| From | Cheapest path | Cost in source points per Avios | Confidence |
|---|---|---|---|
| Esfera | Esfera to Iberia direct, 2:1, starting amount 15,000 | 2.0 | LIKELY |
| Livelo | Livelo to Qatar 3:1, then Qatar to BA to Iberia (combine) | 3.0 (direct to Iberia is 3.5) | LIKELY |
| Amex NL MR | MR to BA 5:4, then BA to Iberia combine | 1.25 (direct to Iberia is 1.5) | UNVERIFIED |

- Combine ratio 1:1. Name must match. Account must be at least 30 days old to move Avios out. **One 2026 source says Avios combined into Iberia are locked for 90 days. UNVERIFIED, conflicts with the data file.** Plan 3 months ahead, or test with a small amount early. Source: https://princeoftravel.com/points/iberia-club/
- Transfers into BA/Qatar and the combine take time. Iberia has **no holds** (`award-holds`), so move the Avios first only after confirming space and the combine timing, and buy only what the award needs.
- Always check `bonificadas` for an Esfera to Iberia bonus. Esfera at 2:1 plus a bonus is usually the cheapest Avios.
- **Compare against the cost basis.** The cost of an Avios is the source currency cost basis times the ratio.

## Pooling

Iberia Family Account (2 to 7 members) and BA Household (up to 7, same address) are in `data/avios-family.json`. LIKELY. Sources: https://www.headforpoints.com/2026/02/06/iberia-club-family-account/

## Infants and children

From `data/family-booking.json`:
- **Infant under 2:** 10% of the adult Avios price, economy only. Add through the Iberia app, the website blocks it. UNVERIFIED.
- **Child 2 to 11:** no published Avios child discount found. **UNVERIFIED.** Cash child discounts vary by fare. Check the booking engine breakdown.

## Output

Per option: Avios per person and for the family, taxes in R$, source currency cost to buy those Avios, R$ per milheiro against cost basis, whether the price is peak or off-peak, and whether availability was confirmed on iberia.com or only hinted by Qatar.
