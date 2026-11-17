---
name: smiles
description: Smiles (GOL) award search and rules for a Brazilian with a CPF. Air France and KLM partner awards to Europe, Fortaleza to Europe via CDG, Seats.aero coverage, Clube Smiles price tiers, booking for others, promo weeks. Use whenever Smiles miles or an Air France or KLM award from Brazil is an option.
category: loyalty
summary: Smiles GOL awards. Air France and KLM partner awards, Seats.aero coverage, price tiers and booking rules.
api_key: None (local data)
---

# Smiles

Check the user's Smiles balance and cost basis with the `my-points` skill. Miles arrive from Livelo or Esfera (1:1, see `data/transfer-partners.json`), so always run `bonificadas` before moving points.

Every fact below carries a source and a confidence level. Anything marked UNVERIFIED must be confirmed on smiles.com.br before it drives a recommendation.

## Availability

- **Seats.aero covers Smiles** (source `smiles`) and reports seat counts, so the 3-seat filter works. Use `seats-aero` and filter `RemainingSeats >= 3`.
- Confidence: VERIFIED in this toolkit (see `data/home-routes.json` and the `seats-aero` skill).

## Price reference points (stale, do not quote as current)

Per segment and per passenger, economy, Air France or KLM metal, Clube Smiles or Diamante price vs everyone else. Source: [Pontos pra Voar, 2024-10-29](https://pontospravoar.com/resgate-passagens-europa-smiles-partir-92900-milhas/). Confidence: UNVERIFIED (single secondary, over a year old).

| Route | Airline | Clube or Diamante | Others |
|---|---|---|---|
| FOR to LIS | Air France | 102,400 | 125,000 |
| FOR to PRG | Air France | 92,900 | 110,000 |
| FOR to CPH | Air France | 96,100 | 114,000 |
| GIG to AMS | Air France | 110,500 | 130,000 |
| SSA to CDG | Air France | 113,300 | 142,000 |

What this shows: Smiles prices vary by month and fare (the article says these were the lowest per month), so there is no fixed table to quote. **Always read the live price on the Smiles site or Seats.aero**, then compute R$ per milheiro against the cost basis.

Two takeaways that likely still hold (LIKELY): a Clube Smiles subscription lowers the price per segment meaningfully, and the price is per segment, so a round trip costs two segments.

## Rules

| Rule | Detail | Source | Confidence |
|---|---|---|---|
| Taxes | Charged on top, amount not published in the sources found. Read it at checkout and add it in R$. | [Pontos pra Voar](https://pontospravoar.com/resgate-passagens-europa-smiles-partir-92900-milhas/) | UNVERIFIED |
| Child 2 to 11 | No child discount on award redemptions. | `data/family-booking.json` | UNVERIFIED |
| Infant under 2 | Typically 10% to 15% of the adult fare plus taxes on international flights, set by the operating airline. Reclame Aqui reports show customers paying the partner airline separately to add the baby after issuing adults with Smiles miles. Ask Smiles support and the operating airline before issuing. | [Melhores Destinos](https://www.melhoresdestinos.com.br/bebe-de-colo-aviao.html), [Reclame Aqui](https://www.reclameaqui.com.br/smiles/cobranca-abusiva-pata-bebe-de-colo-apos-compra-pela-smiles_iBwVsaxh6futIxO9/) | UNVERIFIED |
| Booking for others | 25 people per calendar year, resets 1 January. No fee reported. | [cartoesdecredito.me](https://www.cartoesdecredito.me/milhas/limite-de-cpf-azul-fidelidade-latam-pass-e-smiles-2026/) | LIKELY |
| Earning | Tickets issued with miles on KLM do not earn miles in Smiles. | [Smiles KLM page](https://www.smiles.com.br/klm) | LIKELY |

## Not found (gaps)

- Official Smiles partner award table for 2026: UNVERIFIED, one blog claims a fixed Europe table of 35,000 to 120,000 miles but its validity period is unclear.
- Cancellation and change fees: not found. The official Smiles help page on infants was not found either.
- Smiles Money (miles plus cash) pricing: not found.

## Workflow for AMS and FOR

1. Pull `smiles` results from Seats.aero for FOR to CDG, AMS, LIS and the reverse (`ams-for` runs this).
2. Keep results with at least 3 seats. Price per segment times 3 passengers (infants separately, in cash).
3. Cost in R$ equals miles divided by 1,000 times the user's cost basis for Smiles (after any bonificada), plus taxes in R$.
4. Compare with the cash family fare and with Flying Blue on the same Air France flight.
5. Warn that a booking for the other travellers counts against the 25-person annual limit.
