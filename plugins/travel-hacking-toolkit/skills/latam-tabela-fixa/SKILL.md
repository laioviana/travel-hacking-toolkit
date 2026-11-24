---
name: latam-tabela-fixa
description: LATAM Pass Tabela Fixa, the fixed award chart for flights operated entirely by LATAM partners (Iberia, British Airways, Qatar, Delta, Lufthansa, Swiss, Qantas, JAL, Cathay and others). Full official region-to-region chart for every cabin, before and after the 20 percent increase of 2026-11-23, region lookup by country, the one-charge-per-region-pair pricing rule, the no-infants rule, and booking by phone or WhatsApp. Use whenever LATAM Pass miles could pay for a non-LATAM flight, for Iberia Madrid to Fortaleza on LATAM miles, or when someone says tabela fixa, resgate com parceiras or emissão pela central.
category: loyalty
summary: LATAM Pass fixed partner award chart. Official region matrix, calculator, booking by phone or WhatsApp.
api_key: None (local data)
---

# LATAM Pass Tabela Fixa (partner awards)

The tabela fixa prices **flights operated 100% by a LATAM partner** from a fixed chart keyed on cabin and regions. LATAM-operated flights never use it, since those are priced dynamically on the site (see the `latam-pass` skill). Get the user's LATAM Pass balance and `avg_cost_per_milheiro_brl` with `my-points`.

- **Data:** `data/latam-tabela-fixa.json`. Official chart, current and previous, all four cabins, plus the region table and partner list. Read from latampass.latam.com on 2026-11-24 and checked cell by cell. Confidence: VERIFIED.
- **Calculator:** `scripts/latam_tabela_fixa.py`. Use it rather than reading matrices by hand.

```bash
python3 scripts/latam_tabela_fixa.py Brasil Espanha Holanda --cabin business --pax 3 --cost 22
```
```bash
python3 scripts/latam_tabela_fixa.py --row Europa --cabin economy
```
```bash
python3 scripts/latam_tabela_fixa.py --region Turquia
```
```bash
python3 scripts/latam_tabela_fixa.py --diff
```

Stops can be a region (`Europa`), a country in Portuguese as LATAM writes it (`Países Baixos`, `Holanda`, `Qatar`), or an alias (`EU`, `US`, `ME`). Add `--cash` and `--taxes` (R$, whole party) to get the R$ per milheiro achieved. Add `--table previous` for pre-2026-11-23 prices.

## How the price is built

1. **Map each stop to its LATAM region.** LATAM's regions are its own, not geographic, and some placements are counterintuitive:
   - **México:** América do Norte
   - **Caribbean and Panamá:** América Central
   - **Turquia, Egito, Israel, Geórgia:** Oriente Médio
   - **Índia:** Ásia Ocidental
   - **Maldivas, Sri Lanka:** Ásia Oriental
   - **Rússia, Portugal:** Europa

   Argentina has its own row in economy only.
2. **Charge each distinct origin-region > destination-region combination once.** Connections inside a combination that's already been charged are free. Official example: RIO–MIA–NYC–ATL = Brasil>América do Norte + América do Norte>América do Norte (the second charged once, although there are two US-US legs).
3. **A routing through a third region adds that region's legs.** The table price applies only "if a partner flies the destination without passing through a new region". So GRU–DOH–AMS on Qatar is Brasil>Oriente Médio + Oriente Médio>Europa, **not** Brasil>Europa, and that costs far more. Always route via a hub in the origin or destination region when you can.
4. **Price is per passenger, one way.** Round trip = the sum of both directions.
5. **Brasil>Brasil is 0 in the chart.** Domestic Brazil partner flights aren't priced here, so ask the call center.

## Current chart, the rows that matter for this user

Miles per passenger, one way, valid from 2026-11-23. Previous value in brackets where it changed. Every change was +20%, except one LATAM typo, shown by `--diff`.

| From > To | Economy | Premium Economy | Business | First |
|---|---|---|---|---|
| Brasil > Europa | 96,840 (80,700) | 108,840 (90,700) | 241,920 (201,600) | 403,200 (336,000) |
| Brasil > América do Norte | 68,400 (57,000) | 90,720 (75,600) | 162,000 (135,000) | 259,200 (216,000) |
| Brasil > Oriente Médio | 145,800 (121,500) | 264,600 (220,500) | 350,400 (292,000) | 453,600 (378,000) |
| Brasil > América do Sul | 24,000 | 43,200 | 48,000 | 84,000 |
| Europa > Europa | 28,800 (24,000) | 64,800 (54,000) | 86,400 (72,000) | 86,400 (72,000) |
| Europa > Oriente Médio | 43,200 (36,000) | 85,200 (71,000) | 96,000 (80,000) | 112,800 (94,000) |
| Europa > América do Norte | 51,840 (43,200) | 77,760 (64,800) | 194,400 (162,000) | 259,200 (216,000) |
| Europa > Ásia Oriental | 72,000 (60,000) | 99,600 (83,000) | 172,800 (144,000) | 230,400 (192,000) |
| Europa > Ásia Ocidental | 48,000 | 95,000 | 120,000 | 168,000 |
| Europa > Oceania | 60,000 | 71,000 | 144,000 | 192,000 |

For any other pair, run `--row <region>`.

## Partners

Air partners per LATAM, 2026-11-24:
- Aerolíneas Argentinas
- Aeroméxico
- Austrian
- British Airways
- Cathay Pacific
- Delta
- Finnair
- Iberia
- Japan Airlines
- Lufthansa
- Qantas
- Qatar Airways
- Royal Jordanian
- Swiss
- Virgin Atlantic

