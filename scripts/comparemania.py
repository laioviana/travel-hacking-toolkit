#!/usr/bin/env python3
"""Cashback and points/miles offers for a Brazilian online store, from Comparemania.

comparemania.com.br lists, per store, every cashback site (Méliuz, Cuponomia,
PicPay, Inter, ...) and every points program (Esfera, Livelo, Smiles, Azul,
LATAM Pass, TAP) with its current rate. This script reads that page, values
each offer in R$ for a purchase amount, and ranks them.

Points are valued like scripts/shopping_value.py: data/shopping-portals.json
"valuation", overridden by avg_cost_per_milheiro_brl in data/my-balances.json.

Usage:
  python3 scripts/comparemania.py netshoes                  # R$ 1,000 purchase
  python3 scripts/comparemania.py "magazine luiza" --amount 3500
  python3 scripts/comparemania.py booking --amount 2000 --json
  python3 scripts/comparemania.py --search decolar           # list matching pages
  python3 scripts/comparemania.py --top                      # biggest rate jumps today
  python3 scripts/comparemania.py netshoes --giftcards       # gift card offers too

Plain HTTP works (robots.txt allows everything except /redirecionar/oferta/).
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shopping_value as sv  # noqa: E402

BASE = "https://www.comparemania.com.br"
UA = "Mozilla/5.0 (travel-hacking-toolkit; comparemania.py)"

# Comparemania display name (lowercase) -> valuation key in data/shopping-portals.json
PROGRAMS = {
    "esfera": "esfera",
    "livelo": "livelo",
    "shopping livelo": "livelo",
    "smiles": "smiles",
    "azul": "azul",
    "tudoazul": "azul",
    "latam pass": "latam_pass",
    "shopping latam": "latam_pass",
    "tap miles&go": "tap",
    "tap": "tap",
}


def get(path: str) -> str:
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def search(term: str) -> list[dict]:
    q = urllib.parse.urlencode({"termo": term})
    return json.loads(get(f"/api/search/buscar-nomes?{q}"))


def resolve(store: str) -> str:
    """Store name or slug -> page path like /cashback-netshoes."""
    if store.startswith(("cashback-", "giftcard-", "/")):
        return "/" + store.lstrip("/")
    hits = search(store)
    pages = [h for h in hits if h.get("urlDestino", "").startswith("cashback-")]
    if not pages:
        names = ", ".join(h["nome"] for h in hits) or "nothing"
        raise SystemExit(f"No Comparemania store page for '{store}'. Search found: {names}")
    norm = store.lower().replace(" ", "")
    exact = [h for h in pages if h["nome"].split(":", 1)[-1].strip().lower().replace(" ", "") == norm]
    return "/" + (exact or pages)[0]["urlDestino"]


def parse_rate(text: str) -> dict:
    t = text.lower().replace(",", ".")
    upto = "até" in t
    m = re.search(r"([\d.]+)\s*%", t)
    if m:
        kind = "discount" if "desconto" in t else "cashback"
        return {"value": float(m.group(1)), "unit": "percent", "kind": kind, "upto": upto, "unit_assumed": False}
    m = re.search(r"([\d.]+)\s*pt", t)
    if not m:
        return {"value": None, "unit": "unknown", "kind": "unknown", "upto": upto, "unit_assumed": True}
    val = float(m.group(1))
    if "/u$" in t or "/us$" in t:
        unit, assumed = "per_usd", False
    elif "/€" in t or "/eur" in t:
        unit, assumed = "per_eur", False
    elif "/r$" in t:
        unit, assumed = "per_brl", False
    else:  # "pt(s)" with no currency: Comparemania means per R$ for BR stores
        unit, assumed = "per_brl", True
    return {"value": val, "unit": unit, "kind": "points", "upto": upto, "unit_assumed": assumed}


def parse_offers(page: str) -> list[dict]:
    offers = []
    for m in re.finditer(r"<tr([^>]*)>(.*?)</tr>", page, re.S):
        attrs, inner = m.groups()
        tds = re.findall(r"<td[^>]*>(.*?)</td>", inner, re.S)
        if len(tds) < 2:
            continue
        site, rate_text = clean(tds[0]), clean(tds[1])
        recommended = "Recomendado" in rate_text
        rate_text = rate_text.replace("Recomendado", "").strip()
        tgt = re.search(r'data-bs-target="#([^"]+)"', attrs)
        section = "giftcard" if (tgt and tgt.group(1) == "loginModalCashback") else None
        r = parse_rate(rate_text)
        if section is None:
            section = "points" if r["kind"] == "points" else "cashback"
        offers.append({
            "site": "(login to see seller)" if site == "Bloqueado" else site,
            "section": section,
            "rate_text": rate_text,
            "recommended": recommended,
            **r,
        })
    return offers


def value_offers(offers: list[dict], amount_brl: float) -> list[dict]:
    overrides = sv.cost_basis_overrides()
    ccy = {"per_brl": "BRL", "per_usd": "USD", "per_eur": "EUR"}
    for o in offers:
        o["program"] = PROGRAMS.get(o["site"].lower())
        o["value_brl"] = None
        if o["value"] is None:
            continue
        if o["unit"] == "percent":
            o["value_brl"] = round(amount_brl * o["value"] / 100, 2)
            o["valued_at"] = "cash" if o["kind"] == "cashback" else "discount"
        elif o["program"]:
            units = amount_brl / sv.to_brl_rate(ccy[o["unit"]]) * o["value"]
            mv, basis = sv.milheiro_value(o["program"], overrides)
            o["points"] = round(units)
            o["value_brl"] = round(units / 1000 * mv, 2)
            o["valued_at"] = f"R$ {mv:.2f}/milheiro ({basis})"
        else:
            o["valued_at"] = "no valuation for this program"
        if o["value_brl"] is not None:
            o["effective_pct"] = round(o["value_brl"] / amount_brl * 100, 2)
    return offers


def top() -> list[dict]:
    page = get("/")
    out = []
    for m in re.finditer(
        r'<a[^>]*href="/(cashback-[^"]+)"[^>]*>.*?<h6[^>]*>(.*?)</h6>.*?</svg>|'
        r'<a[^>]*href="/(cashback-[^"]+)"[^>]*>.*?<h6[^>]*>(.*?)</h6>\s*<div[^>]*>\s*<span[^>]*>(.*?)</span>\s*<small[^>]*>(.*?)</small>',
        page, re.S,
    ):
        if m.group(3):
            out.append({"slug": m.group(3), "store": clean(m.group(4)),
                        "change_vs_usual": clean(m.group(5)), "best_rate": clean(m.group(6))})
    seen, uniq = set(), []
    for r in out:
        if r["slug"] not in seen:
            seen.add(r["slug"])
            uniq.append(r)
    return uniq


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("store", nargs="?", help="store name or Comparemania slug (cashback-netshoes)")
    ap.add_argument("--amount", type=float, default=1000.0, help="purchase amount in R$ (default 1000)")
    ap.add_argument("--giftcards", action="store_true", help="also read the store's gift card page")
    ap.add_argument("--search", metavar="TERM", help="list Comparemania pages matching TERM")
    ap.add_argument("--top", action="store_true", help="stores with the biggest rate increase today")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.search:
        res = search(a.search)
        print(json.dumps(res, indent=2, ensure_ascii=False) if a.json else
              "\n".join(f"{h['origem']:9} {h['nome']}  ->  {BASE}/{h['urlDestino']}" for h in res))
        return
    if a.top:
        res = top()
        if a.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print("| Store | vs usual | Best rate | Page |\n|---|---|---|---|")
            for r in res:
                print(f"| {r['store']} | {r['change_vs_usual']} | {r['best_rate']} | {BASE}/{r['slug']} |")
        return
    if not a.store:
        ap.error("give a store, --search TERM or --top")

    path = resolve(a.store)
    offers = parse_offers(get(path))
    if a.giftcards:
        gc_path = path.replace("/cashback-", "/giftcard-", 1)
        try:
            gc = parse_offers(get(gc_path))
            for o in gc:
                o["section"] = "giftcard"
            offers += gc
        except Exception as e:  # no gift card page for this store
            print(f"(no gift card page: {e})", file=sys.stderr)
    if not offers:
        raise SystemExit(f"No offers parsed from {BASE}{path}. The page layout may have changed.")
    offers = value_offers(offers, a.amount)
    offers.sort(key=lambda o: (o["value_brl"] is None, -(o["value_brl"] or 0)))

    if a.json:
        print(json.dumps({"store_page": BASE + path, "amount_brl": a.amount, "offers": offers},
                         indent=2, ensure_ascii=False))
        return
    print(f"{BASE}{path}  |  purchase R$ {a.amount:,.2f}\n")
    print("| # | Type | Site / program | Rate | Value (R$) | Effective % | Valued at |")
    print("|---|---|---|---|---|---|---|")
    for i, o in enumerate(offers, 1):
        rate = o["rate_text"] + (" (unit assumed R$)" if o.get("unit_assumed") and o["kind"] == "points" else "")
        if o["recommended"]:
            rate += " ★"
        val = f"{o['value_brl']:,.2f}" if o["value_brl"] is not None else "n/a"
        eff = f"{o['effective_pct']:.2f}%" if o.get("effective_pct") is not None else "n/a"
        print(f"| {i} | {o['section']} | {o['site']} | {rate} | {val} | {eff} | {o.get('valued_at', '')} |")


if __name__ == "__main__":
    main()
