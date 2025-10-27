import pandas as pd
import os
from utils import load_flattened_fingerprints

def sentiment_trends():
    data = load_flattened_fingerprints()
    if not data:
        print("[!] No data found for sentiment trends.")
        return

    df = pd.DataFrame(data)
    # ensure collected_at exists and is parsed
    df["collected_at"] = pd.to_datetime(df.get("collected_at"), errors="coerce")

    # if there are missing dates, group by file order fallback by title presence
    if df["collected_at"].notna().any():
        grouped = df.groupby(df["collected_at"].dt.date)["sentiment_score"].mean().reset_index()
        grouped.columns = ["date", "average_sentiment"]
    else:
        # fallback: single average
        grouped = pd.DataFrame([{"date": pd.Timestamp.now().date(), "average_sentiment": df["sentiment_score"].mean()}])

    os.makedirs("reports", exist_ok=True)
    grouped.to_csv("reports/sentiment_trends.csv", index=False)
    print("[+] Sentiment trends saved to reports/sentiment_trends.csv")

if __name__ == "__main__":
    sentiment_trends()
