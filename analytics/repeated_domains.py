import os
import json
import pandas as pd
from urllib.parse import urlparse
from utils import load_flattened_fingerprints

def repeated_domains_analysis():
    data = load_flattened_fingerprints()
    df = pd.DataFrame(data)

    # Clean and prepare
    df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")
    df["date"] = df["collected_at"].dt.date
    df["domain"] = df["url"].apply(lambda u: urlparse(u).netloc if isinstance(u, str) else None)

    df = df.dropna(subset=["domain", "date"])

    # Group by domain to see on how many unique days it appeared
    domain_stats = (
        df.groupby("domain")
        .agg(
            total_appearances=("date", "count"),
            unique_days=("date", pd.Series.nunique),
            first_seen=("date", "min"),
            last_seen=("date", "max"),
            avg_sentiment=("sentiment_score", "mean")
        )
        .reset_index()
        .sort_values(by="unique_days", ascending=False)
    )

    os.makedirs("reports", exist_ok=True)
    csv_path = "reports/repeated_domains.csv"
    json_path = "reports/repeated_domains.json"

    domain_stats.to_csv(csv_path, index=False)

    # Convert to JSON for richer data export
    domain_stats.to_json(json_path, orient="records", indent=4, date_format="iso")

    print(f"[+] Repeated domain analytics saved to:")
    print(f"    • {csv_path}")
    print(f"    • {json_path}")

    # Print top recurring domains
    print("\n🏆 Top Persistent Domains:")
    for _, row in domain_stats.head(10).iterrows():
        print(f"{row['domain']}: seen {row['unique_days']} days "
              f"(first: {row['first_seen']}, last: {row['last_seen']})")

if __name__ == "__main__":
    repeated_domains_analysis()
