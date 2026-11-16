# Tailoring plan: Brazilian programs + Amsterdam base

Status: Phase 1 merged (PR #8). Phase 2 in progress.

## Profile (decided)

Personal details (party, ages, balances, purchase costs, status) live only in the gitignored `data/my-profile.json` and `data/my-balances.json`. This repo is public, so none of them belong in tracked files.

- **Base:** AMS. Positioning airports: EIN, RTM, BRU, DUS, CGN.
- **CPF holder,** so Brazilian programs can be booked with Brazilian payment methods.
- **All prices in BRL.** EUR/USD fares are converted with `scripts/fx.py`. Points are valued in **R$ per milheiro**.
- **Where points come from:**
  - Amex NL Membership Rewards is the only card currency.
  - Livelo and Esfera points are bought in promotions, so their value is the purchase cost plus any transfer bonus.
- **Cost basis:** per-program `avg_cost_per_milheiro_brl` in the balances file is the break-even line.
- **Party:** a family with a young child. Award searches need all seats on the same flight, and totals cover everyone. One person holds all the points, so awards for the others are bookings for someone else.
- **US-only skills:** archive them, don't delete.
- **Top route:** AMS ⇄ FOR (Fortaleza), at least once a year.

## Route focus: AMS ⇄ FOR

Nonstops into FOR from Europe, per the Wikipedia "Airlines and destinations" list (checked 2026-11-16):

| Gateway | Airline | Ways to book with points | Seats.aero covers it? |
|---|---|---|---|
| CDG | Air France | Flying Blue (direct balance + Amex NL MR), Smiles (via Livelo/Esfera), Azul Fidelidade? | Yes (`flyingblue`, `smiles`) |
| MAD | Iberia | Iberia Avios (direct), BA/Qatar Avios via a combine, Amex NL MR → Avios? | Partly (`qatar` stands in for Avios pricing) |
| LIS | TAP | TAP Miles&Go (Livelo/Esfera?), Azul Fidelidade, Smiles? | `azul`/`smiles` only |
| LIS (seasonal) | LATAM | **LATAM Pass, your biggest balance** | No |
| GRU/GIG/REC + domestic hop | LATAM / Azul / GOL | LATAM Pass, Smiles, Azul | Partly |

Combinations the agent should always check for AMS ⇄ FOR:

1. **AMS–CDG–FOR on Air France.** Compare Flying Blue (including Promo Rewards) with Smiles (bought Livelo/Esfera + bonus) on cost per R$.
2. **AMS–MAD–FOR on Iberia.** Iberia Avios off-peak pricing. Check the Avios fees and surcharges.
3. **AMS–LIS–FOR on TAP or seasonal LATAM.** LATAM Pass on its own flights (the main way to use a large LATAM balance), or TAP via Azul/Miles&Go. The AMS–LIS leg is paid cash or booked as a separate short-haul award.
4. **Mixed open-jaw.** For example, Flying Blue one way and Iberia Avios on the return. One-way awards make this free to combine.
5. **Positioning.** Start in BRU or DUS when the taxes or fares are lower.
6. **Cash baseline in R$**, from both the NL and BR markets. Buying from the BR market in BRL is sometimes cheaper.

A ready-made "AMS-FOR" recipe (Phase 3) runs all of this with a single command.

## Family travel (2 adults + 1 child)

What changes for the agent:

1. **Seat count = 3 by default.**
   - Seats.aero: drop results with `RemainingSeats < 3` when the program reports seat counts.
   - For programs that hide seat counts (Azul, Qatar, Turkish, Singapore), mark the result "3 seats unverified".
   - Cash searches use 2 adults + 1 child. In one of my existing rules, 2+ travellers means confirming availability for the whole party before any transfer.
2. **Child pricing by age on the travel date.** Under 2 = lap infant (about 10% of the fare plus taxes). 2–11 = own seat at child price. Rules to research and store in a new `data/child-awards.json`:
   - Flying Blue: whether child award discounts exist.
   - Iberia Avios: child pricing.
   - LATAM Pass, Smiles, Azul: whether child awards cost full miles.
   - TAP: child discount.
3. **Splitting tickets across programs.** Three seats often won't fit one program's balance or availability. The agent should consider splits (e.g. 2 on Flying Blue + 1 on Smiles, same flight) and show the total for the family. It should also flag the risk of separate bookings: no protection if one booking changes, and seats aren't kept together.
4. **Pooling and household accounts.** To verify:
   - Flying Blue Family (household pooling)
   - Iberia/Avios household rules
   - LATAM Pass and Smiles family features
   - Livelo/Esfera transfers to a third party's airline account (booking for a family member from the account holder's miles)
   - Whether each program lets you book awards for family members, and any fees.
