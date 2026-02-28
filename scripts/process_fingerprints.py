import hashlib
from datetime import datetime
from collections import defaultdict
import warnings
from pymongo import MongoClient
import os

uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline_c2"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")

def sha256_of_text(text):
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_index_from_scraped(scraped_data):
    index = {}
    for term, entries in scraped_data.items():
        for entry in entries:
            text_hash = entry.get("text_hash") or sha256_of_text(entry.get("raw_text", ""))
            html_hash = entry.get("html_hash") or sha256_of_text(entry.get("snippet", ""))
            record = {
                "url": entry.get("url"),
                "title": entry.get("title", ""),
                "collected_at": entry.get("collected_at"),
                "status_code": entry.get("status_code"),
                "load_time_s": entry.get("load_time_s"),
                "page_size_kb": entry.get("page_size_kb"),
                "language": entry.get("language"),
                "sentiment": entry.get("sentiment"),
                "keywords": entry.get("keywords"),
                "onion_links_outbound": entry.get("onion_links_outbound", []),
                "html_hash": html_hash,
                "text_hash": text_hash,
                "metadata": entry.get("metadata", {})
            }
            index.setdefault(text_hash, []).append(record)
    return index



def simple_keyword_classify(text):
    txt = text.lower()
    ranking = {}
    lex = {
        "drugs": ["drug", "fentanyl", "heroin", "cocaine", "meth", "weed", "opiate"],
        "weapons": ["weapon", "gun", "firearm", "explosive", "silencer"],
        "fraud": ["fraud", "scam", "phishing", "carding", "ccv"],
        "hacking": ["exploit", "vulnerability", "rce", "sql injection", "xss", "dox"],
        "leak": ["leak", "leaked", "dumps", "credentials", "database"],
        "malware": ["malware", "trojan", "ransomware", "botnet"],
        "stolen data": ["stolen", "dump", "credit card", "ssn", "credentials"],
        "marketplace": ["vendor", "market", "purchase", "escrow", "vendor fee"]
    }
    for label, toks in lex.items():
        for t in toks:
            if t in txt:
                ranking[label] = ranking.get(label, 0) + txt.count(t)
    items = sorted(ranking.items(), key=lambda x: -x[1])
    return [(k, float(v) / max(1, sum(ranking.values()))) for k, v in items]


def process_fingerprints_from_mongo():
    scraped_collection = db["data_files"]
    fingerprints_collection = db["fingerprints_data"]

    today = datetime.now().strftime("%Y-%m-%d")
    scraped_doc = scraped_collection.find_one({"_id": f"{today}_scraped"})

    if not scraped_doc:
        print(f"[!] No scraped data found for {today}")
        return

    scraped_data = scraped_doc.get("content", {})
    print(f"[*] Building fingerprint index from MongoDB scraped data ({today})...")
    index = build_index_from_scraped(scraped_data)

    # Convert to dict-based format
    content_dict = {}

    for text_hash, records in index.items():
        sample_text = ""
        if records:
            sample_text = records[0].get("title", "") + " " + " ".join(records[0].get("keywords", []))

        labels_scores = simple_keyword_classify(sample_text)

        entry_data = {
            "records": records,
            "classification": labels_scores,
            "pgp_keys": [],
            "btc_wallets": [],
            "emails": [],
            "first_seen": min(r.get("collected_at") for r in records if r.get("collected_at")),
            "last_seen": max(r.get("collected_at") for r in records if r.get("collected_at")),
        }

        content_dict[text_hash] = entry_data

    doc = {
        "_id": today,
        "content": content_dict,
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow()
    }

    fingerprints_collection.replace_one({"_id": today}, doc, upsert=True)
    print(f"[+] Inserted {len(content_dict)} fingerprint entries into MongoDB for {today}")

if __name__ == "__main__":
    process_fingerprints_from_mongo()