That list is LATAM's earning page, so the call center confirms whether a given partner can be redeemed. **Not partners:** Air France, KLM, TAP, Emirates, Turkish, United, American. Use `smiles`, `flying-blue`, `tap-miles-go` or `avios` for those airlines.

## Where it pays for this user

Value every option in R$ per milheiro against the LATAM cost basis and `brl_milheiro.latam_pass` in `data/points-valuations.json`.

- **Iberia MAD–FOR nonstop is a partner flight.**
  - FOR–MAD is Brasil>Europa. Adding MAD–AMS on Iberia adds Europa>Europa, as a new combination.
  - Per person, current table: economy 96,840 + 28,800 = **125,640**; business 241,920 + 86,400 = **328,320**.
  - Compare with Iberia Avios (`avios` skill) and with cash. Economy at these prices rarely beats Avios off-peak or cash. Business can, when the cash fare is high.
  - Positioning AMS–MAD on cash or Avios can be cheaper than the Europa>Europa leg in miles.
- **Qatar Qsuite AMS–DOH in business, 96,000** (Europa>Oriente Médio). A strong short-haul business use. Onward from DOH adds another region pair.
- **Europa > Ásia Ocidental and Europa > Oceania didn't go up.** Business is 120,000 and 144,000. Oceania only works on a partner flying Europe to Oceania without a stop in another region, such as Qantas PER–LHR. Via DOH or HKG adds the hub's region.
- **Avoid:**
  - Brazil to Europe via the Middle East (Qatar via DOH): 350,400 + 96,000 in business.
  - Short Europe>Europe economy hops at 28,800 when the cash fare is under about R$ 700. Do the math with `--cost`.
- **Brazil to South America didn't go up:** 24,000 economy, for example Aerolíneas Argentinas from Brazil.

## Rules that kill bookings

- **No infants under 2.** LATAM states that partner awards on the tabela fixa can't be issued for children under 2. With a lap infant in the party, either buy the infant ticket from the operating airline, or pick another program. Check every child's age on the travel date against `data/family-booking.json`.
- **Children 2 and over:** assume full miles.
- **Availability belongs to the partner and can change on the same day as the quote.** LATAM may see different space than the partner's own site.
- **Confirm availability with the call center before buying or transferring miles.** LATAM says so explicitly. Livelo and Esfera transfers can take days (`award-holds`, `bonificadas`).
- **Taxes are charged in R$ on top.** The amount isn't published, so read it at quote time and add it to the comparison.
- **Unknown:** change and cancellation fees, mixed-cabin pricing, and whether A>B and B>A count as one combination. Ask the agent, and don't assume.

## Finding space before calling

LATAM has no online search for partner awards. Treat these as proxies, then confirm by phone:
- **Seats.aero (`seats-aero`):**
  - `qatar` results show Qatar and oneworld saver space, which stands in for Iberia, BA, Finnair and Qatar.
  - `delta`, `virginatlantic` and `qantas` sources show their own metal.
  - Confidence: UNVERIFIED that LATAM sees the same space.
- **The partner's own award search,** for example iberia.com with Avios. Seat counts there are only an indication.

## Booking

- **Phone:** 4002-5700 (capitals) or 0300 570 5700 (rest of Brazil). Give your CPF or LATAM Pass number and ask for the *central de emissões com tabela fixa*.
  - Don't say you found the seat on another airline's site, since agents may refuse.
  - If an agent says it can't be priced, call again.
- **WhatsApp:** +56 9 6825 0850. Send **one** message with no greeting first, or the bot won't route it:
  ```
  Ida ou Ida e Volta:
  Origem e destino:
  Data de ida (AAAA-MM-DD):
  Data de volta (AAAA-MM-DD):
  Cabine:
  Adultos:
  Crianças:
  Bebês:
  ```
- **Booking for others:** uses the LATAM Pass beneficiary limit in `data/family-booking.json`.
- **Contacting LATAM sends a message on the user's behalf.** Draft the call script or WhatsApp text, and let the user send it.

## Output

For each tabela fixa option, give:
- the region pairs charged (from the calculator), miles per person and for the party, and taxes in R$
- R$ per milheiro achieved, vs the LATAM cost basis and the floor
- a flag for any infant in the party (not bookable), and the routing-through-a-third-region penalty when it applies
- "Confirm on the call center before moving miles"

## Sources

- [LATAM Pass, regras de resgate (parceiras)](https://latampass.latam.com/br/pt/regras-de-resgate), read 2026-11-24
- [LATAM Pass, tabela de regiões](https://latampass.latam.com/br/pt/regras-de-resgate/tabela-de-regioes), read 2026-11-24
- [LATAM Pass, companhias aéreas parceiras](https://latampass.latam.com/br/pt/aereas-parceiras), read 2026-11-24
- [Passageiro de Primeira, como emitir pela tabela fixa](https://passageirodeprimeira.com/como-emitir-voos-tabela-fixa-latam/) (phone and WhatsApp flow)
- [Passageiro de Primeira, reajuste de 2026-11-23](https://passageirodeprimeira.com/valendo-latam-pass-reajusta-tabela-fixa-de-resgate-com-companhias-parceiras/)

Refresh: if `_meta.last_verified` in the data file is older than 60 days, re-read the official page in the browser and update the matrices.
