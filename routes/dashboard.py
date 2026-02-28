from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from urllib.parse import urlparse
from pymongo import MongoClient
import os

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ==============================
# TOPIC → DATABASE MAPPING
# ==============================
TOPIC_DB_MAP = {
    "drugs": {"db": "darkweb_pipeline", "label": "Drugs & Forums", "icon": "pill", "color": "#8B5CF6"},
    "credit_card": {"db": "darkweb_pipeline_c1", "label": "Credit Card", "icon": "credit-card", "color": "#F59E0B"},
    "weapons": {"db": "darkweb_pipeline_c2", "label": "Weapons", "icon": "crosshair", "color": "#EF4444"},
}

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")


def get_db(topic_id: str):
    if topic_id not in TOPIC_DB_MAP:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    client = MongoClient(MONGO_URI)
    return client[TOPIC_DB_MAP[topic_id]["db"]]


def load_fingerprints(db, start_date: str = None, end_date: str = None):
    """Load and flatten fingerprints, optionally filtered by date range.
    
    The fingerprints_data collection stores documents with:
      _id = date string like "2025-02-15"
      content = { text_hash: { records: [...], classification: [...], ... } }
    
    We filter at the document level first using _id (the date),
    then use doc_date as the canonical date for each record.
    """
    collection = db["fingerprints_data"]
    all_entries = []

    # Build MongoDB query filter using document _id (the date)
    query = {}
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        if date_filter:
            query["_id"] = date_filter

    print(f"[load_fingerprints] query={query}, start={start_date}, end={end_date}")

    for doc in collection.find(query, {"_id": 1, "content": 1}):
        doc_date = str(doc.get("_id", ""))
        content = doc.get("content", {})

        if isinstance(content, dict):
            for hash_key, item in content.items():
                if isinstance(item, dict):
                    records = item.get("records", [])
                    classification = item.get("classification", [])
                    pgp_keys = item.get("pgp_keys", [])
                    btc_wallets = item.get("btc_wallets", [])
                    emails = item.get("emails", [])

                    if isinstance(records, list):
                        for rec in records:
                            collected_at = rec.get("collected_at") or doc_date

                            entry = {
                                "url": rec.get("url"),
                                "title": rec.get("title"),
                                "language": rec.get("language", "unknown"),
                                "sentiment_score": rec.get("sentiment", {}).get("polarity", 0)
                                    if isinstance(rec.get("sentiment"), dict) else 0,
                                "category": rec.get("category", "uncategorized"),
                                "keywords": rec.get("keywords", []),
                                "collected_at": doc_date,
                                "status_code": rec.get("status_code"),
                                "load_time_s": rec.get("load_time_s"),
                                "page_size_kb": rec.get("page_size_kb"),
                                "onion_links_outbound": rec.get("onion_links_outbound", []),
                                "metadata": rec.get("metadata", {}),
                                "classification": classification,
                                "pgp_keys": pgp_keys,
                                "btc_wallets": btc_wallets,
                                "emails": emails,
                            }
                            all_entries.append(entry)

    print(f"[load_fingerprints] loaded {len(all_entries)} entries")
    return all_entries


# ==============================
# ENDPOINTS
# ==============================

@router.get("/topics")
def get_topics():
    """Return list of available topics with stats."""
    topics = []
    client = MongoClient(MONGO_URI)
    for topic_id, info in TOPIC_DB_MAP.items():
        db = client[info["db"]]
        fp_count = 0
        for doc in db["fingerprints_data"].find({}, {"content": 1}):
            content = doc.get("content", {})
            for item in content.values():
                if isinstance(item, dict):
                    fp_count += len(item.get("records", []))

        group_count = db["grouped_titles_data"].count_documents({})

        # Get available date range
        dates = [doc["_id"] for doc in db["fingerprints_data"].find({}, {"_id": 1})]
        dates.sort()

        topics.append({
            "id": topic_id,
            "label": info["label"],
            "icon": info["icon"],
            "color": info["color"],
            "total_records": fp_count,
            "total_pipeline_runs": len(dates),
            "first_date": dates[0] if dates else None,
            "last_date": dates[-1] if dates else None,
        })
    return {"topics": topics}


