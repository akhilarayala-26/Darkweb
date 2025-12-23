import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse, parse_qs, unquote, quote_plus
from datetime import datetime, timezone
from pymongo import MongoClient
import os

# ==============================
# ✅ CONFIGURATION
# ==============================
SEARCH_TERMS = ["drugs forum"]
TOKEN = "&5f83bc=a0d126"
MAX_LINKS = 800  # limit total links

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://ahmia.fi/",
    "Accept-Language": "en-US,en;q=0.9"
}

# ==============================
# ✅ MONGO CONNECTION
# ==============================
uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline"]
collection = db["links_data"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")
print(f"[MongoDB] Collection: {collection.name}")


# ==============================
# 🔍 LINK COLLECTION
# ==============================
def collect_links():
    results = {}
    total_links = 0

    for term in SEARCH_TERMS:
        if total_links >= MAX_LINKS:
            print(f"[!] Reached maximum limit of {MAX_LINKS} links. Stopping search.")
            break

        print(f"[*] Searching for: {term}")
        query = quote_plus(term)
        url = f"https://ahmia.fi/search/?q={query}{TOKEN}"

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] Request failed for {term}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        onion_links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            if "/search/redirect?" in href:
                parsed = urlparse(href)
                query_params = parse_qs(parsed.query)
                if "redirect_url" in query_params:
                    onion_url = unquote(query_params["redirect_url"][0])
                    if ".onion" in onion_url:
                        onion_links.add(onion_url)
            elif ".onion" in href:
                onion_links.add(href)

            # Stop if we hit total limit
            if total_links + len(onion_links) >= MAX_LINKS:
                break

        links_for_term = list(onion_links)
        remaining_capacity = MAX_LINKS - total_links
        if len(links_for_term) > remaining_capacity:
            links_for_term = links_for_term[:remaining_capacity]

        total_links += len(links_for_term)
        print(f"  [+] Found {len(links_for_term)} links for '{term}' (Total so far: {total_links})")
        results[term] = links_for_term

        if total_links >= MAX_LINKS:
            print(f"[!] Reached the maximum limit of {MAX_LINKS} links.")
            break

        time.sleep(2)  # polite delay between searches

    if not any(results.values()):
        print("[!] No links found. The Ahmia token may have changed.")
        return None

    today = datetime.now().strftime("%Y-%m-%d")

    # ==============================
    # 💾 STORE DIRECTLY IN MONGODB
    # ==============================
    doc_data = {
        "_id": today,
        "content": results,
        "created_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc)
    }

    print(f"[MongoDB] Writing up to {MAX_LINKS} links for {today}")

    res = collection.update_one(
        {"_id": today},
        {
            "$set": {
                "content": results,
                "last_updated": datetime.now(timezone.utc)
            },
            "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
        },
        upsert=True
    )

    doc = collection.find_one({"_id": today})
    print("[MongoDB] Document after update:", json.dumps(doc, default=str, indent=2))

    if res.upserted_id:
        print(f"✅ Inserted new document for {today}")
    elif res.modified_count:
        print(f"🔁 Updated existing document for {today}")
    else:
        print(f"⚠️ No changes for {today}")


if __name__ == "__main__":
    collect_links()
