import os
import json
from collections import defaultdict
from datetime import datetime
from pymongo import MongoClient

uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")


def group_links_by_title_from_db():
    """Group URLs by title from MongoDB fingerprints_data (dict-based)."""
    collection = db["fingerprints_data"]
    fingerprints = collection.find({})

    title_to_urls = defaultdict(set)

    for doc in fingerprints:
        content = doc.get("content", {})
        for entry_data in content.values():
            records = entry_data.get("records", [])
            for rec in records:
                title = rec.get("title", "").strip()
                url = rec.get("url", "").strip()
                if title and url:
                    title_to_urls[title].add(url)

    grouped = {
        title: list(urls)
        for title, urls in title_to_urls.items()
        if len(urls) > 1
    }
    return grouped


def save_grouped_titles(grouped_links, output_folder="grouped_titles"):
    """Save grouped title data into JSON and MongoDB (grouped_titles_data)."""
    os.makedirs(output_folder, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(output_folder, f"grouped_titles_{today}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(grouped_links, f, indent=4, ensure_ascii=False)

    print(f"[+] Grouped titles saved to {output_path}")

    grouped_collection = db["grouped_titles_data"]

    doc = {
        "_id": today,
        "content": grouped_links,
        "total_groups": len(grouped_links),
        "created_at": datetime.utcnow(),
        "last_updated": datetime.utcnow()
    }

    grouped_collection.replace_one({"_id": today}, doc, upsert=True)
    print(f"[+] Inserted {len(grouped_links)} grouped titles into MongoDB for {today}.")

    return output_path


if __name__ == "__main__":
    grouped = group_links_by_title_from_db()
    save_grouped_titles(grouped)