5. **Hotels and stays.** Occupancy from the profile party on Trivago, Airbnb and Accor. Prefer family rooms or apartments. Mention kids-stay-free or breakfast policies when known. Accor status benefits usually apply only to the member's own room.
6. **Family comfort flags.**
   - Prefer shorter connections and fewer stops (e.g. nonstop to CDG/MAD/LIS over double connections).
   - Favour daytime long-haul when the price difference is small.
   - Note seat-selection costs to sit together (this matters on Iberia basic fares).
   - Note stroller and car-seat policies.

## Phase 1: data foundation

Every rule from the Research Integrity Protocol applies: a primary source URL and a confidence level for each row.

1. **`data/transfer-partners.json`**:
   - Add an `amex_nl_mr` section (verify: Flying Blue, Avios via BA, and others, with Dutch ratios, which differ from the US ones).
   - Add `livelo` and `esfera` sections (Smiles, LATAM Pass, Azul Fidelidade, TAP Miles&Go, Iberia, Accor, to verify), plus `rove`.
   - Store base ratio, minimum transfer and transfer time for each.
2. **Cost basis for bought points** (new `data/point-costs.json`):
   - The typical promo price per 1,000 Livelo/Esfera points (R$) and the typical bonificada %, giving an **effective cost per airline mile** (e.g. R$ 35/milheiro Livelo at +100% to Smiles = R$ 17.50 per 1,000 Smiles miles).
   - A redemption is judged against this cost, not against a published valuation.
3. **`data/points-valuations.json`**:
   - Add `latam_pass`, `smiles`, `azul_fidelidade`, `livelo`, `esfera` and `amex_nl_mr` from Brazilian sources (Passageiro de Primeira, Melhores Destinos, Pontos pra Voar), priced in R$/milheiro.
   - Add a `currency` field per entry.
   - Accor ALL is fixed at 2,000 points = €40. Store that and convert it to R$.
4. **FX helper** (`scripts/fx.py` or a section in a skill): EUR/USD → BRL from a keyless public source (ECB rates via frankfurter.app), cached daily.
5. **Avios family links** (Iberia ↔ BA ↔ Qatar ↔ Aer Lingus ↔ Vueling ↔ Finnair), with the combine rules.
6. **`data/sweet-spots.json`** gets a Europe ⇄ Northeast Brazil section, starting with the four AMS ⇄ FOR plays above.
7. **`data/my-profile.json`** (new, gitignored): AMS home, positioning airports, BRL display, status, CPF available, the AMS-FOR priority route.
8. Rename "TudoAzul" to "Azul Fidelidade" everywhere.

## Phase 2: rewrite CLAUDE.md (plus `scripts/sync-agent.sh`)

1. **Who you serve:** the profile above in five lines.
2. **Every price, cash or award, in R$.** Award value is shown as "R$ per milheiro" against the cost basis.
3. **Replace the US card list** (Chase/Amex US/Bilt/CapOne/Citi) with Amex NL MR, Livelo, Esfera and Rove.
4. **Before recommending a Livelo/Esfera move,** check the current promos for both buying points and bonificadas. Answer "buy + transfer now, or wait?"
5. **Brazil-route trigger:** any trip to Brazil runs the AMS ⇄ FOR-style multi-gateway check (CDG/MAD/LIS/GRU).
6. **Remove the Amex US portal/IAP/FHR/THC blocks.** Hotels default to Accor (status benefits), then cash in R$.
7. Add rail (NS/Eurostar/SNCF) for Europe trips under ~6 hours.
8. Stay under 40k characters.