@router.get("/topic/{topic_id}/overview")
def get_overview(topic_id: str, start: str = None, end: str = None):
    """Summary stats for a topic."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    if not data:
        return {"summary": {}, "message": "No data found for this date range"}

    # Unique domains
    domains = set()
    for entry in data:
        url = entry.get("url", "")
        try:
            domains.add(urlparse(url).netloc)
        except Exception:
            pass

    # Sentiment stats
    sentiments = [e["sentiment_score"] for e in data if e.get("sentiment_score") is not None]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

    # Date range of data
    dates = set()
    for e in data:
        try:
            dates.add(str(e.get("collected_at", "")).split("T")[0])
        except Exception:
            pass
    sorted_dates = sorted(dates)

    # Mirror count
    mirror_count = 0
    try:
        mirror_doc = db["mirror_data"].find_one(sort=[("_id", -1)])
        if mirror_doc:
            mirror_count = mirror_doc.get("summary", {}).get("total_mirror_clusters", 0)
    except Exception:
        pass

    # Grouped titles count
    group_count = 0
    try:
        gt_doc = db["grouped_titles_data"].find_one(sort=[("_id", -1)])
        if gt_doc:
            group_count = gt_doc.get("total_groups", 0)
    except Exception:
        pass

    return {
        "summary": {
            "total_records": len(data),
            "unique_domains": len(domains),
            "total_groups": group_count,
            "mirror_clusters": mirror_count,
            "avg_sentiment": round(avg_sentiment, 4),
            "data_start": sorted_dates[0] if sorted_dates else None,
            "data_end": sorted_dates[-1] if sorted_dates else None,
            "total_days": len(sorted_dates),
        }
    }


@router.get("/topic/{topic_id}/keywords")
def get_keywords(topic_id: str, start: str = None, end: str = None, limit: int = 20):
    """Top keywords for a topic, filtered by date."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    all_keywords = []
    for item in data:
        kws = item.get("keywords") or []
        for kw in kws:
            if isinstance(kw, str):
                all_keywords.append(kw.lower())

    counter = Counter(all_keywords)
    top = [{"keyword": k, "count": c} for k, c in counter.most_common(limit)]
    return {"keywords": top}


@router.get("/topic/{topic_id}/groups")
def get_groups(topic_id: str, start: str = None, end: str = None):
    """Grouped titles with URLs and content summaries."""
    db = get_db(topic_id)

    # Get the latest grouped titles document (or specific date)
    if end:
        gt_doc = db["grouped_titles_data"].find_one({"_id": {"$lte": end}}, sort=[("_id", -1)])
    else:
        gt_doc = db["grouped_titles_data"].find_one(sort=[("_id", -1)])

    if not gt_doc:
        return {"groups": [], "total": 0}

    # Load fingerprints to get content metadata per title
    fingerprints = load_fingerprints(db, start, end)
    title_meta = defaultdict(lambda: {
        "keywords": [], "sentiments": [], "languages": [],
        "categories": [], "page_sizes": [], "load_times": []
    })
    for entry in fingerprints:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        meta = title_meta[title]
        kws = entry.get("keywords") or []
        for kw in kws:
            if isinstance(kw, str) and len(kw) > 2:
                meta["keywords"].append(kw.lower())
        s = entry.get("sentiment_score", 0)
        if s is not None:
            meta["sentiments"].append(s)
        lang = entry.get("language")
        if lang and lang != "unknown":
            meta["languages"].append(lang)
        cat = entry.get("category")
        if cat and cat != "uncategorized":
            meta["categories"].append(cat)

    content = gt_doc.get("content", {})
    groups = []
    for title, urls in content.items():
        unique_urls = list(set(urls))
        domains = list(set(urlparse(u).netloc for u in unique_urls if u))

        # Build summary from fingerprint metadata
        meta = title_meta.get(title, {})
        kw_counter = Counter(meta.get("keywords", []))
        top_keywords = [k for k, _ in kw_counter.most_common(5)]
        sentiments = meta.get("sentiments", [])
        pos = sum(1 for s in sentiments if s > 0.05)
        neg = sum(1 for s in sentiments if s < -0.05)
        neu = len(sentiments) - pos - neg
        avg_s = round(sum(sentiments) / len(sentiments), 3) if sentiments else 0
        lang_counter = Counter(meta.get("languages", []))
        top_langs = [{"lang": l, "count": c} for l, c in lang_counter.most_common(3)]

        groups.append({
            "title": title,
            "urls": unique_urls,
            "url_count": len(unique_urls),
            "domain_count": len(domains),
            "domains": domains[:5],
            "summary": {
                "top_keywords": top_keywords,
                "sentiment": {"positive": pos, "neutral": neu, "negative": neg, "avg": avg_s},
                "languages": top_langs,
            }
        })

    groups.sort(key=lambda x: x["url_count"], reverse=True)
    return {"groups": groups, "total": len(groups), "date": gt_doc.get("_id")}


