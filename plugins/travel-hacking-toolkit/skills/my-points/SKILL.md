---
name: my-points
description: Read the user's points, miles, elite status, purchase cost basis and travel profile from their own balance source (local data/my-balances.json and data/my-profile.json now, their own web app later). Use whenever a trip, award search, transfer, or hotel decision needs the user's inventory. Covers Brazilian programs (Livelo, Esfera, LATAM Pass, Smiles, Azul), Amex NL Membership Rewards, Flying Blue, Iberia Avios and Accor. Replaces AwardWallet.
category: loyalty
summary: The user own points and miles balances, cost basis, status and travel profile (local files or own web app).
api_key: none
license: MIT
---

# My Points

The user does not use AwardWallet. Their balances come from one of two sources, checked in this order.

## Source 1: their web app (when exposed)

If `MY_POINTS_API_URL` is set, fetch it. Optional bearer token in `MY_POINTS_API_TOKEN`.

```bash
curl -s -H "Authorization: Bearer $MY_POINTS_API_TOKEN" "$MY_POINTS_API_URL"
```

The response must match the file schema below. If it errors, fall through to Source 2 and say so once.

## Source 2: local file

Read `data/my-balances.json` (gitignored, never commit). Schema:

```json
{ "updated": "YYYY-MM-DD",
  "balances": [
    { "program": "Livelo", "kind": "bank", "balance": 10000, "avg_cost_per_milheiro_brl": 26.00 },
    { "program": "Amex Membership Rewards (NL)", "kind": "bank", "balance": null },
    { "program": "LATAM Pass", "kind": "airline", "balance": 150000, "status": "", "expires": null, "avg_cost_per_milheiro_brl": 22.00 } ] }
```

- `kind` is `bank` (transferable currency), `airline`, or `hotel`. `data/my-balances.example.json` is the template.
- `balance: null` means unknown. Ask for it once, and don't count that currency in effective balances until it's known.
- `avg_cost_per_milheiro_brl` is optional: what the user paid on average per 1,000 points, in R$. Present for points bought in promotions (Livelo, Esfera) and miles the user knows the cost of (LATAM Pass, Iberia Avios).

## Travel profile

Read `data/my-profile.json` (gitignored, template `data/my-profile.example.json`) for:

- home airport, positioning airports and search markets
- display currency
- travelling party
- elite status
- priority routes (details in `data/home-routes.json`)

Default every search to the party in the profile. Work out each child's age on each travel date from their birth month.

## Rules

1. **No source.** If neither source exists, ask the user once for their balances and offer to save them to `data/my-balances.json`. Do not call AwardWallet.
2. **Stale balances.** Check `updated`. The user wants a monthly refresh: if it's older than 30 days, ask for updated balances at the start of the response (a one-line reminder with the program list). Then continue the task using the old numbers, marked as possibly stale. Never recommend a transfer on stale data without confirming.
3. **Effective balance.** For each program, compute the direct balance plus what the bank balances can transfer in, via `data/transfer-partners.json`, adjusted for ratio. The user's bank currencies are:
   - `amex_nl_mr`, Dutch ratios. Never use the US `amex_mr` section for this user.
   - `livelo`
   - `esfera`
   - `rove`

   For Avios, also route through `data/avios-family.json`: Livelo → Qatar → Iberia beats Livelo → Iberia, and Amex NL → BA → Iberia beats Amex NL → Iberia.
4. **Cost basis.** When `avg_cost_per_milheiro_brl` exists, it's the break-even line. Value a redemption as `(cash fare R$ - award taxes R$) / points × 1000`. Below the cost basis means the user loses money compared with what they paid for the points. Then compare against `brl_milheiro` in `data/points-valuations.json`.
5. **Bought currencies.** For points that went through a transfer bonus, the effective cost is `cost / (ratio × (1 + bonus))`. See `data/point-costs.json`.
6. **Show everything in BRL** (`display_currency`). Convert EUR/USD cash prices with `python3 scripts/fx.py <amount> <CUR>`.
7. **Expiry and status.** Flag any `expires` within 6 months and any status up for renewal.
8. **Privacy.** Never print balances into logs or external requests.
