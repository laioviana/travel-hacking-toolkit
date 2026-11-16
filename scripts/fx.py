#!/usr/bin/env python3
"""Convert amounts to BRL (or any currency) using ECB reference rates.

Source: Frankfurter (https://www.frankfurter.app), a keyless public API that
serves European Central Bank daily reference rates. Rates are cached for the
day in .cache/fx-<date>-<base>.json so repeated calls don't hit the network.

Usage:
    python3 scripts/fx.py 450 EUR            # -> BRL (default target)
    python3 scripts/fx.py 1200 USD --to BRL
    python3 scripts/fx.py --rate EUR         # just print the rate to BRL
    python3 scripts/fx.py 450 EUR --json     # machine-readable

ECB rates are published around 16:00 CET on working days. They are reference
rates, not what a card charges: card FX adds roughly 1-3% (Amex NL adds a
foreign transaction fee on non-EUR spend). Say so when it matters.
"""

import argparse
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
API = "https://api.frankfurter.app/latest?from={base}"


def get_rates(base: str) -> dict:
    base = base.upper()
    cache = CACHE_DIR / f"fx-{date.today().isoformat()}-{base}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    req = urllib.request.Request(API.format(base=base), headers={"User-Agent": "travel-hacking-toolkit"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    CACHE_DIR.mkdir(exist_ok=True)
    cache.write_text(json.dumps(data))
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("amount", nargs="?", type=float)
    ap.add_argument("currency", nargs="?")
    ap.add_argument("--to", default="BRL")
    ap.add_argument("--rate", metavar="CURRENCY", help="print the rate from CURRENCY to --to")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    base = (a.rate or a.currency or "").upper()
    target = a.to.upper()
    if not base:
        ap.error("give an amount and currency, or --rate CURRENCY")
    if base == target:
        rate, as_of = 1.0, date.today().isoformat()
    else:
        try:
            data = get_rates(base)
        except Exception as e:  # network or API failure: fail loudly, never guess a rate
            print(f"ERROR: could not fetch FX rates for {base}: {e}", file=sys.stderr)
            return 1
        if target not in data.get("rates", {}):
            print(f"ERROR: no {base}->{target} rate in ECB data", file=sys.stderr)
            return 1
        rate, as_of = data["rates"][target], data["date"]

    if a.rate:
        out = {"from": base, "to": target, "rate": rate, "as_of": as_of}
        print(json.dumps(out) if a.json else f"1 {base} = {rate:.4f} {target} (ECB, {as_of})")
        return 0
    if a.amount is None:
        ap.error("missing amount")
    converted = round(a.amount * rate, 2)
    out = {"amount": a.amount, "from": base, "to": target, "rate": rate, "converted": converted, "as_of": as_of}
    print(json.dumps(out) if a.json else f"{a.amount:,.2f} {base} = {converted:,.2f} {target} (rate {rate:.4f}, ECB {as_of})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
