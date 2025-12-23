from pymongo import MongoClient
import os

def load_flattened_fingerprints():
    """
    Load and flatten all fingerprints from MongoDB 'fingerprints_data' collection.
    Returns a list of dicts similar to the old file-based loader:
    [{url, title, language, sentiment_score, category, keywords, collected_at, ...}, ...]
    """
    uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
    client = MongoClient(uri)
    db = client["darkweb_pipeline"]
    collection = db["fingerprints_data"]

    all_entries = []

    for doc in collection.find({}, {"_id": 1, "content": 1}):
        doc_date = doc.get("_id")
        content = doc.get("content", {})

        if isinstance(content, dict):
            for hash_key, item in content.items():
                if isinstance(item, dict):
                    records = item.get("records", [])
                    classification = item.get("classification", [])
                    pgp_keys = item.get("pgp_keys", [])
                    btc_wallets = item.get("btc_wallets", [])
                    emails = item.get("emails", [])


                    if isinstance(records, list):
                        for rec in records:
                            entry = {
                                "url": rec.get("url"),
                                "title": rec.get("title"),
                                "language": rec.get("language", "unknown"),
                                "sentiment_score": rec.get("sentiment", {}).get("polarity", 0)
                                    if isinstance(rec.get("sentiment"), dict) else 0,
                                "category": rec.get("category", "uncategorized"),
                                "keywords": rec.get("keywords", []),
                                "collected_at": rec.get("collected_at") or doc_date,

                                # Added new attributes
                                "status_code": rec.get("status_code"),
                                "load_time_s": rec.get("load_time_s"),
                                "page_size_kb": rec.get("page_size_kb"),
                                "onion_links_outbound": rec.get("onion_links_outbound", []),

                                "metadata": rec.get("metadata", {}),
                                "classification": classification,
                                "pgp_keys": pgp_keys,
                                "btc_wallets": btc_wallets,
                                "emails": emails,

                            }
                            all_entries.append(entry)

    print(f"[+] Loaded {len(all_entries)} fingerprint records from MongoDB.")
    return all_entries

if __name__ == "__main__":
    records = load_flattened_fingerprints()
    print(f"Total records fetched: {len(records)}")
    print(records[:2])