@router.get("/topic/{topic_id}/domains")
def get_domains(topic_id: str, start: str = None, end: str = None):
    """Unique domains grouped by day."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    grouped = defaultdict(lambda: defaultdict(list))
    for rec in data:
        url = rec.get("url")
        collected_at = rec.get("collected_at")
        if not url or not collected_at:
            continue
        try:
            domain = urlparse(url).netloc.lower()
            date_key = str(collected_at).split("T")[0]
        except Exception:
            continue

        existing_titles = [item.get("title") for item in grouped[date_key][domain]]
        title = rec.get("title", "Untitled")
        if title not in existing_titles:
            grouped[date_key][domain].append({
                "title": title,
                "language": rec.get("language"),
                "sentiment_score": rec.get("sentiment_score"),
                "category": rec.get("category"),
                "keywords": rec.get("keywords"),
                "status_code": rec.get("status_code"),
                "load_time_s": rec.get("load_time_s"),
                "page_size_kb": rec.get("page_size_kb"),
                "classification": rec.get("classification"),
            })

    return {"daily_domains": dict(grouped)}


@router.get("/topic/{topic_id}/sentiment")
def get_sentiment(topic_id: str, start: str = None, end: str = None):
    """Sentiment distribution and time series."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    positive = neutral = negative = 0
    daily_sentiment = defaultdict(list)

    for entry in data:
        score = entry.get("sentiment_score", 0) or 0
        if score > 0.05:
            positive += 1
        elif score < -0.05:
            negative += 1
        else:
            neutral += 1

        try:
            date_key = str(entry.get("collected_at", "")).split("T")[0]
            daily_sentiment[date_key].append(score)
        except Exception:
            pass

    # Daily averages
    timeline = []
    for date in sorted(daily_sentiment.keys()):
        scores = daily_sentiment[date]
        timeline.append({
            "date": date,
            "avg_sentiment": round(sum(scores) / len(scores), 4) if scores else 0,
            "count": len(scores),
        })

    return {
        "distribution": {"positive": positive, "neutral": neutral, "negative": negative},
        "timeline": timeline,
        "total": positive + neutral + negative,
    }


