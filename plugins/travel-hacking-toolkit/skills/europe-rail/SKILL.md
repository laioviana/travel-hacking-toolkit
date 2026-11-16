---
name: europe-rail
description: European rail from Amsterdam for trips under about six hours. NS domestic, NS International and Eurostar to Brussels, Paris and London, SNCF, with child fares, and links to the deutsche-bahn skill for Germany. Use for any weekend or short trip from the Netherlands where train may beat flying, and for positioning to BRU, DUS or CGN.
category: destinations
summary: Rail from Amsterdam under six hours. NS, Eurostar, SNCF, child fares, links to deutsche-bahn.
api_key: None
---

# Europe Rail

From Amsterdam, rail often beats flying with a toddler for trips under about six hours door to door. Compare it with `compare-flights` and say which wins in R$ and in hours. Convert fares with `python3 scripts/fx.py`.

Every fact has a source and confidence. There is no keyless API for NS or SNCF in this toolkit, so searches use the operator sites and web search. For Germany and neighbours use the `deutsche-bahn` skill (db-vendo-client), which also returns Amsterdam to Cologne, Düsseldorf and Brussels connections.

## Amsterdam routes

| Route | Facts | Source | Confidence |
|---|---|---|---|
| Amsterdam to Paris (Eurostar) | Page shows 3.25 (read as 3 h 25 min, unit not stated), no change, via Schiphol and Rotterdam, 10 trains a day. Standard fares from EUR 35 to EUR 149. | [NS International](https://www.nsinternational.com/en/travel-with-thalys/route-thalys-1) | LIKELY |
| Amsterdam to Brussels (Eurostar) | Page shows 1.56 (read as 1 h 56 min, unit not stated), 14 trains a day. | same | LIKELY |
| Amsterdam to London | Eurostar, with a change or the direct service where operated. Check live. Bookable 6 to 8 months ahead. | [Eurostar via search summary](https://www.eurostar.com/travel-info/travel-planning/travel-with-children) | UNVERIFIED |
| Amsterdam to Cologne or Düsseldorf | Use `deutsche-bahn`. | skill | n/a |

Booking: NS International sells the tickets online or at its desks, booking online avoids fees, window is 360 days ahead for Paris and Brussels. Luggage: 2 pieces up to 75 x 53 x 30 cm plus 1 hand piece. Source: NS International page above. Confidence: LIKELY.

## Children

Eurostar pages state children under 4 travel free without their own ticket, sitting on an adult's lap, a seat needs a child ticket, ages 4 to 11 get roughly 50% off Standard and Plus (not Premier), and ID is needed at any age. Source: [Eurostar, travel with children](https://www.eurostar.com/travel-info/travel-planning/travel-with-children). Confidence: LIKELY (reported from the official pages by a search summary, the page itself blocked direct fetch). Check how many lap infants per adult are allowed before booking, UNVERIFIED.

Work out the child's age on the travel date from the profile before pricing.

## Domestic NL and SNCF

- NS domestic (Schiphol to Amsterdam Centraal, Eindhoven, Rotterdam) fares and child rules: not researched. UNVERIFIED. Use ns.nl live.
- SNCF Paris to onward France and Paris to Lisbon-type connections: not researched. UNVERIFIED.

## When rail wins

- Brussels (BRU) and Paris: usually yes, compare the Eurostar fare with a cash flight plus airport transfer times.
- Positioning to BRU or DUS for a long-haul award (see `ams-for`): price the train in R$ and add it to the award total.
- London, Cologne: check both, then decide on door to door time and with a toddler prefer the train when fares are close.
