---
name: hotel-chains
description: Maps hotel brand names (Westin, Sheraton, Holiday Inn, etc.) to chain families and loyalty programs. Use when hotel results contain branded properties or deciding whether to check award rates.
category: reference
summary: Maps brand names (Westin, Holiday Inn, etc.) to chain families and loyalty programs.
---

# Hotel Chain Recognition

**Reference data:** `data/hotel-chains.json`

Use the `quick_lookup` section in the data file to instantly identify which loyalty program a hotel belongs to when it appears in search results. When you see "Westin" you need to know that's Marriott Bonvoy. When you see "The Standard" you need to know that's Hyatt.

## The Trigger Table

When results contain properties from ANY of these chains, IMMEDIATELY pull balances with the `my-points` skill and check award rates. No judgment call. No asking. Just do it.

| Chain Family | Properties Include | Loyalty Program |
|---|---|---|
| IHG | Holiday Inn, InterContinental, Crowne Plaza, Kimpton, Staybridge, Candlewood | IHG One Rewards |
| Marriott | Marriott, Sheraton, Westin, W, Ritz-Carlton, St. Regis, Courtyard, Aloft | Marriott Bonvoy |
| Hilton | Hilton, DoubleTree, Hampton, Embassy Suites, Waldorf Astoria, Conrad, Curio | Hilton Honors |
| Hyatt | Hyatt, Grand Hyatt, Park Hyatt, Andaz, Thompson, Alila, Hyatt Place | World of Hyatt |
| Accor | Sofitel, Novotel, Pullman, Fairmont, Raffles, Swissôtel, ibis, Mercure | Accor Live Limitless |
| Radisson | Radisson, Radisson Blu, Park Inn, Country Inn | Radisson Rewards |
| Wyndham | Wyndham, Ramada, Days Inn, Super 8, La Quinta, Tryp | Wyndham Rewards |
| Best Western | Best Western, Best Western Plus, Best Western Premier, SureStay | Best Western Rewards |

## Always Compare Points vs Cash for Hotels

- Hyatt points: 1.4cpp VFTW floor / 1.5cpp UP/OMAAT median / 1.7cpp TPG ceiling. Often a great redemption.
- Hilton at 0.4cpp floor (almost always better to pay cash).
- Marriott at 0.6-0.7cpp.
- IHG at 0.5cpp across all sources. Almost always better to pay cash.

Mention transfer opportunities. "Your Chase UR transfers 1:1 to Hyatt. That 25K/night Category 5 hotel is worth $375 in cash. That's 1.5cpp, between the 1.4 conservative floor and 1.7 ceiling. Decent but not exceptional."

## Booking Windows for Hotels

Reference `data/sweet-spots.json` `booking_windows` section if a user wants to know how far in advance to book.

## This User: Accor First

- Programs that matter for this user: **ALL Accor** (reachable from Livelo at 3.5:1 in blocks of 2,000 and from Esfera at 3.5:1, see `data/transfer-partners.json`), then cash. Hilton and IHG via Livelo or Esfera are available at poor ratios and are rarely worth it.
- Pull the Accor status from the profile with `my-points` and state the benefits on every Accor property.
- ALL points are fixed value: 2,000 points = EUR 40. Convert to R$ with `python3 scripts/fx.py`.
- Ignore US-only paths in the table above (Chase, US Amex, Bilt, Capital One transfers).
