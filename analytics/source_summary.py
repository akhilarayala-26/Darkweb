import pandas as pd
from analytics.utils import load_flattened_fingerprints

def generate_source_summary():
    data = load_flattened_fingerprints()
    if not data:
        return []

    df = pd.DataFrame(data)

    # Ensure title column exists
    if "title" not in df.columns:
        return []

    # Drop rows without titles
    df = df[df["title"].notna() & (df["title"] != "")]

    # Group by title to count occurrences (how often a title appeared)
    grouped = (
        df.groupby("title")
        .agg(
            total_entries=("url", "count"),
            unique_sources=("url", pd.Series.nunique),
            avg_sentiment=("sentiment_score", "mean")
        )
        .reset_index()
        .sort_values("total_entries", ascending=False)
    )

    # Determine trend — based on average sentiment or entry frequency
    grouped["trend"] = grouped["avg_sentiment"].apply(
        lambda x: "up" if x > 0.05 else "down" if x < -0.05 else "neutral"
    )

    # Rename to match frontend props
    result = []
    for _, row in grouped.iterrows():
        result.append({
            "source": row["title"],  # title shown in frontend as "source"
            "total_entries": int(row["total_entries"]),
            "unique_titles": int(row["unique_sources"]),
            "trend": row["trend"]
        })

    return result