## Phase 3: new skills

| Skill | What it covers | Priority |
|---|---|---|
| `ams-for` (or a `home-route` recipe) | A single command running the full AMS ⇄ FOR search matrix above and ranking the options in R$ | **1** |
| `brazil-programs` | Livelo/Esfera purchase promos, bonificadas, Clube plans, cost-basis math, when to buy | **1** |
| `bonificadas` + `scripts/refresh-bonificadas.py` | Current Brazilian purchase and transfer promos from a Brazilian source, refreshed weekly | **1** |
| `latam-pass` | LATAM award search (browser automation or manual workflow, since Seats.aero has no LATAM) and partner rules | **1** |
| `flying-blue` | Promo Rewards, dynamic pricing, AMS taxes, holds, Amex NL transfer | **2** |
| `avios` | Iberia off-peak, combining Avios across programs, reading Qatar results as a stand-in for Avios prices | **2** |
| `smiles`, `azul-fidelidade`, `tap-miles-go` | Partner charts, promo weeks, booking with a CPF | **3** |
| `europe-rail` | NS, Eurostar, SNCF, linked with `deutsche-bahn` | **3** |

## Phase 4: adapt existing skills

- `flight-search-strategy`, `ignav`, `compare-flights`: markets **NL then BR**, convert to R$, add positioning airports.
- `seats-aero`: Smiles and Azul become bookable programs. Note the gaps for LATAM Pass, Iberia and TAP.
- `points-valuations`, `trip-calculator`: support R$/milheiro and the purchase-cost basis.
- `compare-hotels`, `hotel-chains`: Accor-first (status benefits), Trivago set to NL country with BRL currency if supported (else EUR → BRL).
- `transfer-bonuses`: point to `bonificadas`, plus Amex NL bonuses if a source exists.
- `status-match`: the profile status as the starting point for hotel matches.
- `award-holds`, `stopovers`, `booking-guidance`: LATAM Pass, Smiles, Azul, TAP, Iberia.
- `lessons-learned`: Brazil caveats.
- `my-points`: add Amex NL MR, and let a bought-points entry carry an average cost per milheiro.

## Phase 5: archive

Move to `skills/_archive/` (not loaded): `awardwallet`, `american-airlines`, `amex-travel` (US portal), `premium-hotels`, `bilt`, `sutochno`, `vrbo`, `tripadvisor`. Move `data/fhr-properties.json`, `thc-properties.json` and `chase-edit-properties.json` to `data/_archive/`.

Update `scripts/skill-meta.tsv`, the README tables (`scripts/gen-skill-tables.sh`), `llms.txt` and `scripts/smoke-test.sh` so they skip `_archive`.

## Phase 6: verify

- `bash scripts/smoke-test.sh` (full run).
- Test prompts:
  1. "AMS → FOR in July, 1 adult, economy and business options." Covers all gateways, priced in R$.
  2. "Livelo has 100% to LATAM Pass and points at R$ 36. Should I buy?"
  3. "Weekend in Lisbon." Covers rail vs. flight, Accor, R$.

## Order

1. **PR 1:** Phase 1 data (transfer map, cost basis, valuations, FX, profile) plus `my-points` with Amex NL.
2. **PR 2:** Phase 2 CLAUDE.md, plus the `ams-for`, `brazil-programs`, `bonificadas` and `latam-pass` skills.
3. **PR 3:** `flying-blue`, `avios`, and the Phase 4 changes.
4. **PR 4:** Phase 5 archive, the remaining skills, and Phase 6 verification.

Family items fit into PR 1 (`child-awards.json` and the party defaults in `my-profile.json`) and PR 2 (3-seat filtering in the AMS-FOR recipe and Seats.aero).

## Still needed from you

- Your **Amex NL MR balance**.

- **Your Amex NL MR balance,** so it can go into `data/my-balances.json`.
- **The average price you paid per 1,000 Livelo/Esfera points,** if you know it. Otherwise we assume the typical promo price.
