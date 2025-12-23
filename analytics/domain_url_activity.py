import json
import os
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime
from utils import load_flattened_fingerprints



def analyze_domain_url_activity():
    data = load_flattened_fingerprints()


    if not data:
        print("❌ No fingerprint data found.")
        return

    domain_info = defaultdict(lambda: defaultdict(set))  # domain -> date -> set(urls)

    for entry in data:
        url = entry.get("url")
        collected_at = entry.get("collected_at")
        if not url or not collected_at:
            continue

        domain = urlparse(url).netloc
        date = collected_at.split("T")[0]
        domain_info[domain][date].add(url)

    # Build stats
    result = {}
    for domain, date_map in domain_info.items():
        all_urls = set()
        timeline = []
        for date, urls in sorted(date_map.items()):
            all_urls.update(urls)
            timeline.append({"date": date, "urls": list(urls)})

        url_change_count = sum(
            len(urls) for urls in date_map.values()
        ) - len(set.union(*date_map.values()))
        first_seen = min(date_map.keys())
        last_seen = max(date_map.keys())
        frequency = len(date_map)

        result[domain] = {
            "unique_urls": len(all_urls),
            "total_url_changes": max(url_change_count, 0),
            "active_days": frequency,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "timeline": timeline,
        }

    os.makedirs("reports", exist_ok=True)
    print("hlo")
    output_path = os.path.join("reports", f"domain_url_activity_{datetime.now().strftime('%Y-%m-%d')}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"[+] Domain URL activity report saved to {output_path}")


def main():
    print("=== Domain URL Activity Analysis ===")
    analyze_domain_url_activity()
    print("✅ Completed domain URL activity analysis.\n")


if __name__ == "__main__":
    main()
