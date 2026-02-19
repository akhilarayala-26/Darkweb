import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urlparse, parse_qs, unquote, quote_plus
from datetime import datetime, timezone
from pymongo import MongoClient
import os

# ==============================
# ✅ CONFIGURATION
# ==============================
SEARCH_TERMS = ["credit card"]
#SEARCH_TERMS = ["weapons"]
MAX_LINKS = 800

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
uri = os.getenv(
    "MONGO_URI",
    "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone"
)

client = MongoClient(uri)
db = client["darkweb_pipeline_c1"]
collection = db["links_data"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")
print(f"[MongoDB] Collection: {collection.name}")

# ==============================
# 🔐 TOKEN FETCHER (AUTO)
# ==============================
def fetch_ahmia_token():
    print("[*] Fetching fresh Ahmia token...")
    url = "https://ahmia.fi/search/"

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print("[!] Failed to fetch Ahmia base page:", e)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")

    for inp in soup.find_all("input", type="hidden"):
        name = inp.get("name")
        value = inp.get("value")
        if name and value and len(name) == 6 and len(value) == 6:
            token = f"&{name}={value}"
            print("[+] Token extracted:", token)
            return token

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "&" in href and "=" in href:
            for part in href.split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    if len(k) == 6 and len(v) == 6:
                        token = f"&{k}={v}"
                        print("[+] Token extracted from link:", token)
                        return token

    print("[!] Token not found — Ahmia structure may have changed")
    return ""

# ==============================
# 🔍 LINK COLLECTION
# ==============================
def collect_links():
    token = fetch_ahmia_token()
    if not token:
        print("[!] Aborting — No token available")
        return

    results = {}
    total_links = 0

    for term in SEARCH_TERMS:
        if total_links >= MAX_LINKS:
            break

        print(f"[*] Searching for: {term}")
        query = quote_plus(term)
        url = f"https://ahmia.fi/search/?q={query}{token}"

        response = None
        for attempt in range(1, 4):
            try:
                response = requests.get(url, headers=HEADERS, timeout=45)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                print(f"[!] Attempt {attempt}/3 failed for {term}: {e}")
                if attempt < 3:
                    wait = attempt * 5
                    print(f"    Retrying in {wait}s...")
                    time.sleep(wait)
        if response is None or response.status_code != 200:
            print(f"[!] All attempts failed for {term}, skipping.")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        onion_links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if "/search/redirect?" in href:
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                if "redirect_url" in qs:
                    onion_url = unquote(qs["redirect_url"][0])
                    if ".onion" in onion_url:
                        onion_links.add(onion_url)

            elif ".onion" in href:
                onion_links.add(href)

            if total_links + len(onion_links) >= MAX_LINKS:
                break

        links = list(onion_links)
        capacity = MAX_LINKS - total_links
        links = links[:capacity]

        results[term] = links
        total_links += len(links)

        print(f"  [+] Found {len(links)} links (Total: {total_links})")

        time.sleep(random.uniform(2.5, 5.0))

    if not any(results.values()):
        print("[!] No links found — token likely invalidated")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    print(f"[MongoDB] Writing data for {today}")

    res = collection.update_one(
        {"_id": today},
        {
            "$set": {
                "content": results,
                "last_updated": datetime.now(timezone.utc)
            },
            "$setOnInsert": {
                "created_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    doc = collection.find_one({"_id": today})
    print("[MongoDB] Stored document:")
    print(json.dumps(doc, default=str, indent=2))

    if res.upserted_id:
        print(f"✅ Inserted new document for {today}")
    elif res.modified_count:
        print(f"🔁 Updated existing document for {today}")
    else:
        print("⚠️ No changes detected")

# ==============================
# 🚀 ENTRY POINT
# ==============================
if __name__ == "__main__":
    collect_links()
