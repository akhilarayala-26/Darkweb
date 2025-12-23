
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import hashlib
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from langdetect import detect, DetectorFactory
from textblob import TextBlob
from rake_nltk import Rake
from pymongo import MongoClient
import os

uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")

def split_yesterdays_data():
    collection = db["data_files"]

    # Date you want to split
    date_str = "2025-10-29"
    doc_id = f"{date_str}_scraped"

    # Get the combined doc
    doc = collection.find_one({"_id": doc_id})
    if not doc:
        print(f"No document found with _id {doc_id}")
        return

    content = doc.get("content", {})
    scraped_data = content.get("drugs forum", [])
    failed_data = content.get("failed", [])

    # Remove old combined doc
    collection.delete_one({"_id": doc_id})

    # New 'scraped' doc
    scraped_doc = {
        "_id": f"{date_str}_scraped",
        "content": {"drugs forum": scraped_data},
        "created_at": doc.get("created_at", datetime.utcnow()),
        "date": date_str,
        "last_updated": datetime.utcnow(),
        "type": "scraped"
    }

    # New 'failed' doc
    failed_doc = {
        "_id": f"{date_str}_failed",
        "content": failed_data,
        "created_at": doc.get("created_at", datetime.utcnow()),
        "date": date_str,
        "last_updated": datetime.utcnow(),
        "type": "failed"
    }

    # Insert both new docs
    collection.insert_many([scraped_doc, failed_doc])

    print(f"✅ Split completed for {date_str}: created '{date_str}_scraped' and '{date_str}_failed'")

if __name__ == "__main__":
    split_yesterdays_data()