@router.get("/topic/{topic_id}/trends")
def get_trends(topic_id: str, start: str = None, end: str = None):
    """Time-based trends: URLs, keywords, sources, titles over time."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    trends_map = defaultdict(lambda: {"urls": 0, "keywords": 0, "sources": 0, "titles": 0})
    seen_titles = defaultdict(set)
    seen_sources = defaultdict(set)
    seen_keywords = defaultdict(set)

    for entry in data:
        collected_at = entry.get("collected_at")
        if not collected_at:
            continue
        try:
            date_key = str(collected_at).split("T")[0]
        except Exception:
            continue

        trends_map[date_key]["urls"] += 1

        title = entry.get("title")
        url = entry.get("url", "")
        source = urlparse(url).netloc if url else None
        keywords = entry.get("keywords", [])

        if title:
            seen_titles[date_key].add(title)
        if source:
            seen_sources[date_key].add(source)
        for k in keywords:
            if isinstance(k, str):
                seen_keywords[date_key].add(k)

    trends = []
    for date_key in sorted(trends_map.keys()):
        trends.append({
            "date": date_key,
            "urls": trends_map[date_key]["urls"],
            "keywords": len(seen_keywords[date_key]),
            "sources": len(seen_sources[date_key]),
            "titles": len(seen_titles[date_key]),
        })

    return {"trends": trends}


@router.get("/topic/{topic_id}/mirrors")
def get_mirrors(topic_id: str):
    """Mirror detection clusters."""
    db = get_db(topic_id)

    # Get the latest mirror data
    mirror_doc = db["mirror_data"].find_one(sort=[("_id", -1)])
    if not mirror_doc:
        return {"clusters": [], "summary": {}}

    clusters = mirror_doc.get("mirror_clusters", [])
    summary = mirror_doc.get("summary", {})

    return {
        "clusters": clusters,
        "summary": summary,
        "date": mirror_doc.get("_id"),
    }


@router.get("/topic/{topic_id}/actors")
def get_actors(topic_id: str, start: str = None, end: str = None):
    """Extract actor intelligence: BTC wallets, PGP keys, emails."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    btc_wallets = Counter()
    pgp_keys = []
    emails = Counter()
    seen_pgp = set()

    for entry in data:
        for wallet in entry.get("btc_wallets", []):
            if wallet:
                btc_wallets[wallet] += 1
        for key in entry.get("pgp_keys", []):
            key_short = key[:64] if key else ""
            if key_short and key_short not in seen_pgp:
                seen_pgp.add(key_short)
                pgp_keys.append({"key_preview": key_short, "full_key": key})
        for email in entry.get("emails", []):
            if email:
                emails[email] += 1

        # Also check metadata
        meta = entry.get("metadata", {})
        for wallet in meta.get("btc_wallets", []):
            if wallet:
                btc_wallets[wallet] += 1
        for key in meta.get("pgp_keys", []):
            key_short = key[:64] if key else ""
            if key_short and key_short not in seen_pgp:
                seen_pgp.add(key_short)
                pgp_keys.append({"key_preview": key_short, "full_key": key})
        for email in meta.get("emails", []):
            if email:
                emails[email] += 1

    return {
        "btc_wallets": [{"address": addr, "count": c} for addr, c in btc_wallets.most_common(50)],
        "pgp_keys": pgp_keys[:20],
        "emails": [{"email": addr, "count": c} for addr, c in emails.most_common(50)],
        "totals": {
            "btc_wallets": len(btc_wallets),
            "pgp_keys": len(pgp_keys),
            "emails": len(emails),
        }
    }


