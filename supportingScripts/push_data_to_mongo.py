
# MongoDB connection
 # or replace with your existing connection script
#!/usr/bin/env python3
"""
push_data_by_date.py

Reads JSON files from the local "data/" folder and upserts one MongoDB document per file.
Document _id will include the date and type (e.g. "2025-10-22_scraped") so files with the
same date but different types (scraped / failed) become separate documents. Each document
also contains fields:
  - date: "YYYY-MM-DD"
  - type: "scraped" | "failed" | "<other>"
  - content: <original JSON content>
  - created_at, last_updated

This produces N docs = number of files (e.g. 9 dates × 2 types => 18 docs).
"""

import os
import json
import re
from datetime import datetime, timezone
from pymongo import UpdateOne

# Try importing existing DB connection (adjust path if yours differs)
try:
    # common place based on our conversation
    from db.mongo_client import db
except Exception:
    try:
        # alternate fallback name if you placed it at project root as db_connection.py
        from db_connection import db
    except Exception:
        # As a last fallback, try environment MONGO_URI
        from pymongo import MongoClient
        import os as _os
        uri = _os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(uri)
        db = client["darkweb_pipeline"]

DATA_FOLDER = "data"
COLLECTION_NAME = "data_files"  # collection to store these file-documents
collection = db[COLLECTION_NAME]

def extract_date_and_type(filename: str):
    """
    From filename like:
      - scraped_2025-10-22.json
      - failed_2025-10-22.json
    return (date_str, type_str) or (None, None) if no date found.
    """
    # find date pattern YYYY-MM-DD
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if not m:
        return None, None
    date = m.group(1)

    # type is the prefix before underscore (if exists)
    prefix = filename.split("_")[0].lower()
    # normalize known types
    if prefix in ("scraped", "failed", "links", "fingerprints", "grouped", "report", "reports"):
        kind = prefix
    else:
        # fallback: anything else treat as 'other'
        kind = prefix if prefix else "other"

    return date, kind

def push_file(filepath: str, filename: str):
    date, kind = extract_date_and_type(filename)
    if not date:
        print(f"⚠️  Skipping (no date found): {filename}")
        return

    # create document id so multiple docs per date are possible:
    # includes date + kind -> ensures unique doc per file type per date
    doc_id = f"{date}_{kind}"

    # Load JSON content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load JSON {filename}: {e}")
        return

    update = {
        "$set": {
            "date": date,
            "type": kind,
            "content": content
        },
        "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
        "$currentDate": {"last_updated": True}
    }

    res = collection.update_one({"_id": doc_id}, update, upsert=True)
    if res.upserted_id:
        print(f"✅ Inserted: {doc_id}")
    elif res.modified_count:
        print(f"🔁 Updated: {doc_id}")
    else:
        print(f"⚠️ No-op (no changes) for: {doc_id}")

def main():
    if not os.path.isdir(DATA_FOLDER):
        print(f"❌ Data folder not found: {DATA_FOLDER}")
        return

    files = sorted(os.listdir(DATA_FOLDER))
    json_files = [f for f in files if f.lower().endswith(".json")]

    if not json_files:
        print(f"⚠️ No JSON files found in {DATA_FOLDER}")
        return

    for fn in json_files:
        path = os.path.join(DATA_FOLDER, fn)
        push_file(path, fn)

    print("\n🎯 Done. All files processed.")

if __name__ == "__main__":
    main()
