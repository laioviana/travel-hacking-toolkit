---
name: azul-fidelidade
description: Azul Fidelidade (formerly TudoAzul) award rules for a Brazilian with a CPF. Azul pelo Mundo awards to Lisbon, TAP flights bookable with Azul points, beneficiary list limits, 90 day fee, Seats.aero coverage without seat counts. Use whenever Azul points, Azul flights to Lisbon or a TAP award from Brazil are an option.
category: loyalty
summary: Azul Fidelidade awards. Lisbon flights, TAP awards, beneficiary rules. Seats.aero hides seat counts.
api_key: None (local data)
---

# Azul Fidelidade

The program was called TudoAzul until 2024. Check the user's Azul balance and cost basis with `my-points`. Livelo and Esfera transfer 1:1 (see `data/transfer-partners.json`); run `bonificadas` first.

**Keep exposure low.** `brazil-programs` notes Azul went through a restructuring in 2025 to 2026. Do not hold a big balance without a booking in sight.

Every fact has a source and a confidence level. UNVERIFIED means confirm on voeazul.com.br first.

## Availability

- **Seats.aero covers Azul** (source `azul`) but **hides seat counts**. Mark any 3-seat result "3 seats unverified" and confirm on the Azul site.
- Confidence: VERIFIED in this toolkit (`seats-aero` skill, `data/home-routes.json`).

## What Azul Fidelidade is good for

- **Azul nonstop VCP or GRU area to Lisbon (Azul pelo Mundo).** Price is dynamic, there is no fixed table. Alert posts quoted economy from about 43,000 to 87,000 points per segment plus taxes depending on date. Sources: [Pontos pra Voar, 71,200 points](https://pontospravoar.com/alerta-ppv-passagens-lisboa-71200-pontos-azul-fidelidade-taxas/), [Pontos pra Voar, 87,000 points](https://pontospravoar.com/alerta-passagens-ppv-voos-portugal-partir-87-mil-pontos-azul-fidelidade/). Confidence: UNVERIFIED (single-date alerts, treat as range only).
- **TAP flights with Azul points.** TAP allows partner awards including business class through Azul and Smiles. One report quotes business Brasilia to Lisbon from 186,000 points per segment plus taxes, with very limited seats and a "commercial fare" type that has more seats but much higher points. Source: [Passageiro de Primeira, 2025-02-06](https://passageirodeprimeira.com/tap-executiva-award/). Confidence: UNVERIFIED (blog, over a year old, figure shown only as an image for Azul vs Smiles).
- This is how a Fortaleza family could reach LIS on TAP and then Europe, see `ams-for`.

## Rules

| Rule | Detail | Source | Confidence |
|---|---|---|---|
| Booking for others | Passenger must be on a pre-registered beneficiary list. Slots depend on tier, sources disagree (5 to 15). | [Pontos pra Voar](https://pontospravoar.com/como-funciona-limitacao-cpf-emissao-passagens-pontos/) | UNVERIFIED |
| Fee | Between R$ 69.90 and R$ 189.90 when booking under 120 days out without the account holder on the booking. | same | UNVERIFIED |
| Late taxes | An extra fee applies to some emissions under 90 days out, except Diamante. | [Pontos pra Voar](https://pontospravoar.com/alerta-ppv-passagens-lisboa-71200-pontos-azul-fidelidade-taxas/) | UNVERIFIED |
| Child 2 to 11 | No child discount (older source). | `data/family-booking.json` | UNVERIFIED |
| TAP partner awards | No fixed table, price follows the fare type offered. | [Passageiro de Primeira](https://passageirodeprimeira.com/tap-executiva-award/) | UNVERIFIED |

## Gaps

No 2026 official Azul partner table found. Infant rules, change fees and the exact taxes on Lisbon flights were not found. Never guess them: read them at checkout.

## Workflow

1. Search `azul` on Seats.aero for the route, then confirm seats on the Azul site.
2. Price in points per passenger times the party, add taxes in R$, convert to R$ per milheiro against the cost basis.
3. Flag the beneficiary list and the fee window before recommending a booking for the other travellers.
4. Compare with TAP Miles&Go (`tap-miles-go`) for the same TAP flight.
