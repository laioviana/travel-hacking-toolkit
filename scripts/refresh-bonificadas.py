#!/usr/bin/env python3
"""Refresh data/bonificadas.json from Brazilian points blogs.

Brazilian transfer bonuses ("transferências bonificadas") and point-purchase
promos change every few days, and no issuer publishes a machine-readable list.
This script reads the RSS feeds of two independent Brazilian blogs, keeps posts
from the last LOOKBACK_DAYS that announce a transfer bonus or a points sale,
and extracts what the headline states (percentage, programs, "ends today").

Hard rules (Research Integrity Protocol, same as refresh-transfer-bonuses.py):
- NEVER fabricate. Only what a headline literally says is extracted. Anything
  not in the headline (exact end date, club-only tiers, minimums) is left null
  and the agent must open the linked post before relying on it.
- Fail closed. If no feed can be fetched or parsed, exit nonzero and leave the
  existing file untouched.
- Confidence: LIKELY when both blogs report the same destination program and
  percentage; UNVERIFIED when only one does.

Usage:
    python3 scripts/refresh-bonificadas.py            # update file
    python3 scripts/refresh-bonificadas.py --dry-run  # print, don't write
    python3 scripts/refresh-bonificadas.py --days 21  # wider lookback
"""

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "data" / "bonificadas.json"
LOOKBACK_DAYS = 14

FEEDS = {
    "pontospravoar": ["https://pontospravoar.com/feed/", "https://pontospravoar.com/feed/?paged=2"],
    "passageirodeprimeira": ["https://passageirodeprimeira.com/feed/", "https://passageirodeprimeira.com/feed/?paged=2"],
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

# Canonical key -> regex matched against the headline. Keys match
# data/transfer-partners.json where a key exists there.
PROGRAMS = {
    "latam_pass": r"latam\s*pass|\blatam\b",
    "smiles": r"\bsmiles\b",
    "azul": r"\bazul\b|tudoazul",
    "tap": r"\btap\b|miles\s*&\s*go",
    "iberia": r"\biberia\b",
    "british_airways": r"british\s*airways",
    "qatar": r"\bqatar\b",
    "flying_blue": r"flying\s*blue",
    "accor": r"\baccor\b|\ball\b(?=.*accor)",
    "livelo": r"\blivelo\b",
    "esfera": r"\besfera\b",
}
# Sources of points that are not airline/hotel programs (bank cards, cashback)
ORIGINS = {
    "livelo": r"\blivelo\b",
    "esfera": r"\besfera\b",
    "itau": r"ita[uú]",
    "c6": r"\bc6\b",
    "nomad": r"\bnomad\b",
    "meliuz": r"m[ée]liuz",
    "inter": r"\binter\b",
    "btg": r"\bbtg\b",
    "bradesco": r"bradesco",
    "santander": r"santander",
    "credit_cards_several": r"cart(?:ão|ões)|parceiros",
}

TRANSFER_RE = re.compile(r"(?:até\s+)?(\d{1,3})\s*%\s*(?:de\s+)?b[ôo]nus", re.I)
DISCOUNT_RE = re.compile(r"(?:até\s+)?(\d{1,3})\s*%\s*(?:de\s+)?desconto", re.I)
ENDS_TODAY_RE = re.compile(r"acaba hoje|termina hoje|último dia|ultimo dia|só hoje|apenas hoje|últimas horas|ultimas horas", re.I)
UNTIL_RE = re.compile(r"até\s+(?:o\s+dia\s+)?(\d{1,2})/(\d{1,2})", re.I)


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_feed(xml):
    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def tag(name):
            m = re.search(rf"<{name}>(.*?)</{name}>", block, re.S)
            if not m:
                return ""
            return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1))).strip()
        title, link, pub = tag("title"), tag("link"), tag("pubDate")
        if not (title and link and pub):
            continue
        try:
            published = parsedate_to_datetime(pub).date()
        except (TypeError, ValueError):
            continue
        items.append({"title": title, "url": link, "published": published})
    return items


def find(patterns, text):
    return [k for k, rx in patterns.items() if re.search(rx, text, re.I)]


def classify(item):
    t = item["title"]
    low = t.lower()
    kind = None
    pct = None
    m = TRANSFER_RE.search(t)
    if m and re.search(r"transfer", low):
        kind, pct = "transfer_bonus", int(m.group(1))
    elif re.search(r"compra\s+de\s+(pontos|milhas)|compre\s+(pontos|milhas)|venda\s+de\s+(pontos|milhas)", low):
        m2 = DISCOUNT_RE.search(t) or TRANSFER_RE.search(t)
        kind, pct = "purchase_promo", int(m2.group(1)) if m2 else None
    if not kind:
        return None

    programs = find(PROGRAMS, t)
    origins = find(ORIGINS, t)
    if kind == "transfer_bonus":
        # "... de X para Y": the program after "para" is the destination.
        para = re.search(r".*\bpara\s+(?:a\s+|o\s+)?(.*)$", t, re.I)  # last "para"
        after = find(PROGRAMS, para.group(1)) if para else []
        if after:
            to_program = after[0]
            from_programs = [p for p in programs + origins if p != to_program and p != "credit_cards_several"] or None
            from_programs = sorted(set(from_programs)) if from_programs else None
            return _finish(item, kind, pct, to_program, from_programs, low)
        # Destination = first airline/hotel program that is not a bank currency.
        dest = [p for p in programs if p not in ("livelo", "esfera")]
        # Livelo/Esfera are the destination when points move INTO them (e.g. bank -> Livelo).
        if not dest and programs:
            dest = programs[:1]
        to_program = dest[0] if dest else None
        from_programs = [o for o in origins if o != to_program] or None
    else:
        to_program = programs[0] if programs else None
        from_programs = None

    return _finish(item, kind, pct, to_program, from_programs, low)


