import pandas as pd
import os
from collections import Counter
from utils import load_flattened_fingerprints

def keyword_trends(top_n=30):
    data = load_flattened_fingerprints()
    all_keywords = []
    for item in data:
        kws = item.get("keywords") or []
        for kw in kws:
            if isinstance(kw, str):
                all_keywords.append(kw.lower())

    counter = Counter(all_keywords)
    df = pd.DataFrame(counter.most_common(top_n), columns=["keyword", "count"])

    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/keyword_trends.csv", index=False)
    print("[+] Keyword trends saved to reports/keyword_trends.csv")

if __name__ == "__main__":
    keyword_trends()
