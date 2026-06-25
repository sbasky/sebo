"""
Search Console data fetcher with week-over-week comparison.
Last 7 days vs average of previous 4 weeks.
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from auth import get_search_console_service

load_dotenv()

SITE_URL = os.getenv("SITE_URL", "")
DELTA_THRESHOLD = 2.0  # positions change treated as significant


def _week_range(weeks_ago: int) -> tuple[str, str]:
    """Return (start, end) for a week offset from yesterday.
    weeks_ago=0 → last 7 days ending yesterday.
    """
    end = date.today() - timedelta(days=1) - timedelta(weeks=weeks_ago)
    start = end - timedelta(days=6)
    return start.isoformat(), end.isoformat()


def _fetch_period(
    service, site_url: str, start: str, end: str, dimension: str, row_limit: int = 500
) -> dict[str, dict]:
    """Fetch one period for a single dimension. Returns dict keyed by key (query or page)."""
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": [dimension],
        "rowLimit": row_limit,
        "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}],
    }
    resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    return {
        row["keys"][0]: {
            "impressions": row["impressions"],
            "clicks": row["clicks"],
            "ctr": row["ctr"],
            "position": row["position"],
        }
        for row in resp.get("rows", [])
    }


def _avg_baseline(weeks: list[dict], key: str) -> dict | None:
    """Average metrics for a key across baseline weeks. None if key never appeared."""
    found = [w[key] for w in weeks if key in w]
    if not found:
        return None
    n = len(found)
    return {
        "impressions": sum(f["impressions"] for f in found) / n,
        "clicks": sum(f["clicks"] for f in found) / n,
        "ctr": sum(f["ctr"] for f in found) / n,
        "position": sum(f["position"] for f in found) / n,
    }


def _compare(
    current: dict[str, dict],
    baseline_weeks: list[dict[str, dict]],
    dimension: str,
) -> dict:
    """Categorise current-week keys into losing / winning / quick_wins / stable / new."""
    losing, winning, quick_wins, stable, new_keys = [], [], [], [], []

    for key, curr in current.items():
        base = _avg_baseline(baseline_weeks, key)
        row = {
            "key": key,
            dimension: key,
            "current_position": round(curr["position"], 1),
            "current_impressions": int(curr["impressions"]),
            "current_clicks": int(curr["clicks"]),
            "current_ctr": round(curr["ctr"] * 100, 2),
        }

        if base is None:
            row["baseline_position"] = None
            row["delta_position"] = None
            new_keys.append(row)
            continue

        row["baseline_position"] = round(base["position"], 1)
        row["baseline_impressions"] = round(base["impressions"], 1)
        delta = curr["position"] - base["position"]
        row["delta_position"] = round(delta, 1)

        if 8 <= curr["position"] <= 15 and curr["impressions"] >= 10:
            quick_wins.append(row)

        if delta > DELTA_THRESHOLD:
            losing.append(row)
        elif delta < -DELTA_THRESHOLD:
            winning.append(row)
        else:
            stable.append(row)

    losing.sort(key=lambda r: r["delta_position"], reverse=True)
    winning.sort(key=lambda r: r["delta_position"])
    quick_wins.sort(key=lambda r: r["current_impressions"], reverse=True)
    stable.sort(key=lambda r: r["current_impressions"], reverse=True)

    return {
        "losing": losing[:20],
        "winning": winning[:20],
        "quick_wins": quick_wins[:20],
        "stable": stable[:10],
        "new": new_keys[:10],
    }


def fetch_comparison(service=None, site_url: str = None) -> dict:
    """
    Fetch last 7 days vs avg of previous 4 weeks for queries and pages.
    Returns structured dict ready for brief_generator and snapshot.
    """
    service = service or get_search_console_service()
    site_url = site_url or SITE_URL

    curr_start, curr_end = _week_range(0)

    curr_queries = _fetch_period(service, site_url, curr_start, curr_end, "query")
    curr_pages = _fetch_period(service, site_url, curr_start, curr_end, "page")

    baseline_queries, baseline_pages, baseline_ranges = [], [], []
    for i in range(1, 5):
        s, e = _week_range(i)
        baseline_ranges.append({"start": s, "end": e})
        baseline_queries.append(_fetch_period(service, site_url, s, e, "query"))
        baseline_pages.append(_fetch_period(service, site_url, s, e, "page"))

    return {
        "site_url": site_url,
        "current_period": {"start": curr_start, "end": curr_end},
        "baseline_period": {"weeks": 4, "ranges": baseline_ranges},
        "queries": _compare(curr_queries, baseline_queries, "query"),
        "pages": _compare(curr_pages, baseline_pages, "page"),
    }


if __name__ == "__main__":
    import json
    print(f"Fetching data for: {SITE_URL}\n")
    data = fetch_comparison()
    q = data["queries"]
    print(f"Queries — losing: {len(q['losing'])}, winning: {len(q['winning'])}, "
          f"quick wins: {len(q['quick_wins'])}, new: {len(q['new'])}")
    if q["losing"]:
        print("\nTop losing keywords:")
        for r in q["losing"][:5]:
            print(f"  {r['key'][:50]:50} pos {r['baseline_position']} → {r['current_position']} (Δ+{r['delta_position']})")
    if q["quick_wins"]:
        print("\nTop quick wins:")
        for r in q["quick_wins"][:5]:
            print(f"  {r['key'][:50]:50} pos {r['current_position']}  {r['current_impressions']} imp")
