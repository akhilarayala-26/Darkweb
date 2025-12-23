import os
import json
import pandas as pd
from analytics.utils import load_flattened_fingerprints

def repeated_domains_analysis():
    """Analyze repeated titles (instead of domains) across multiple days."""
    data = load_flattened_fingerprints()
    if not data:
        print("[!] No data found.")
        return []

    df = pd.DataFrame(data)

    if "collected_at" not in df or "title" not in df:
        print("[!] Missing 'collected_at' or 'title' fields.")
        return []

    df["collected_at"] = pd.to_datetime(df["collected_at"], errors="coerce")
    df["date"] = df["collected_at"].dt.date

    df = df.dropna(subset=["title", "date"])
    df["title"] = df["title"].str.strip()

    if df.empty:
        print("[!] No valid title data.")
        return []

    # Group by title to find repeated appearances
    title_stats = (
        df.groupby("title")
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

    # Filter titles that appeared on more than one day
    repeated_titles = title_stats[title_stats["unique_days"] > 1]

    os.makedirs("reports", exist_ok=True)
    json_path = "reports/repeated_titles.json"

    repeated_titles.to_json(json_path, orient="records", indent=4, date_format="iso")

    result = repeated_titles.to_dict(orient="records")

    print(f"[+] Repeated titles analytics saved to {json_path} ({len(result)} titles found)")
    return result

if __name__ == "__main__":
    repeated_domains_analysis()
