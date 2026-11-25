---
name: shopping-portals
description: Earn miles, points or cashback on an online purchase. Before the user buys something (a laptop, clothes, a Booking.com or Hotels.com stay, groceries, AliExpress), check the shopping portals they can use from the Netherlands (Flying Blue Shop & Earn, Avios eStore UK, Iberia Club Store, Revolut RevPoints and Shops, CashbackXL, Woolsocks, Rove, and Brazilian portals Esfera, Livelo, Méliuz for R$ purchases), compare the live rates in R$ and effective percent, and say which portal and which card to use. Use whenever the user says they want to buy, order or book something online, or mentions shopping portal, cashback, eStore, earnonline, Woolsocks, CashbackXL, TopCashback or RevPoints.
category: loyalty
summary: Compare shopping portals and cashback (Flying Blue, Avios eStore, Revolut, CashbackXL, Woolsocks) for a purchase in R$.
api_key: None (browser for live rates)
---

# Shopping Portals

Pick the best portal and card for one online purchase. Every option is turned into one number, R$ back and effective %, so miles and cash compare directly.

- **Data:** `data/shopping-portals.json` (portals, URL patterns, tracking rules, default point values)
- **Calculator:** `scripts/shopping_value.py`

## The short version

- **Cash usually beats miles.** A shopping mile is worth what it costs to get one another way, about R$ 45 per 1,000 for Flying Blue or Avios via Livelo with a bonus. At that value, Flying Blue at 9 miles per €10 is a 0.6% return, while CashbackXL at 2.25% is almost four times as much.
- **Miles win during events.** Black Friday triples the Avios eStore rates, and Esfera sometimes pays 6 points per R$ 1 (about 17%).
- **Miles also win on travel bookings.** Booking.com, Hotels.com and Agoda pay 8–10 Avios per £1, or up to 44 Flying Blue miles per €10.

## Workflow

1. **Pin down the purchase.**
   - Retailer, amount before shipping, and the shop's country (bol.com NL, Amazon.de, Booking.com, a Brazilian store).
   - If the user only named a product, find where it's cheapest first, then apply the portal.
   - A portal never justifies a higher price.
2. **Pull balances and context with `my-points`.**
   - Cost bases override the default point values (the calculator does this itself).
   - Note which programs need activity to keep miles alive. A Flying Blue purchase counts as activity.
   - Read `revolut_plan` from `data/my-profile.json` if it's there. If it isn't, assume Standard and say so in one line.
3. **Look up the live rate on each relevant portal, in parallel.** Rates change weekly and during events, so the `sample_rates` in the data file are only a hint.
   - **Use a real browser.** avios.com, revolut.com, TopCashback, Livelo and LATAM block plain HTTP fetches with 403. Use the host's built-in browser tools when available, else `agent-browser`. Reject non-essential cookies.
   - **Which portals to check** depends on the shop:

     | Shop | Check these, in this order |
     |---|---|
     | Dutch or EU shop | `flying_blue_shop` (NL store, `/nl/az`), `cashbackxl` (`/webshops/<slug>`), `woolsocks` (`/nl-NL/cashback/<merchant>-cashback`), Revolut Shops (in-app only; ask the user to look if needed) |
     | UK shop, or a travel booking | `avios_uk`, plus the above |
     | Spanish shop | `iberia_club_store`. Enter through the Iberia page, since avios.com/es-ES redirects to the UK store from NL. |
     | US shop, or a Rove hotel booking | `rove` |
     | Brazilian store paid in R$ | `esfera`, `livelo`, `meliuz`, and the Smiles and LATAM Pass shopping portals. Run `bonificadas` too, because a points-per-R$ promo plus a transfer bonus can stack. |
     | Anything | `topcashback_uk` and `topcashback_us` are geo-blocked from NL. Skip them unless the data file says the block is gone. |

   - **Record each rate exactly as shown,** with "up to", "from" or "was" kept. "Up to" means only some categories earn the top rate. Read the retailer's terms for the category being bought.
4. **Run the calculator** with every rate found:
   ```bash
   python3 scripts/shopping_value.py --amount 450 --currency EUR \
       flying_blue_shop=22 cashbackxl=3 woolsocks=4 avios_uk=5 revolut=0.5
   ```
   - `revolut=` is RevPoints per €1. That's 1 ÷ the plan's € per point (Standard 0.1, Premium 0.25, Metal 0.5, Ultra 1), times the Shops multiplier for an in-app Shops purchase.
   - Fixed rewards use `PORTAL=fixed:N`.
5. **Stack the layers.** One portal per purchase, then add on top:
   - **The card.** Revolut card RevPoints, or Amex NL MR, stack with any portal. MR moves 2:1 to Flying Blue, so value it at about half a Flying Blue mile. Use whichever card earns more for this purchase, and check Amex Offers in the app.
   - **Gift cards.** A Woolsocks or CashbackXL gift card for the retailer gets instant cashback. Paying with it usually voids the airline portal's earning, though, so it's an alternative to the portal, not a stack. Compare the two.
   - **Revolut Shops** happens in-app and can't be combined with an external portal. Compare it as its own option.
6. **Recommend.**
   - **Table:** portal, live rate, reward, R$ value, effective %, tracking time.
   - **Then one opinionated line,** for example: "Use CashbackXL (R$ 89, 3%) and pay with the Revolut card (+R$ 7). Flying Blue's 22 miles per €10 is worth only 1.5% at your values. It's only worth taking if you need activity on the Flying Blue account."
   - **If a miles option is close to cash,** prefer cash unless the miles top up a balance for a concrete award, or keep an expiring balance alive.

## Tracking rules (say these when recommending an airline portal)

Getting the click-through wrong is the main reason miles never post. Before checkout:

- Log in to the portal, then click through to the shop. Finish the purchase in one session in the same browser.
- Accept cookies. Turn off ad blockers and tracking protection for that tab.
- Disable other cashback or coupon extensions.
- No voucher codes the portal didn't give you, and no refer-a-friend links.
- Keep the order confirmation.

Missing miles claims open after the pending window:

| Portal | Pending | Final |
|---|---|---|
| Flying Blue | 5 working days | about 90 days (travel: 90–120 days after the stay) |
| Avios | 5 days | 35 days |
| CashbackXL | hours | 1 week to 4 months |

## Valuations

`valuation.programs` in the data file holds a default R$ per milheiro for each program, with its derivation. Use the cheapest realistic replacement cost, not the best-case redemption value. Never value a shopping mile above the price the user could buy the same mile for.

When `bonificadas` shows a big Livelo bonus into Flying Blue or Avios, recompute the replacement cost (`cost_basis × ratio_denominator ÷ (1 + bonus)`) and pass it with `--value flying_blue=38`. Don't edit the data file with it, since that value comes from the user's private cost basis. Note it in the answer.

## Keeping the data fresh

- **On a successful lookup,** if a portal's facts changed (new URL pattern, a geo-block lifted, a new tier), update `data/shopping-portals.json` and bump `_meta.last_updated`.
- **Sample rates are dated.** Don't overwrite them on every lookup.
- **Never write personal details** (balances, plan, purchases) into this tracked file.
