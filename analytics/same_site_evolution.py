import json
import os
from urllib.parse import urlparse
from collections import defaultdict
from datetime import datetime
from utils import load_flattened_fingerprints

def analyze_site_evolution():
    data = load_flattened_fingerprints()

    if not data:
        print("❌ No fingerprint data found.")
        return

    title_to_domains = defaultdict(lambda: defaultdict(list))

    for entry in data:
        url = entry.get("url")
        title = entry.get("title", "").strip()
        collected_at = entry.get("collected_at")

        if not url or not collected_at or not title:
            continue

        domain = urlparse(url).netloc
        date = collected_at.split("T")[0]
        title_to_domains[title][domain].append(date)

    result = {}

    for title, domains in title_to_domains.items():
        domain_list = []
        all_dates = set()
        for domain, dates in domains.items():
            first_seen = min(dates)
            last_seen = max(dates)
            all_dates.update(dates)
            domain_list.append({
                "domain": domain,
                "first_seen": first_seen,
                "last_seen": last_seen
            })

        result[title] = {
            "domains": sorted(domain_list, key=lambda d: d["first_seen"]),
            "total_domains": len(domain_list),
            "active_days": len(all_dates)
        }

    os.makedirs("reports", exist_ok=True)
    output_path = os.path.join(
        "reports",
        f"same_site_evolution_{datetime.now().strftime('%Y-%m-%d')}.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"[+] Site evolution report saved to {output_path}")


def main():
    print("=== Site Evolution Analysis ===")
    analyze_site_evolution()
    print("✅ Completed analysis.\n")


if __name__ == "__main__":
    main()
