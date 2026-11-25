#!/usr/bin/env python3
"""Compare shopping-portal offers for one purchase, in R$ and effective %.

Each offer is PORTAL=RATE, where PORTAL is a key in data/shopping-portals.json
and RATE is read in that portal's unit:

  miles_per_10_eur   flying_blue_shop=9        (9 miles per EUR 10)
  avios_per_gbp      avios_uk=8                (8 Avios per GBP 1)
  avios_per_eur      iberia_club_store=5       (5 Avios per EUR 1)
  revpoints_per_eur  revolut=0.5               (RevPoints per EUR 1)
  rove_per_usd       rove=5                    (Rove Miles per USD 1)
  points_per_brl     esfera=6                  (points per R$ 1)
  percent            cashbackxl=2.25           (2.25% cash back)

A fixed reward is RATE "fixed:N", e.g. avios_uk=fixed:3600.

The purchase amount is converted into each portal's currency with fx.py.
Points are valued with data/shopping-portals.json "valuation", overridden by
the user's avg_cost_per_milheiro_brl from data/my-balances.json when present.

Usage:
  python3 scripts/shopping_value.py --amount 300 --currency EUR \
      flying_blue_shop=9 cashbackxl=2.25 woolsocks=4
  python3 scripts/shopping_value.py --amount 300 --currency EUR --json ...
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = json.loads((REPO / "data" / "shopping-portals.json").read_text())
PORTALS = DATA["portals"]
VALUES = DATA["valuation"]["programs"]

UNIT_CCY = {
    "miles_per_10_eur": "EUR",
    "avios_per_eur": "EUR",
    "avios_per_gbp": "GBP",
    "revpoints_per_eur": "EUR",
    "rove_per_usd": "USD",
    "points_per_brl": "BRL",
}

_fx_cache: dict = {}


def to_brl_rate(ccy: str) -> float:
    ccy = ccy.upper()
    if ccy == "BRL":
        return 1.0
    if ccy not in _fx_cache:
        out = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "fx.py"), "--rate", ccy, "--json"],
            capture_output=True, text=True, check=True,
        ).stdout
        data = json.loads(out)
        rate = data.get("rate") or data.get("BRL") or data.get("value")
        if rate is None:
            raise SystemExit(f"fx.py --json gave no rate for {ccy}: {out}")
        _fx_cache[ccy] = float(rate)
    return _fx_cache[ccy]


def cost_basis_overrides() -> dict:
    """program display name -> avg_cost_per_milheiro_brl, from the private balances file."""
    path = REPO / "data" / "my-balances.json"
    if not path.exists():
        return {}
    try:
        rows = json.loads(path.read_text()).get("balances", [])
    except (json.JSONDecodeError, AttributeError):
        return {}
    return {
        r["program"].lower(): float(r["avg_cost_per_milheiro_brl"])
        for r in rows
        if r.get("program") and r.get("avg_cost_per_milheiro_brl")
    }


def milheiro_value(program: str, overrides: dict) -> tuple[float, str]:
    v = VALUES[program]
    bp = (v.get("balance_program") or "").lower()
    if bp and bp in overrides:
        return overrides[bp], ("--value" if bp.startswith("__cli__") else "your cost basis")
    return float(v["brl_milheiro"]), "default"


def evaluate(key: str, rate_s: str, amount: float, ccy: str, overrides: dict) -> dict:
    if key not in PORTALS:
        raise SystemExit(f"unknown portal '{key}'. Known: {', '.join(PORTALS)}")
    p = PORTALS[key]
    unit, earns = p["unit"], p["earns"]
    amount_brl = amount * to_brl_rate(ccy)

    if earns == "cash":
        if rate_s.startswith("fixed:"):
            reward_brl = float(rate_s[6:]) * to_brl_rate(p.get("currency", ccy))
            reward = f"{p.get('currency', '')} {float(rate_s[6:]):.2f}"
        else:
            reward_brl = amount_brl * float(rate_s) / 100
            reward = f"{float(rate_s):g}% cash"
        basis = "cash"
    else:
        if rate_s.startswith("fixed:"):
            units = float(rate_s[6:])
        else:
            pccy = UNIT_CCY[unit]
            amount_in_pccy = amount_brl / to_brl_rate(pccy)
            per = float(rate_s) / (10 if unit == "miles_per_10_eur" else 1)
            units = amount_in_pccy * per
        mv, basis = milheiro_value(earns, overrides)
        reward_brl = units / 1000 * mv
        reward = f"{units:,.0f} {earns} @ R$ {mv:.2f}/milheiro"

    return {
        "portal": p["name"],
        "key": key,
        "reward": reward,
        "value_brl": round(reward_brl, 2),
        "effective_pct": round(reward_brl / amount_brl * 100, 2) if amount_brl else 0.0,
        "valued_at": basis,
        "confidence": p.get("confidence", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--amount", type=float, required=True, help="purchase amount, excluding shipping")
    ap.add_argument("--currency", default="EUR", help="currency of the amount (default EUR)")
    ap.add_argument("--value", action="append", default=[], metavar="PROGRAM=BRL",
                    help="override R$ per milheiro for a program, e.g. flying_blue=38 (repeatable)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("offers", nargs="+", help="PORTAL=RATE")
    a = ap.parse_args()

    overrides = cost_basis_overrides()
    for v in a.value:
        prog, _, brl = v.partition("=")
        if prog not in VALUES or not brl:
            raise SystemExit(f"--value must be PROGRAM=BRL with PROGRAM in: {', '.join(VALUES)}")
        VALUES[prog] = {"brl_milheiro": float(brl), "balance_program": f"__cli__{prog}"}
        overrides[f"__cli__{prog}"] = float(brl)
    rows = []
    for o in a.offers:
        if "=" not in o:
            raise SystemExit(f"offer must be PORTAL=RATE, got '{o}'")
        k, r = o.split("=", 1)
        rows.append(evaluate(k.strip(), r.strip(), a.amount, a.currency, overrides))
    rows.sort(key=lambda r: r["value_brl"], reverse=True)

    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    total_brl = a.amount * to_brl_rate(a.currency)
    print(f"Purchase: {a.currency.upper()} {a.amount:,.2f} = R$ {total_brl:,.2f}\n")
    print("| # | Portal | Reward | Value (R$) | Effective % | Valued at |")
    print("|---|---|---|---|---|---|")
    for i, r in enumerate(rows, 1):
        print(f"| {i} | {r['portal']} | {r['reward']} | {r['value_brl']:,.2f} | {r['effective_pct']:.2f}% | {r['valued_at']} |")


if __name__ == "__main__":
    main()
