#!/usr/bin/env python3
"""Price a LATAM Pass Tabela Fixa (partner award) itinerary.

Reads data/latam-tabela-fixa.json (the official LATAM chart, current and
previous tables). Pricing rule from LATAM: one charge per distinct
origin-region > destination-region combination, regardless of how many
connections fall inside that combination.

Usage:
    # Path of stops: each stop is a region, a country (PT, as in LATAM's
    # region table) or an alias like EU, US, ME (see ALIASES).
    python3 scripts/latam_tabela_fixa.py Holanda Qatar --cabin business
    python3 scripts/latam_tabela_fixa.py Brasil "Estados Unidos" "Estados Unidos" --cabin economy
    python3 scripts/latam_tabela_fixa.py EU ME --cabin business --pax 3 --cost 22
    python3 scripts/latam_tabela_fixa.py --row Europa --cabin business   # one origin, every destination
    python3 scripts/latam_tabela_fixa.py --diff                          # what changed on 2026-11-23
    python3 scripts/latam_tabela_fixa.py --region Turquia                # which region is a country in

Options:
    --cabin   economy | premium_economy | business | first (default economy)
    --pax     passengers paying miles (infants under 2 are NOT allowed on tabela fixa)
    --cost    R$ per milheiro paid for the LATAM miles (from data/my-balances.json)
    --cash    family cash fare in R$, to compute R$ per milheiro achieved
    --taxes   award taxes in R$ for the whole party (read at quote time)
    --table   current | previous (default current)
    --json    machine-readable output
"""

import argparse
import json
import sys
import unicodedata
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "latam-tabela-fixa.json"

