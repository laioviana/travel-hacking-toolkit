#!/usr/bin/env python3
"""Look up crowdsourced status match reports on statusmatcher.com, live.

statusmatcher.com has one page per program (https://statusmatcher.com/company/<slug>)
with two report lists:
  - "obtaining status with X"  -> someone matched INTO X   (use --to X)
  - "leveraging status with X" -> someone matched FROM X   (use --from X)
Each report has an outcome (Match / Challenge / Deny), a date and a short text.
The report page itself also names the tiers on both sides (--details N).

Content policy: the site's terms forbid reusing its content without consent.
This script only fetches and summarises at runtime. Its cache lives in the
gitignored .cache/statusmatcher/ and nothing it fetches may be committed.

Hard rules (Research Integrity Protocol):
- NEVER fabricate. Only what the page states is returned. Crowdsourced reports
  are UNVERIFIED until the program's own terms confirm them.
- Fail closed. If a page can't be fetched or parsed, say so and exit nonzero
  for that program instead of returning an empty "no opportunities" result.

Usage:
    python3 scripts/statusmatcher.py --profile                 # from each status in data/my-profile.json
    python3 scripts/statusmatcher.py --from "all accor" --months 12
    python3 scripts/statusmatcher.py --to "flying blue" --details 5
    python3 scripts/statusmatcher.py --from accor --format table
    python3 scripts/statusmatcher.py --list                    # known programs and slugs
"""

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUGS_FILE = os.path.join(ROOT, "data", "statusmatcher-slugs.json")
PROFILE_FILE = os.path.join(ROOT, "data", "my-profile.json")
CACHE_DIR = os.path.join(ROOT, ".cache", "statusmatcher")
BASE = "https://statusmatcher.com"
UA = "Mozilla/5.0 (compatible; travel-hacking-toolkit/1.0)"
CACHE_TTL = 24 * 3600
REQUEST_DELAY = 1.0  # be polite: one request per second
MAX_PAGES = 5

_last_request = 0.0


class FetchError(Exception):
    pass


# ---------- HTTP + cache ----------

