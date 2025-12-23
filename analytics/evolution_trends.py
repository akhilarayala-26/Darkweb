from datetime import datetime, timedelta
from collections import defaultdict
from analytics.utils import load_flattened_fingerprints

async def get_time_trends(days: int = 30):
    data = load_flattened_fingerprints()

    # Filter data within range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    trends_map = defaultdict(lambda: {"urls": 0, "keywords": 0, "sources": 0, "titles": 0})
    seen_titles = defaultdict(set)
    seen_sources = defaultdict(set)
    seen_keywords = defaultdict(set)

    for entry in data:
        collected_at = entry.get("collected_at")
        if not collected_at:
            continue

        try:
            date_obj = datetime.strptime(str(collected_at).split("T")[0], "%Y-%m-%d").date()
        except ValueError:
            continue

        if not (start_date <= date_obj <= end_date):
            continue

        date_key = date_obj.strftime("%b %d")
        trends_map[date_key]["urls"] += 1

        title = entry.get("title")
        source = entry.get("url", "").split("/")[2] if entry.get("url") else None
        keywords = entry.get("keywords", [])

        if title:
            seen_titles[date_key].add(title)
        if source:
            seen_sources[date_key].add(source)
        for k in keywords:
            seen_keywords[date_key].add(k)

    trends = []
    for date_key in sorted(trends_map.keys(), key=lambda d: datetime.strptime(d, "%b %d")):
        trends.append({
            "date": date_key,
            "urls": trends_map[date_key]["urls"],
            "keywords": len(seen_keywords[date_key]),
            "sources": len(seen_sources[date_key]),
            "titles": len(seen_titles[date_key]),
        })

    return {"trends": trends}

async def get_site_evolution():
    data = load_flattened_fingerprints()
    title_to_domains = defaultdict(lambda: defaultdict(list))

    for entry in data:
        url = entry.get("url")
        title = (entry.get("title") or "").strip()
        collected_at = entry.get("collected_at")

        if not url or not title or not collected_at:
            continue

        try:
            domain = url.split("/")[2]
            date = str(collected_at).split("T")[0]
            title_to_domains[title][domain].append(date)
        except Exception:
            continue

    evolutions = []
    for title, domains in title_to_domains.items():
        domain_list = []
        all_dates = set()

        for domain, dates in domains.items():
            sorted_dates = sorted(dates)
            first_seen = sorted_dates[0]
            last_seen = sorted_dates[-1]
            all_dates.update(dates)
            domain_list.append({
                "domain": domain,
                "first_seen": first_seen,
                "last_seen": last_seen
            })

        if len(domain_list) > 1:
            evolutions.append({
                "title": title,
                "domains": sorted(domain_list, key=lambda x: x["first_seen"]),
                "total_domains": len(domain_list),
                "active_days": len(all_dates)
            })

    evolutions.sort(key=lambda x: x["total_domains"], reverse=True)
    return {"site_evolutions": evolutions[:10]}
