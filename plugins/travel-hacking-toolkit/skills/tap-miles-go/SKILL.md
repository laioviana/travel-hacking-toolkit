---
name: tap-miles-go
description: TAP Miles and Go award rules for a Brazilian booking Brazil to Lisbon and Europe. Dynamic own-flight pricing since 2026, transfer ratios from Esfera and Livelo, promo discounts, booking with a CPF. Use whenever TAP, Lisbon via TAP or Miles and Go points are an option, including Fortaleza to Lisbon.
category: loyalty
summary: TAP Miles and Go awards. Dynamic pricing, Esfera and Livelo ratios, Fortaleza to Lisbon.
api_key: None (requires browser)
---

# TAP Miles&Go

TAP flies Fortaleza to Lisbon (see `data/home-routes.json`). It is not on Seats.aero as its own program, so availability comes from the TAP site, or from `azul` and `smiles` results on TAP flights (see `azul-fidelidade`).

Every fact has a source and a confidence level.

## Pricing (changed in 2026)

Source for this section: [Passageiro de Primeira, 2026-07-30](https://passageirodeprimeira.com/tap-milesgo-amplia-resgates-com-milhas-adotando-tarifa-dinamica-para-voos-proprios/). Confidence: LIKELY (single secondary that cites TAP, one date).

- Own-flight awards moved from a semi-flexible table to **dynamic pricing** that follows the cash fare. Short-haul Europe can cost up to 45% fewer miles, long-haul can rise above the old levels in some periods.
- Old Brazil to Europe economy minimum was 39,500 miles, next level usually 53,000.
- Examples on 2026-10-16, taxes extra: GRU to LIS economy 49,000 miles, business 175,000. GRU to MAD economy 46,000, business 270,000. Treat as a snapshot, not a table.
- Any seat that is for sale can now be booked with miles, at a variable price.
- Economy Prime cannot yet be booked with miles.
- Taxes are charged on top. One blog estimates R$ 130 to R$ 250 per segment to Lisbon or Madrid ([Fabrica de Milha](https://fabricademilha.com/programas-de-milhas/tap-miles-go)), UNVERIFIED. Partner awards may charge taxes in EUR ([Buscamilhas](https://buscamilhas.com/blog/passagem-aereas-com-milhas/tabela-fixa-tap/)). Read the real figure at checkout.
- **Sources conflict on GRU to LIS economy**: 49,000 miles ([Passageiro de Primeira](https://passageirodeprimeira.com/tap-milesgo-amplia-resgates-com-milhas-adotando-tarifa-dinamica-para-voos-proprios/)) vs 32,500 miles on the 2026 table ([Alerta de Milhas](https://www.alertademilhas.com.br/blog/programas/tap-miles-go-brasileiro-como-funciona-vale-pena-2026)). Check the TAP site for the live number.

Promotions: TAP ran a 30% discount on Brazil to Europe awards until 2026-07-14 for travel until 2026-08-31 (expired). Source: [Passageiro de Primeira](https://passageirodeprimeira.com/?p=548912). Confidence: LIKELY. Look for the next one in `bonificadas`.

## Getting miles in

| From | Ratio | Source | Confidence |
|---|---|---|---|
| Esfera | 2.7:1, or 2.2:1 with Clube Esfera | [Passageiro de Primeira](https://passageirodeprimeira.com/tap-milesgo-amplia-resgates-com-milhas-adotando-tarifa-dinamica-para-voos-proprios/) and `data/transfer-partners.json` | LIKELY |
| Livelo | 1:1 only for Bradesco Centurion holders. Not the normal Livelo route. | same | LIKELY |
| Amex NL MR | Not verified. Check `data/transfer-partners.json` before suggesting. | | UNVERIFIED |

At 2.7:1 a Esfera point costs 2.7 times as much per TAP mile, so TAP via Esfera is usually worse than Azul or Smiles on the same flight. Do the arithmetic with the cost basis before recommending it.

## Rules

| Rule | Status |
|---|---|
| Child 2 to 11 | 25% off the miles of the fare available on the purchase date. Source: [TAP Miles&Go terms](https://www.flytap.com/en-us/legal-info/terms-and-conditions-miles-and-go). LIKELY (read via a search summary of the official page). |
| Infant under 2 | UNVERIFIED, not found. Read at checkout. |
| Booking for others | UNVERIFIED, still not found. Ask TAP support. |
| Holds | See `award-holds`. |
| Fixed partner table | TAP also revised a fixed table in 2026, sources disagree on the figures, UNVERIFIED. |

## Workflow for Fortaleza to Lisbon

1. Check TAP's own site for LIS and FOR on the dates, in miles and cash.
2. Check `azul` and `smiles` on Seats.aero for the same TAP flight.
3. Compute R$ per milheiro for each currency, including the 2.7:1 Esfera conversion.
4. Present whichever path is cheapest in R$ against cash and the cost basis.