def _finish(item, kind, pct, to_program, from_programs, low):
    t = item["title"]
    end_date = None
    if ENDS_TODAY_RE.search(t):
        end_date = item["published"].isoformat()
    else:
        u = UNTIL_RE.search(t)
        if u:
            d, mo = int(u.group(1)), int(u.group(2))
            year = item["published"].year + (1 if mo < item["published"].month else 0)
            try:
                end_date = date(year, mo, d).isoformat()
            except ValueError:
                end_date = None

    excludes_esfera = bool(re.search(r"exceto\s+esfera", low))
    return {
        "kind": kind,
        "pct": pct,
        "pct_is_max": bool(re.search(r"até\s+\d{1,3}\s*%", low)),
        "to_program": to_program,
        "from": from_programs,
        "includes_livelo": bool(re.search(ORIGINS["livelo"], low)),
        "includes_esfera": bool(re.search(ORIGINS["esfera"], low)) and not excludes_esfera,
        "end_date_inclusive": end_date,
        "title": t,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, default=LOOKBACK_DAYS)
    a = ap.parse_args()

    today = date.today()
    cutoff = today - timedelta(days=a.days)
    raw = []
    ok_sources = []
    for source, urls in FEEDS.items():
        got = 0
        for url in urls:
            try:
                items = parse_feed(fetch(url))
            except Exception as e:
                print(f"WARN: {source} {url}: {e}", file=sys.stderr)
                continue
            got += len(items)
            for it in items:
                it["source"] = source
                raw.append(it)
        if got:
            ok_sources.append(source)
    if not ok_sources:
        print("ERROR: no feed could be fetched or parsed; leaving data untouched.", file=sys.stderr)
        return 1

    seen_urls = set()
    promos = []
    for it in raw:
        if it["published"] < cutoff or it["url"] in seen_urls:
            continue
        seen_urls.add(it["url"])
        c = classify(it)
        if not c:
            continue
        c.update({"published": it["published"].isoformat(), "source": it["source"], "url": it["url"]})
        if c["end_date_inclusive"] and c["end_date_inclusive"] < today.isoformat():
            c["status"] = "expired"
        else:
            c["status"] = "check_post" if not c["end_date_inclusive"] else "active"
        promos.append(c)

    # Merge reports of the same promo (same kind, destination, pct, origins,
    # published within 2 days) into one entry listing every source URL.
    merged = []
    for p in sorted(promos, key=lambda p: p["published"], reverse=True):
        key = (p["kind"], p["to_program"], p["pct"], tuple(p["from"] or []))
        for m in merged:
            mkey = (m["kind"], m["to_program"], m["pct"], tuple(m["from"] or []))
            if mkey == key and abs((date.fromisoformat(m["published"]) - date.fromisoformat(p["published"])).days) <= 2:
                m["urls"].append(p["url"])
                m["sources"] = sorted(set(m["sources"]) | {p["source"]})
                m["end_date_inclusive"] = m["end_date_inclusive"] or p["end_date_inclusive"]
                break
        else:
            p["urls"] = [p.pop("url")]
            p["sources"] = [p.pop("source")]
            merged.append(p)
    for p in merged:
        if p["end_date_inclusive"] and p["end_date_inclusive"] < today.isoformat():
            p["status"] = "expired"
        # Cross-source confirmation: both blogs report the same destination + pct.
        both = {s for q in merged if q["kind"] == p["kind"] and q["to_program"] == p["to_program"] and q["pct"] == p["pct"] for s in q["sources"]}
        p["confidence"] = "LIKELY" if len(both) >= 2 else "UNVERIFIED"
    promos = merged

    out = {
        "_meta": {
            "last_updated": today.isoformat(),
            "staleness_days": 7,
            "description": "Brazilian transfer bonuses (bonificadas) and point-purchase promos announced in the last %d days, extracted from blog headlines. Only headline facts are stored; open the post (url) for end date, club-only tiers and minimums before acting." % a.days,
            "sources": [u for urls in FEEDS.values() for u in urls],
            "sources_ok": ok_sources,
            "generated_by": "scripts/refresh-bonificadas.py",
        },
        "promos": promos,
    }
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if a.dry_run:
        print(text)
    else:
        DATA_FILE.write_text(text)
        print(f"Wrote {DATA_FILE.relative_to(REPO)}: {len(promos)} promos from {', '.join(ok_sources)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
