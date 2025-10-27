import pandas as pd
import os
from collections import Counter
from utils import load_flattened_fingerprints

def category_stats():
    data = load_flattened_fingerprints()
    categories = []
    for item in data:
        cat = item.get("category") or "uncategorized"
        categories.append(cat)

    counter = Counter(categories)
    df = pd.DataFrame(counter.most_common(), columns=["category", "count"])

    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/category_stats.csv", index=False)
    print("[+] Category stats saved to reports/category_stats.csv")

if __name__ == "__main__":
    category_stats()
