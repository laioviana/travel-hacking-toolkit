---
name: bonificadas
description: Current Brazilian transfer bonuses (transferências bonificadas) and point or mile purchase promos for Livelo, Esfera, Smiles, LATAM Pass, Azul Fidelidade, TAP, Iberia, Qatar and Accor. Refreshed from Brazilian points blogs. Use before any Livelo or Esfera transfer, when asked whether to buy points or miles now, or when pricing an award that needs miles moved into Smiles, LATAM Pass or Azul.
category: loyalty
summary: Current Brazilian transfer bonuses and point purchase promos. Refreshed from Brazilian points blogs.
api_key: None (public feeds)
---

# Bonificadas

Brazilian transferable points are almost never worth moving at the base ratio. Bonuses of 60–133% into Smiles, LATAM Pass and Azul run every few weeks, and the programs also sell points and miles at a discount. This skill tells the agent what's running now.

Data: `data/bonificadas.json`, produced by `scripts/refresh-bonificadas.py`.
- **Sources:** the RSS feeds of Pontos pra Voar and Passageiro de Primeira.
- **Refresh:** weekly through `.github/workflows/refresh-data.yml`, and on demand.

## The freshness gate (every time, before citing a promo)

Promos often last 1–3 days, so a weekly snapshot is not enough.

1. **Refresh first, always.** The script takes a few seconds:
   ```bash
   python3 scripts/refresh-bonificadas.py
   ```
   If it fails (offline or feed changed), use the existing file and say how old `_meta.last_updated` is.
2. **Drop expired entries.** That's any entry with `status: "expired"`, or an `end_date_inclusive` before today.
3. **`status: "check_post"`** means the headline didn't say when it ends. Open one of the `urls` before telling the user it is still on. Never invent an end date.
4. **`pct_is_max: true`** means "até X%". The top tier usually needs a club subscription (Clube Livelo, Clube Esfera, Clube Smiles, Clube Azul) or a minimum amount. Read the post for the tier this user qualifies for. This user has no club subscriptions unless `data/my-profile.json` says otherwise.
5. **`confidence`.**
   - `LIKELY`: both blogs reported the same promo.
   - `UNVERIFIED`: only one blog did.

   Either way, the user must confirm on the program's own site before moving points.

## Fields

| Field | Meaning |
|---|---|
| `kind` | `transfer_bonus` or `purchase_promo` |
| `pct` | Bonus % (transfers) or discount/bonus % (purchases), as the headline states |
| `to_program` | Destination key, matching `data/transfer-partners.json` (`latam_pass`, `smiles`, `azul`, `qatar`, `accor`, …) |
| `from` | Origins named in the headline (`livelo`, `esfera`, `itau`, `c6`, `nomad`, …) |
| `includes_livelo` / `includes_esfera` | Whether the user's two bank currencies are part of it. "Exceto Esfera" sets `includes_esfera: false`. |
| `end_date_inclusive` | Only when the headline says "acaba hoje", "último dia", "até DD/MM", etc. |
| `urls`, `sources` | Every post that reported it |

Only promos with `includes_livelo` or `includes_esfera`, or a `purchase_promo` for a program the user holds, are relevant to this user. Card-specific promos (Itaú, C6, Nomad, Inter) are noise for them. Mention them at most in one line.

## The math

Effective cost per 1,000 airline miles (formula in `data/point-costs.json`):

```
effective = cost_per_milheiro_brl / (base_ratio × (1 + bonus_pct/100))
```

Use the user's own `avg_cost_per_milheiro_brl` from `data/my-balances.json` for points already held. For a new purchase, use the promo price from the post.

**Example:** Livelo bought at R$ 26.00, moved to Azul at 1:1 with +100% (the non-club tier) costs `26.00 / (1 × 2.0)` = **R$ 13.00 per 1,000 Azul points**.

Then compare against:
- **the redemption value** of the award being considered: `(cash fare R$ − award taxes R$) / miles × 1000`
- **the program's floor** in `brl_milheiro` (`data/points-valuations.json`)

## Decision rules

1. **No concrete redemption, no transfer.** Miles in Smiles, LATAM Pass and Azul are exposed to devaluation (for example, LATAM's partner table +20% from 2026-11-23). Points sitting in Livelo or Esfera keep their options open.
2. **Never transfer at the base ratio** unless a specific award would disappear before the next bonus. Big bonuses recur within weeks.
3. **Mind the timing.** Livelo can take up to 7 business days to credit. Award space can vanish in that time. Check `data/family-booking.json` before moving points for a 3-seat booking.
4. **Purchase promos are only good below the user's cost basis.** For example, a LATAM Pass purchase only makes sense if the effective R$/milheiro is below the user's current LATAM average (`avg_cost_per_milheiro_brl`) and they have a use for the miles.
5. **Check the expiry rules** of the destination program before topping it up.

## Output

Show a short table, filtered to promos relevant to the user, with these columns:
- Promo
- Bonus
- Ends
- Effective R$/milheiro, at the user's cost basis
- Confidence
- Link

Add one line on whether to act now or wait.
