---
name: my-points
description: Read the user's points, miles, and elite status from their own balance source (local data/my-balances.json now, their own web app later). Use whenever a trip, award search, transfer, or hotel decision needs the user's inventory. Replaces AwardWallet.
category: loyalty
summary: User's own points/miles balances and status (local file or own web app).
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
    { "program": "Chase Ultimate Rewards", "kind": "bank", "balance": 145000 },
    { "program": "United MileagePlus", "kind": "airline", "balance": 16000, "status": "Silver", "expires": "2027-03-01" } ] }
```

`kind` is `bank` (transferable currency), `airline`, or `hotel`. `data/my-balances.example.json` is the template.

## Rules

1. If neither source exists, ask the user once for their balances and offer to save them to `data/my-balances.json`. Do not call AwardWallet.
2. Check `updated`. The user wants a monthly refresh: if older than 30 days, ask for updated balances at the start of the response (a one-line reminder with the program list), then continue the task using the old numbers marked as possibly stale. Never recommend a transfer on stale data without confirming.
3. Compute effective balance per program: direct balance plus transferable bank balances via `data/transfer-partners.json` (adjust for ratio).
4. Flag any `expires` within 6 months and any status up for renewal.
5. Never print balances into logs or external requests.
