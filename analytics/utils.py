import json
import os

def load_flattened_fingerprints(folder="fingerprints"):
    """
    Load all fingerprint JSONs from `folder` and return a flat list of records.
    Each record is a dict with fields: url, title, language, sentiment_score, category, keywords, collected_at.
    """
    all_entries = []
    if not os.path.isdir(folder):
        return all_entries

    for file in sorted(os.listdir(folder)):
        if not file.endswith(".json"):
            continue
        path = os.path.join(folder, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        # data expected to be dict: {hash: { "text_hash":..., "records": [...] }, ...}
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, dict):
                    records = v.get("records", [])
                    if isinstance(records, list):
                        for rec in records:
                            entry = {
                                "url": rec.get("url"),
                                "title": rec.get("title"),
                                "language": rec.get("language", "unknown"),
                                "sentiment_score": rec.get("sentiment", {}).get("polarity", 0) if isinstance(rec.get("sentiment"), dict) else 0,
                                "category": rec.get("category", "uncategorized"),
                                "keywords": rec.get("keywords", []),
                                "collected_at": rec.get("collected_at")
                            }
                            all_entries.append(entry)
        # support legacy flat-list JSONs
        elif isinstance(data, list):
            for rec in data:
                if isinstance(rec, dict):
                    entry = {
                        "url": rec.get("url"),
                        "title": rec.get("title"),
                        "language": rec.get("language", "unknown"),
                        "sentiment_score": rec.get("sentiment", {}).get("polarity", 0) if isinstance(rec.get("sentiment"), dict) else 0,
                        "category": rec.get("category", "uncategorized"),
                        "keywords": rec.get("keywords", []),
                        "collected_at": rec.get("collected_at")
                    }
                    all_entries.append(entry)
    return all_entries
