import pandas as pd
import os
from urllib.parse import urlparse
from collections import Counter
from utils import load_flattened_fingerprints

def domain_activity(top_n=100):
    data = load_flattened_fingerprints()
    domains = []
    for item in data:
        url = item.get("url")
        if not url:
            continue
        try:
            netloc = urlparse(url).netloc
        except Exception:
            netloc = url
        if netloc:
            domains.append(netloc)

    counter = Counter(domains)
    df = pd.DataFrame(counter.most_common(top_n), columns=["domain", "activity_count"])

    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/domain_activity.csv", index=False)
    print("[+] Domain activity saved to reports/domain_activity.csv")

if __name__ == "__main__":
    domain_activity()
