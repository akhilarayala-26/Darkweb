import pandas as pd
import os
import json
from collections import Counter
from analytics.utils import load_flattened_fingerprints # updated to use DB version

def keyword_trends(top_n=30):
    """Generate keyword frequency trends and save to a JSON file."""
    data = load_flattened_fingerprints()
    all_keywords = []
    
    for item in data:
        kws = item.get("keywords") or []
        for kw in kws:
            if isinstance(kw, str):
                all_keywords.append(kw.lower())

    counter = Counter(all_keywords)
    top_keywords = counter.most_common(top_n)

    trends = [{"keyword": k, "count": c} for k, c in top_keywords]

    os.makedirs("reports", exist_ok=True)
    output_path = "reports/keyword_trends.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trends, f, indent=4, ensure_ascii=False)

    print(f"[+] Keyword trends saved to {output_path}")
    return trends

if __name__ == "__main__":
    keyword_trends()