ALIASES = {
    "br": "Brasil", "brazil": "Brasil",
    "ar": "Argentina",
    "sa": "América do Sul", "south america": "América do Sul", "america do sul": "América do Sul",
    "ca": "América Central", "caribe": "América Central", "caribbean": "América Central",
    "central america": "América Central",
    "na": "América do Norte", "us": "América do Norte", "usa": "América do Norte",
    "eua": "América do Norte", "north america": "América do Norte",
    "eu": "Europa", "europe": "Europa",
    "oc": "Oceania",
    "me": "Oriente Médio", "middle east": "Oriente Médio",
    "af": "África", "africa": "África", "africa norte": "África", "africa sul": "África",
    "ea": "Ásia Oriental", "east asia": "Ásia Oriental",
    "wa": "Ásia Ocidental", "west asia": "Ásia Ocidental",
    # English country names that come up most for this user
    "netherlands": "Europa", "holanda": "Europa", "portugal": "Europa", "spain": "Europa",
    "uk": "Europa", "germany": "Europa", "france": "Europa", "turkey": "Oriente Médio",
    "qatar": "Oriente Médio", "uae": "Oriente Médio", "dubai": "Oriente Médio",
    "japan": "Ásia Oriental", "india": "Ásia Ocidental", "mexico": "América do Norte",
    "australia": "Oceania", "morocco": "África", "south africa": "África",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(s.lower().replace("-", " ").split())


def load():
    return json.loads(DATA.read_text())


def resolver(data):
    table = {}
    for region, countries in data["region_countries"].items():
        if region.startswith("_"):
            continue
        table[norm(region)] = region
        for c in countries:
            table[norm(c)] = region
    table[norm("Argentina")] = "Argentina"  # own row in the economy chart
    for k, v in ALIASES.items():
        table.setdefault(norm(k), v)
    return table


def resolve(token, table):
    r = table.get(norm(token))
    if not r:
        sys.exit(f"Unknown region or country: {token!r}. Try --region <name> or a region name like Europa.")
    return r


def regions_for(data, cabin):
    return data["economy_regions"] if cabin == "economy" else data["regions"]


def price(data, cabin, table_name, a, b):
    regs = regions_for(data, cabin)
    if cabin != "economy":
        a = "América do Sul" if a == "Argentina" else a
        b = "América do Sul" if b == "Argentina" else b
    m = data["chart"][cabin][table_name]
    return m[regs.index(a)][regs.index(b)]


def brl(x):
    return "R$ " + f"{x:,.0f}".replace(",", ".")


def miles(x):
    return f"{x:,}".replace(",", ".")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("stops", nargs="*")
    p.add_argument("--cabin", default="economy", choices=["economy", "premium_economy", "business", "first"])
    p.add_argument("--table", default="current", choices=["current", "previous"])
    p.add_argument("--pax", type=int, default=1)
    p.add_argument("--cost", type=float, help="R$ per milheiro paid")
    p.add_argument("--cash", type=float, help="cash fare in R$ for the whole party")
    p.add_argument("--taxes", type=float, default=0.0, help="award taxes in R$ for the whole party")
    p.add_argument("--row", help="print one origin region against every destination")
    p.add_argument("--diff", action="store_true", help="list pairs that changed between previous and current")
    p.add_argument("--region", help="look up which region a country is in")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    data = load()
    table = resolver(data)

    if a.region:
        print(f"{a.region} -> {resolve(a.region, table)}")
        return

    if a.diff:
        out = []
        for cabin, t in data["chart"].items():
            regs = regions_for(data, cabin)
            for i, r1 in enumerate(regs):
                for j, r2 in enumerate(regs):
                    old, new = t["previous"][i][j], t["current"][i][j]
                    if old != new:
                        out.append({"cabin": cabin, "from": r1, "to": r2, "previous": old, "current": new,
                                    "change_pct": round((new / old - 1) * 100, 1) if old else None})
        if a.json:
            print(json.dumps(out, ensure_ascii=False, indent=1))
        else:
            for d in out:
                print(f"{d['cabin']:16} {d['from']:>17} > {d['to']:<17} {miles(d['previous']):>8} -> {miles(d['current']):>8}  ({d['change_pct']:+}%)")
            print(f"{len(out)} pairs changed. Valid from {data['_meta']['current_valid_from']}.")
        return

    if a.row:
        origin = resolve(a.row, table)
        regs = regions_for(data, a.cabin)
        rows = [{"to": r, "current": price(data, a.cabin, "current", origin, r),
                 "previous": price(data, a.cabin, "previous", origin, r)} for r in regs]
        if a.json:
            print(json.dumps({"from": origin, "cabin": a.cabin, "rows": rows}, ensure_ascii=False, indent=1))
        else:
            print(f"{a.cabin} from {origin} (one way, per passenger)")
            for r in rows:
                flag = "" if r["current"] == r["previous"] else f"  (was {miles(r['previous'])})"
                print(f"  > {r['to']:<17} {miles(r['current']):>8}{flag}")
        return

    if len(a.stops) < 2:
        p.error("give at least an origin and a destination, or use --row / --diff / --region")

    path = [resolve(s, table) for s in a.stops]
    seen, legs = set(), []
    for x, y in zip(path, path[1:]):
        key = (x, y)
        if key in seen:
            continue  # same combination charged once
        seen.add(key)
        legs.append({"from": x, "to": y, "miles": price(data, a.cabin, a.table, x, y)})

    per_pax = sum(l["miles"] for l in legs)
    total = per_pax * a.pax
    result = {"cabin": a.cabin, "table": a.table, "path": path, "legs": legs,
              "miles_per_pax": per_pax, "pax": a.pax, "miles_total": total}
    if a.cost:
        result["miles_cost_brl"] = round(total / 1000 * a.cost, 2)
    if a.cash:
        result["brl_per_milheiro_achieved"] = round((a.cash - a.taxes) / total * 1000, 2)
    if 0 in [l["miles"] for l in legs]:
        result["warning"] = "A Brasil>Brasil leg is 0 in the chart: domestic Brazil partner flights are not priced from this table."

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return
    print(f"Tabela fixa, {a.cabin}, {a.table} table ({data['_meta']['current_valid_from'] if a.table == 'current' else 'until ' + data['_meta']['previous_valid_until']})")
    for l in legs:
        print(f"  {l['from']} > {l['to']}: {miles(l['miles'])}")
    print(f"  Per passenger: {miles(per_pax)}   x{a.pax} = {miles(total)} miles")
    if "miles_cost_brl" in result:
        print(f"  Miles cost at {brl(a.cost)}/milheiro: {brl(result['miles_cost_brl'])}")
    if "brl_per_milheiro_achieved" in result:
        print(f"  Value vs cash {brl(a.cash)} minus taxes {brl(a.taxes)}: {brl(result['brl_per_milheiro_achieved'])}/milheiro")
    if "warning" in result:
        print("  WARNING: " + result["warning"])


if __name__ == "__main__":
    main()
