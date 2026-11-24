---
name: status-matcher
description: Find status match opportunities from the elite status the user already holds, using live crowdsourced reports on statusmatcher.com (Match, Challenge or Deny, with dates and what proof worked). Run it proactively on any trip plan, hotel or car search, or airline or hotel program question, and whenever status, tiers, a status match or statusmatcher.com comes up. Feeds the status-match skill, which applies the lifetime and once-per-N-years rules.
category: loyalty
summary: Live status match opportunities from your current elite statuses, via statusmatcher.com reports.
api_key: None (public site)
---

# Status Matcher

The user already holds elite status (see `status` in `data/my-profile.json`). Other programs often match it for free or for a fee. statusmatcher.com collects reports of people trying, with the outcome and how they did it. This skill reads those reports live and turns them into opportunities that fit the user's actual travel.

- **Script:** `scripts/statusmatcher.py` (fetches live, 1 request per second, 24h cache in the gitignored `.cache/statusmatcher/`).
- **Program map:** `data/statusmatcher-slugs.json` (program → statusmatcher.com page).
- **Rules for applying:** the [`status-match`](../status-match/SKILL.md) skill. This skill finds opportunities; that one decides whether to spend them.

## Content rule (public repo)

statusmatcher.com's terms forbid reusing its content without written consent. Summarise reports in the conversation and link them. **Never write report text into a tracked file**, never add it to `data/`, and never add this script to the weekly refresh workflow.

## When to run (proactive, no asking)

- Any trip plan (`ams-for`, `plan-trip`, `trip-planner`) or hotel or car rental search.
- Any question about an airline, hotel or car rental program the user could earn status in.
- The user mentions status, tiers, a match, a challenge or statusmatcher.com.

Run it, then mention a match only when it fits the current trip or program. One line is enough when nothing fits. Don't end with an offer to check more.

## Workflow

### 1. Read the user's statuses

Use `my-points` (the `status` array in the profile). Each entry has a `program` and a `tier`.

### 2. Pull outbound opportunities

```bash
python3 scripts/statusmatcher.py --profile --months 12 --details 5 --format table
```

- `--profile` runs a FROM-lookup for every status in the profile.
- `--details N` opens the N newest reports per program to get the tiers on both sides (e.g. Gold → Silver). Use it for the shortlist, not everything.
- Default output is JSON (`--format json`); `by_counterpart` groups reports by target program with Match / Challenge / Deny counts and the latest date.

For a specific target ("can I get Flying Blue status?"), look at it from the other side too:

```bash
python3 scripts/statusmatcher.py --to "flying blue" --details 5 --format table
```

This adds the target's all-time match rate (`into_summary`) and how to apply (`request_links`, `tiers_offered`), including paid statusmatch.com concierge links.

`python3 scripts/statusmatcher.py --list` shows every mapped program. If a program is missing, find its slug on https://statusmatcher.com/sitemap and add it to `data/statusmatcher-slugs.json`. Hotel groups use one brand page (Accor → `sofitel`), which shows the group-level reports.

### 3. Filter to what matters for this user

Keep a target only if it passes all of these:

1. **Recent success.** At least one Match or Challenge in the last 12 months, and more successes than denials. A single old report is a lead, not an opportunity.
2. **Tier fit.** Check the user's tier against what worked. Many reports match from a higher tier (e.g. Accor Platinum). If successful reports only came from higher tiers, say the user's tier is unproven.
3. **Travel fit.** The status must be useful on travel the user actually does: the priority routes in `data/home-routes.json` (AMS ⇄ FOR, so SkyTeam via Flying Blue, oneworld via Iberia/LATAM/TAP), the current trip, hotels in Europe and Brazil, and car rental in Brazil (Localiza) or Europe (Europcar, Sixt).
4. **Not US-only.** Drop programs whose value is US-only (US domestic airlines, US rental desks) unless the trip goes there.

### 4. Apply the status-match rules

For every target that passes, load [`status-match`](../status-match/SKILL.md) and `data/status-match.json`:

- **Lifetime and once-per-N-years limits first.** Flying Blue via paid concierge is once per lifetime. A wasted match can't be undone. If there's no travel in the next 6–12 months that uses it, the verdict is "hold".
- **Free direct match beats paid concierge.** For paid matches, convert the fee to R$ with `python3 scripts/fx.py` and compare it with the benefit on the user's real trips (bags for the whole party, lounge for the party, seat selection, upgrades).
- **Challenges.** Note what has to be completed (stays, flights) and whether the user's travel covers it in the window.

### 5. Present

| Target | Your status → reported tier | Reports (12 mo) | Latest | Cost | Lifetime limit | Fit | Verdict |
|---|---|---|---|---|---|---|---|
| (target program) | (your tier) → (tier in reports) | 3 Match, 0 Deny | YYYY-MM-DD | Free | None known | Car rental in Europe | Apply before next rental |

- Link the newest supporting report for each row.
- **Verdicts:** apply now, apply before trip X, hold (no travel uses it yet), or skip.
- Mark every row **UNVERIFIED**: these are crowdsourced reports. Before applying, confirm on the program's own page (or the statusmatch.com FAQ for paid matches).
- Mention what proof worked in the reports (status card screenshot, recent stays, upcoming booking). Upcoming bookings often matter, so time the application after booking the trip.

## Failure handling

- **Fetch or parse error:** the script returns `error` for that program and exits nonzero only when everything failed. Say the lookup failed and why. Don't report "no opportunities".
- **Layout change:** if every program fails with "layout not recognised", the site's HTML changed. Fix the regexes in `scripts/statusmatcher.py` (`ITEM_RE`, `parse_company`).
- **No status in the profile:** run `--to` lookups for the programs the trip uses instead, and explain that most matches need an existing status to match from.
