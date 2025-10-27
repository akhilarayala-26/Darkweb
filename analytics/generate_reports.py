import json
import os
from datetime import datetime
from urllib.parse import urlparse
from utils import load_flattened_fingerprints
import pandas as pd

def generate_summary(data):
    total_pages = len(data)
    languages = {}
    for item in data:
        lang = item.get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1

    avg_sentiment = sum([item.get("sentiment_score", 0) for item in data]) / max(total_pages, 1)

    return {
        "timestamp": datetime.now().isoformat(),
        "total_pages": total_pages,
        "languages": languages,
        "average_sentiment": avg_sentiment
    }

def generate_daily_trends(data):
    df = pd.DataFrame(data)
    df["collected_at"] = pd.to_datetime(df.get("collected_at"), errors="coerce")

    # extract date and domain
    df["date"] = df["collected_at"].dt.date
    df["domain"] = df["url"].apply(lambda u: urlparse(u).netloc if isinstance(u, str) else "")

    daily_summary = (
        df.groupby("date")
        .agg(
            pages=("url", "count"),
            unique_domains=("domain", pd.Series.nunique),
            avg_sentiment=("sentiment_score", "mean")
        )
        .reset_index()
        .sort_values("date")
    )

    trends = []
    for _, row in daily_summary.iterrows():
        trends.append({
            "date": str(row["date"]),
            "pages": int(row["pages"]),
            "unique_domains": int(row["unique_domains"]),
            "average_sentiment": round(float(row["avg_sentiment"]), 3)
        })

    return trends

def main():
    data = load_flattened_fingerprints()
    summary = generate_summary(data)
    trends = generate_daily_trends(data)

    summary["daily_trends"] = trends

    os.makedirs("reports", exist_ok=True)
    output_path = os.path.join("reports", f"summary_{datetime.now().strftime('%Y-%m-%d')}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    print(f"[+] Summary report saved to {output_path}\n")

    # Pretty console output
    print("📈 Day-to-Day Trend:")
    for t in trends:
        print(f"{t['date']} → {t['pages']} pages, {t['unique_domains']} unique domains, "
              f"avg sentiment {t['average_sentiment']}")

if __name__ == "__main__":
    main()
