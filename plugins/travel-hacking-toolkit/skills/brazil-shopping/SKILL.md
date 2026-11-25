---
name: brazil-shopping
description: Cashback and points or miles on a purchase from a Brazilian online store (Magazine Luiza, Netshoes, Americanas, Casas Bahia, Mercado Livre, KaBuM, Decolar, Booking.com in R$, LATAM, Localiza and thousands more). Reads Comparemania (comparemania.com.br), which lists every cashback site (Méliuz, Cuponomia, PicPay, Inter, My Cashback, Dotz) and every points program (Esfera, Livelo, Smiles, Azul, LATAM Pass, TAP) for each store, values each offer in R$ against the user's cost basis, and names the best one. Use whenever the user wants to buy from a Brazilian site or pay in R$, or says compra, loja, cashback, pontos por real, compre e pontue, Shopping Livelo, Shopping Smiles, Méliuz or Comparemania.
category: loyalty
summary: Cashback and points per R$ for any Brazilian online store via Comparemania, valued at your cost basis.
api_key: None (public site)
---

# Brazil Shopping

Every Brazilian store has a long list of ways to earn on a purchase: about ten cashback sites and five or six points programs, with rates that change daily. Comparemania gathers them on one page per store. This skill reads that page, turns each offer into R$ back, and picks one.

- **Script:** `scripts/comparemania.py` (plain HTTP; Comparemania allows it)
- **Data:** `data/shopping-portals.json`, keys `comparemania`, `brazil_cashback_sites` and `valuation`
- **Shops outside Brazil:** use the `shopping-portals` skill instead (Flying Blue, Avios, Revolut, CashbackXL, Woolsocks)

## Why points often win here

Brazilian programs pay many points per R$ during promos: Azul at 18 points per R$ 1, or Livelo at 6. Points are worth R$ 13–29 per 1,000, so 6 Livelo points per R$ is roughly a 15% return. That often beats the best cashback site. Value the points at the user's cost basis, never above it.

## Workflow

1. **Pin down the store and amount** in R$, before shipping.
   - If the user named a product, find the cheapest store first. Cashback never justifies a higher price.
   - Remember the user lives in the Netherlands. A Brazilian store only fits when delivery is in Brazil (family, a coming trip), or for something digital or travel-related (Booking.com, Decolar, LATAM, Localiza, gift cards).
2. **Pull balances and cost basis with `my-points`.** The script reads `data/my-balances.json` itself.
   - Also read `br_accounts` from `data/my-profile.json` (for example `["inter", "picpay"]`). Bank-linked cashback sites only pay through that bank's app.
   - If `br_accounts` is missing, assume none and say so in one line.
3. **Run the script:**
   ```bash
   python3 scripts/comparemania.py "magazine luiza" --amount 3500 --giftcards
   ```
   - Not sure of the store's name? `--search <text>` lists the matching pages.
   - `--top` lists the stores whose rates jumped most versus usual today. Useful when the user is flexible about where to buy.
   - Add `--json` when you need to post-process the results.
4. **Check the points units.**
   - `pt/R$`, `pt/U$` and `pt/€` are explicit.
   - `pt(s)` shows no currency. The script assumes per R$ and marks the row "(unit assumed R$)".
   - If such a row comes out on top, open the program's own partner page for that store to confirm the unit before recommending it.
   - Use a browser for the program pages, since Livelo and LATAM block plain fetches.
5. **Filter by what the user can actually use.**
   - Cashback sites listed under `brazil_cashback_sites.needs_brazilian_account` count only if that account is in `br_accounts`.
   - Standalone sites (Méliuz, Cuponomia, My Cashback) only need a free account with a CPF. Payouts go by Pix to a Brazilian account.
   - Points programs need an account in that program. The user holds Livelo, Esfera, LATAM Pass, Smiles and Azul (see balances).
6. **Check for stacking.**
   - **Transfer bonus.** Run `bonificadas`. Livelo or Esfera points earned today can later move to Smiles, LATAM Pass or Azul with a bonus. That doesn't change today's value (valued at cost basis), but mention it if a bonus is running.
   - **Gift cards.** Buying a store gift card through a cashback site, then paying with it, sometimes still earns points at the store. It often doesn't, though. Only claim a stack if the gift card seller's or program's terms allow it.
   - **Card.** The card the user pays with earns its own points on top. Amex NL charges a foreign transaction fee on R$ purchases, which can wipe out a small cashback. Check the profile's cards before recommending one.
7. **Recommend.**
   - **Table:** type, site or program, rate, R$ value, effective %, plus a note on whether the user can use it.
   - **Then one opinionated line,** for example: "Go through Livelo (6 points per R$ = 21,000 points, worth R$ 532, 15%). Méliuz pays 10% (R$ 350) but needs a Pix payout to a Brazilian account."
   - **Tie-break between two close offers:**
     - Prefer the program whose points the user needs for a concrete award.
     - Then prefer cash, which never devalues.

## Tracking rules

The click-through happens on the cashback site or points program, not on Comparemania. Never fetch `/redirecionar/oferta/` links; robots.txt disallows them. Before checkout:

- Log in to the program, then click through to the store and finish in one session.
- Turn off ad blockers.
- Don't use coupons from other sites.

Points usually post within 30–60 days. Livelo and Esfera show a "pontos a receber" entry first.

## Keeping it working

- **If parsing returns nothing,** the page layout changed. The script parses `<tr>` rows with two cells. Fix `parse_offers` in `scripts/comparemania.py`, and bump `_meta.last_updated` in the data file.
- **Never write personal data** (accounts, balances, purchases) into tracked files.