def fetch(path, use_cache=True):
    global _last_request
    url = BASE + path
    key = hashlib.sha1(url.encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, key + ".html")
    if use_cache and os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < CACHE_TTL:
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    wait = REQUEST_DELAY - (time.time() - _last_request)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise FetchError(f"{url} returned HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise FetchError(f"{url} failed: {e}") from e
    finally:
        _last_request = time.time()
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(body)
    return body


# ---------- parsing ----------

def text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def parse_date(s):
    try:
        return dt.datetime.strptime(s.strip(), "%B %d, %Y").date()
    except ValueError:
        return None


ITEM_RE = re.compile(
    r'<a href="/report/(\d+)">\s*<div class="result-box result-box-(\w+)">.*?'
    r'<h6[^>]*>\s*<span><span>(.*?)</span>\s*to\s*</span>\s*<span>(.*?)</span>\s*</h6>.*?'
    r'<span class="instructions">(.*?)</span>.*?'
    r'<span class="fw-bold">From:</span>.*?<br/>\s*<span>([A-Z][a-z]+ \d{1,2}, \d{4})</span>',
    re.S,
)


def parse_items(fragment):
    out = []
    for m in ITEM_RE.finditer(fragment):
        rid, outcome, frm, to, snippet, date = m.groups()
        d = parse_date(date)
        out.append({
            "report_id": int(rid),
            "url": f"{BASE}/report/{rid}",
            "outcome": outcome.capitalize(),
            "from_program": text(frm),
            "to_program": text(to),
            "date": d.isoformat() if d else None,
            "snippet": text(snippet),
        })
    return out


def section(page, list_id):
    start = page.find(f'id="{list_id}"')
    if start < 0:
        return None
    if list_id == "report-list-to":
        end = page.find('id="new-report"', start)
    else:
        end = page.find("</section>", start)
    return page[start:end if end > 0 else len(page)]


def parse_company(page):
    page = re.sub(r"<svg.*?</svg>", "", page, flags=re.S)
    info = {}
    h3 = re.search(r"<h3>(.*?) Status Match</h3>", page)
    if not h3:
        raise FetchError("page layout not recognised (no program heading)")
    info["page_title"] = text(h3.group(1))
    prog = re.search(r'id="report-list-to"[^>]*>Reports for obtaining status with (.*?)</h4>', page)
    info["program"] = text(prog.group(1)) if prog else info["page_title"]
    summ = re.search(
        r"is most likely to <strong>(\w+)</strong> Status based\s*on <span>(\d+)</span> of <span>(\d+)</span>",
        page,
    )
    if summ:
        info["into_summary"] = {
            "most_likely": summ.group(1),
            "count": int(summ.group(2)),
            "total_reports": int(summ.group(3)),
            "rate": round(int(summ.group(2)) / int(summ.group(3)), 2) if int(summ.group(3)) else None,
        }
    req = re.search(r"<h4>Request a Status Match</h4>(.*?)<p>Share your results", page, re.S)
    if req:
        block = req.group(1)
        links = re.findall(r'href="(https?://[^"]+)"', block)
        info["how_to_request"] = text(block)[:400]
        info["request_links"] = links
        info["tiers_offered"] = [text(t) for t in re.findall(r'<span class="status-box"[^>]*>(.*?)</span>', block)]
    return info, page


def company_reports(slug, direction, max_pages, since, use_cache):
    """direction: 'to' (matched INTO the program) or 'from' (matched FROM it)."""
    list_id = f"report-list-{direction}"
    seen, items, info = set(), [], None
    for p in range(max_pages):
        path = f"/company/{slug}" + (f"?page-{direction}={p}" if p else "")
        page = fetch(path, use_cache)
        if info is None:
            info, _ = parse_company(page)
        frag = section(page, list_id)
        if frag is None:
            raise FetchError(f"/company/{slug}: no {list_id} section")
        new = [i for i in parse_items(frag) if i["report_id"] not in seen]
        if not new:
            break
        for i in new:
            seen.add(i["report_id"])
        items.extend(new)
        dates = [i["date"] for i in new if i["date"]]
        if since and dates and min(dates) < since.isoformat():
            break  # lists are newest first; older pages only go further back
        if f"page-{direction}={p + 1}" not in page:
            break
    if since:
        items = [i for i in items if i["date"] and i["date"] >= since.isoformat()]
    return info, items


def report_details(report_id, use_cache):
    page = fetch(f"/report/{report_id}", use_cache)
    page = re.sub(r"<svg.*?</svg>", "", page, flags=re.S)
    m = re.search(
        r"<h4>\s*From\s*<a[^>]*>(.*?)</a>\s*<span>(.*?)</span>\s*<br/>\s*To\s*<a[^>]*>(.*?)</a>\s*<span>(.*?)</span>",
        page, re.S,
    )
    body = re.search(r'<div class="instructions text-break">(.*?)</div>', page, re.S)
    if not m:
        return {"error": "tiers not found on report page"}
    return {
        "from_tier": text(m.group(2)),
        "to_tier": text(m.group(4)),
        "text": text(body.group(1))[:600] if body else None,
    }


# ---------- aggregation ----------

def aggregate(items, key):
    groups = {}
    for i in items:
        g = groups.setdefault(i[key], {"program": i[key], "Match": 0, "Challenge": 0, "Deny": 0, "latest": None, "reports": []})
        g[i["outcome"]] = g.get(i["outcome"], 0) + 1
        if i["date"] and (g["latest"] is None or i["date"] > g["latest"]):
            g["latest"] = i["date"]
        g["reports"].append(i)
    out = []
    for g in groups.values():
        total = g["Match"] + g["Challenge"] + g["Deny"]
        g["total"] = total
        g["success_rate"] = round((g["Match"] + g["Challenge"]) / total, 2) if total else None
        out.append(g)
    out.sort(key=lambda g: (g["Match"] + g["Challenge"], g["total"], g["latest"] or ""), reverse=True)
    return out


# ---------- program resolution ----------

def load_slugs():
    with open(SLUGS_FILE, encoding="utf-8") as f:
        return json.load(f)["programs"]


def resolve(name, slugs):
    n = name.strip().lower()
    for key, p in slugs.items():
        if n == key or n == p["slug"].lower() or n == p["name"].lower() or n in p["aliases"]:
            return key, p
    for key, p in slugs.items():
        if any(n in a or a in n for a in p["aliases"] if len(a) > 3):
            return key, p
    return None, None


def profile_statuses():
    if not os.path.exists(PROFILE_FILE):
        raise SystemExit(f"{PROFILE_FILE} not found. Use --from <program> instead.")
    with open(PROFILE_FILE, encoding="utf-8") as f:
        prof = json.load(f)
    return [(s.get("program", ""), s.get("tier", "")) for s in prof.get("status", []) if s.get("program")]


# ---------- output ----------

def run_one(direction, name, tier, slugs, args, since):
    key, p = resolve(name, slugs)
    if not p:
        return {"query": name, "error": f"unknown program '{name}'. Add it to data/statusmatcher-slugs.json (slug from {BASE}/sitemap)."}
    try:
        info, items = company_reports(p["slug"], direction, args.pages, since, not args.no_cache)
    except FetchError as e:
        return {"query": name, "program_key": key, "error": str(e)}
    if args.details:
        for i in items[: args.details]:
            try:
                i.update(report_details(i["report_id"], not args.no_cache))
            except FetchError as e:
                i["details_error"] = str(e)
    counterpart = "to_program" if direction == "from" else "from_program"
    return {
        "query": name,
        "your_tier": tier or None,
        "program_key": key,
        "program": info.get("program"),
        "direction": direction,
        "page": f"{BASE}/company/{p['slug']}",
        "into_summary": info.get("into_summary"),
        "how_to_request": info.get("how_to_request") if direction == "to" else None,
        "request_links": info.get("request_links") if direction == "to" else None,
        "window_since": since.isoformat() if since else None,
        "report_count": len(items),
        "by_counterpart": aggregate(items, counterpart),
        "confidence": "UNVERIFIED (crowdsourced reports; confirm on the program's own terms before applying)",
    }


def print_table(results):
    for r in results:
        if "error" in r:
            print(f"\n**{r['query']}**: ERROR {r['error']}\n")
            continue
        arrow = "from" if r["direction"] == "from" else "into"
        tier = f" ({r['your_tier']})" if r.get("your_tier") else ""
        print(f"\n### Matches {arrow} {r['program']}{tier}, since {r['window_since'] or 'all time'}: {r['report_count']} reports")
        print(f"Source: {r['page']}\n")
        if r.get("into_summary"):
            s = r["into_summary"]
            print(f"Into {r['program']}: most likely **{s['most_likely']}** ({s['count']} of {s['total_reports']} reports, all time)\n")
        if not r["by_counterpart"]:
            print("No reports in this window.\n")
            continue
        label = "Target program" if r["direction"] == "from" else "Matched from"
        print(f"| {label} | Match | Challenge | Deny | Latest | Example |")
        print("|---|---|---|---|---|---|")
        for g in r["by_counterpart"]:
            ex = g["reports"][0]
            tiers = f" {ex['from_tier']} → {ex['to_tier']}." if ex.get("from_tier") else ""
            snip = (tiers + " " + ex["snippet"]).strip().replace("|", "/")[:110]
            print(f"| {g['program']} | {g['Match']} | {g['Challenge']} | {g['Deny']} | {g['latest']} | [{ex['outcome']}]({ex['url']}) {snip} |")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="frm", action="append", default=[], help="program you hold status in (repeatable)")
    ap.add_argument("--to", action="append", default=[], help="program you want status in (repeatable)")
    ap.add_argument("--profile", action="store_true", help="use every status in data/my-profile.json as --from")
    ap.add_argument("--months", type=int, default=12, help="only reports from the last N months (0 = all, default 12)")
    ap.add_argument("--pages", type=int, default=3, help=f"max list pages per program (default 3, cap {MAX_PAGES})")
    ap.add_argument("--details", type=int, default=0, help="fetch tiers for the N newest reports per program")
    ap.add_argument("--format", choices=["json", "table"], default="json")
    ap.add_argument("--no-cache", action="store_true", help="ignore the 24h cache")
    ap.add_argument("--list", action="store_true", help="list known programs and exit")
    args = ap.parse_args()
    args.pages = max(1, min(args.pages, MAX_PAGES))
    args.details = max(0, min(args.details, 15))

    slugs = load_slugs()
    if args.list:
        for k, p in sorted(slugs.items()):
            print(f"{k:24} {p['kind']:8} {BASE}/company/{p['slug']}")
        return 0

    queries = [("from", n, "") for n in args.frm] + [("to", n, "") for n in args.to]
    if args.profile:
        queries += [("from", prog, tier) for prog, tier in profile_statuses()]
    if not queries:
        ap.error("give --profile, --from or --to")

    since = (dt.date.today() - dt.timedelta(days=30 * args.months)) if args.months else None
    results = [run_one(d, n, t, slugs, args, since) for d, n, t in queries]

    if args.format == "table":
        print_table(results)
    else:
        json.dump({"fetched_at": dt.datetime.now().isoformat(timespec="seconds"), "results": results}, sys.stdout, indent=2, ensure_ascii=False)
        print()
    return 1 if all("error" in r for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