@router.get("/topic/{topic_id}/evolution")
def get_evolution(topic_id: str, start: str = None, end: str = None):
    """URL evolution — titles first, then date-span sub-groups within each title.
    
    Hierarchy:
      Title A (total URLs)
        ├── Feb 24 → Feb 26 (all days): 3 links
        ├── Feb 24 only: 5 links
        └── ...
    """
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    # Step 1: Build url -> { dates, title, metadata }
    url_map = {}
    for entry in data:
        url = entry.get("url")
        if not url:
            continue
        date_str = str(entry.get("collected_at", "")).split("T")[0]
        title = (entry.get("title") or "Untitled").strip()

        if url not in url_map:
            try:
                domain = urlparse(url).netloc
            except Exception:
                domain = ""
            url_map[url] = {
                "url": url,
                "title": title,
                "domain": domain,
                "keywords": entry.get("keywords", [])[:5],
                "sentiment_score": entry.get("sentiment_score", 0),
                "category": entry.get("category", ""),
                "status_code": entry.get("status_code"),
                "dates": set(),
            }
        url_map[url]["dates"].add(date_str)

    # Step 2: Group by title
    title_groups = defaultdict(list)
    for url, info in url_map.items():
        title_groups[info["title"]].append(info)

    # Get all unique dates across the dataset
    all_dates_sorted = sorted(set(d for info in url_map.values() for d in info["dates"]))

    # Step 3: For each title, sub-group URLs by date-span
    result_titles = []
    for title, url_list in title_groups.items():
        # Sub-group by date pattern
        span_buckets = defaultdict(list)
        for info in url_list:
            dates_key = tuple(sorted(info["dates"]))
            span_buckets[dates_key].append({
                "url": info["url"],
                "domain": info["domain"],
                "keywords": info["keywords"],
                "sentiment_score": info["sentiment_score"],
                "category": info["category"],
                "status_code": info["status_code"],
            })

        date_spans = []
        for dates_tuple, links in span_buckets.items():
            dates_list = list(dates_tuple)
            num_days = len(dates_list)

            if num_days == 1:
                label = f"{dates_list[0]} only"
                span_type = "single_day"
            elif dates_list == all_dates_sorted and num_days > 1:
                label = f"{dates_list[0]} → {dates_list[-1]} (all {num_days} days)"
                span_type = "full_range"
            else:
                label = " → ".join(dates_list)
                span_type = "partial"

            date_spans.append({
                "label": label,
                "dates": dates_list,
                "span_type": span_type,
                "num_days": num_days,
                "count": len(links),
                "links": links,
            })

        # Sort spans: full_range first, then partial, then single
        type_order = {"full_range": 0, "partial": 1, "single_day": 2}
        date_spans.sort(key=lambda s: (type_order.get(s["span_type"], 9), -s["num_days"], -s["count"]))

        result_titles.append({
            "title": title,
            "total_urls": len(url_list),
            "total_spans": len(date_spans),
            "date_spans": date_spans,
        })

    # Sort titles by total URLs descending
    result_titles.sort(key=lambda t: -t["total_urls"])

    return {
        "title_groups": result_titles,
        "available_dates": all_dates_sorted,
        "total_titles": len(result_titles),
        "total_urls": len(url_map),
    }


@router.get("/topic/{topic_id}/repeated")
def get_repeated_titles(topic_id: str, start: str = None, end: str = None):
    """Titles appearing across multiple days."""
    db = get_db(topic_id)
    data = load_fingerprints(db, start, end)

    if not data:
        return {"repeated": []}

    from collections import defaultdict
    title_stats = defaultdict(lambda: {
        "dates": set(), "count": 0, "sentiments": [], "urls": set()
    })

    for entry in data:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        try:
            date = str(entry.get("collected_at", "")).split("T")[0]
        except Exception:
            continue

        title_stats[title]["dates"].add(date)
        title_stats[title]["count"] += 1
        title_stats[title]["urls"].add(entry.get("url", ""))
        s = entry.get("sentiment_score", 0)
        if s is not None:
            title_stats[title]["sentiments"].append(s)

    result = []
    for title, stats in title_stats.items():
        if len(stats["dates"]) > 1:
            sorted_dates = sorted(stats["dates"])
            avg_s = sum(stats["sentiments"]) / len(stats["sentiments"]) if stats["sentiments"] else 0
            result.append({
                "title": title,
                "total_appearances": stats["count"],
                "unique_days": len(stats["dates"]),
                "unique_urls": len(stats["urls"]),
                "first_seen": sorted_dates[0],
                "last_seen": sorted_dates[-1],
                "avg_sentiment": round(avg_s, 4),
            })

    result.sort(key=lambda x: x["unique_days"], reverse=True)
    return {"repeated": result}
