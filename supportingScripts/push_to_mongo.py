import json, os, re
from datetime import datetime
from db.mongo_client import db
from datetime import datetime, timezone
DATA_FOLDERS = {
    "links": "links",
    "data": "data",
    "fingerprints": "fingerprints",
    "grouped_titles": "grouped_titles",

}

def push_one_file(category, folder, filename):
    match = re.search(r"_(\d{4}-\d{2}-\d{2})", filename)
    if not match:
        return
    date = match.group(1)
    filepath = os.path.join(folder, filename)

    with open(filepath, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Skipping invalid JSON: {filename}")
            return

    collection = db[category]
    document_id = f"{category}_{date}"

    result = collection.update_one(
        {"_id": document_id},
        {
            "$set": {
                "data": data,
                "category": category,
                "date": date
            },
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
            "$currentDate": {"last_updated": True}
        },
        upsert=True
    )

    if result.upserted_id or result.modified_count > 0:
        print(f"✅ Uploaded {filename} → {category}/{document_id}")
    else:
        print(f"⚠️ Skipped {filename} (no changes).")

def main():
    print("🚀 Pushing local JSON data to MongoDB...")
    for category, folder in DATA_FOLDERS.items():
        if not os.path.exists(folder):
            print(f"⚠️ Folder not found: {folder}")
            continue
        for filename in sorted(os.listdir(folder)):
            if filename.endswith(".json"):
                push_one_file(category, folder, filename)
    print("\n🎯 MongoDB sync completed successfully!")

if __name__ == "__main__":
    main()