from urllib.parse import urlparse
from datetime import datetime
from collections import defaultdict
from analytics.utils import load_flattened_fingerprints  # import your existing loader

def get_domain(url: str):
    """Extract the domain (without scheme or path) from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None

def group_unique_domains_by_day():
    """
    Group unique domains by collection date.
    Returns a dict: { 'YYYY-MM-DD': { 'domain': [record_details, ...], ... }, ... }
    """
    records = load_flattened_fingerprints()
    grouped_data = defaultdict(lambda: defaultdict(list))

    for rec in records:
        url = rec.get("url")
        collected_at = rec.get("collected_at")
        title = rec.get("title", "Untitled")

        if not url or not collected_at:
            continue

        domain = get_domain(url)
        if not domain:
            continue

        # Normalize date to YYYY-MM-DD
        try:
            date_key = datetime.fromisoformat(collected_at.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            continue

        # Use title as a basic identifier for uniqueness within the domain/day
        existing_titles = [item.get("title") for item in grouped_data[date_key][domain]]
        if title not in existing_titles:
            grouped_data[date_key][domain].append({
                "title": rec.get("title"),
                "language": rec.get("language"),
                "sentiment_score": rec.get("sentiment_score"),
                "category": rec.get("category"),
                "keywords": rec.get("keywords"),
                "status_code": rec.get("status_code"),
                "load_time_s": rec.get("load_time_s"),
                "page_size_kb": rec.get("page_size_kb"),
                "onion_links_outbound": rec.get("onion_links_outbound"),
                "classification": rec.get("classification"),
                "first_seen": rec.get("first_seen"),
                "last_seen": rec.get("last_seen"),
            })

    print(f"[+] Grouped unique domains for {len(grouped_data)} days.")
    return grouped_data


if __name__ == "__main__":
    result = group_unique_domains_by_day()
    
    # Example: print summary of each day
    for date, domains in result.items():
        print(f"\n📅 Date: {date}")
        print(f"   Total unique domains: {len(domains)}")
        for domain, details in domains.items():
            print(f"   - {domain} ({len(details)} pages)")
            for item in details[:2]:  # show preview of first two entries per domain
                print(f"       → {item['title']}")
