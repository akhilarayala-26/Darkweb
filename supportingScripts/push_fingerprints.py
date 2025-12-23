#!/usr/bin/env python3
"""
push_fingerprints.py

Pushes each JSON file from the "fingerprints/" folder into MongoDB.
Each document will have:
  _id: <date>              # e.g. "2025-10-18"
  content: <file content>  # JSON content as-is
  created_at, last_updated
"""

import os
import json
import re
from datetime import datetime, timezone
from pymongo import MongoClient

# Try using existing connection if available
try:
    from db.mongo_client import db
except Exception:
    try:
        from db_connection import db
    except Exception:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(uri)
        db = client["darkweb_pipeline"]

FOLDER = "fingerprints"
COLLECTION_NAME = "fingerprints_data"
collection = db[COLLECTION_NAME]


def extract_date(filename: str):
    """Extracts YYYY-MM-DD from filename like fingerprints_2025-10-18.json"""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return match.group(1) if match else None


def push_file(filepath: str, filename: str):
    date = extract_date(filename)
    if not date:
        print(f"⚠️  Skipping {filename} (no valid date found)")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return

    update = {
        "$set": {"content": content},
        "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
        "$currentDate": {"last_updated": True},
    }

    res = collection.update_one({"_id": date}, update, upsert=True)
    if res.upserted_id:
        print(f"✅ Inserted: {filename} as _id={date}")
    elif res.modified_count:
        print(f"🔁 Updated: {filename} (_id={date})")
    else:
        print(f"⚠️ No changes for {filename} (_id={date})")


def main():
    if not os.path.isdir(FOLDER):
        print(f"❌ Folder not found: {FOLDER}")
        return

    json_files = [f for f in os.listdir(FOLDER) if f.endswith(".json")]
    if not json_files:
        print(f"⚠️ No JSON files found in {FOLDER}")
        return

    for file in sorted(json_files):
        path = os.path.join(FOLDER, file)
        push_file(path, file)

    print("\n🎯 Done pushing fingerprints to MongoDB.")


if __name__ == "__main__":
    main()
