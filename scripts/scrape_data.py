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

DetectorFactory.seed = 0

# MongoDB Connection
uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline_c1"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")

# Tor Proxy
PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# Regex Patterns
PGP_KEY_PATTERN = re.compile(r'-----BEGIN PGP PUBLIC KEY BLOCK-----.*?-----END PGP PUBLIC KEY BLOCK-----', re.DOTALL)
BITCOIN_WALLET_PATTERN = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
ONION_LINK_PATTERN = re.compile(r'\b[a-z2-7]{16}\.onion\b|\b[a-z2-7]{56}\.onion\b')

# ==============================
# 🔧 Helper Functions
# ==============================
def html_sha256(html_text):
    return hashlib.sha256(html_text.encode('utf-8')).hexdigest()

def text_sha256(text):
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def extract_metadata_from_text(text):
    return {
        "pgp_keys": PGP_KEY_PATTERN.findall(text),
        "btc_wallets": BITCOIN_WALLET_PATTERN.findall(text),
        "emails": EMAIL_PATTERN.findall(text),
    }

def extract_onion_links(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    links = set()
    for a in soup.find_all('a', href=True):
        if ".onion" in a['href']:
            links.add(a['href'])
    for match in ONION_LINK_PATTERN.findall(html_text):
        links.add(match)
    return list(links)

def extract_handles_and_social(html_text):
    handles = {"telegram": [], "x": [], "discord": []}
    for t in re.findall(r'(?:t\.me\/[A-Za-z0-9_]+)|@([A-Za-z0-9_]{4,})', html_text):
        if t:
            handles["telegram"].append(t if t.startswith("t.me") else f"@{t}")
    for t in re.findall(r'(?:twitter\.com\/[A-Za-z0-9_]+)|@([A-Za-z0-9_]{4,})', html_text):
        if t:
            handles["x"].append(t if t.startswith("twitter.com") else f"@{t}")
    for d in re.findall(r'(?:discord\.gg\/[A-Za-z0-9]+)|discord(app)?\.com\/invite\/[A-Za-z0-9]+', html_text):
        handles["discord"].append(d)
    return handles

def rake_keywords(text, max_words=10):
    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases()[:max_words]

def simple_keyword_summary(text, top_n=10):
    words = re.findall(r'\w{4,}', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:top_n]
    return [w for w, _ in top]

# ==============================
# 🕸️ Scraper Logic
# ==============================
def scrape_single(url, timeout=90):
    try:
        start = time.time()
        response = requests.get(url, proxies=PROXIES, timeout=timeout)
        elapsed = time.time() - start

        if response.status_code != 200:
            return None, f"Failed ({response.status_code}) {url}"

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
        text_content = " ".join(soup.stripped_strings)
        snippet = text_content[:2000]
        word_count = len(re.findall(r'\w+', text_content))

        try:
            language = detect(text_content) if text_content.strip() else "unknown"
        except Exception:
            language = "unknown"

        try:
            tb = TextBlob(snippet)
            sentiment = {
                "polarity": round(tb.sentiment.polarity, 4),
                "subjectivity": round(tb.sentiment.subjectivity, 4)
            }
        except Exception:
            sentiment = {"polarity": 0.0, "subjectivity": 0.0}

        try:
            keywords_rake = rake_keywords(text_content, max_words=12)
        except Exception:
            keywords_rake = simple_keyword_summary(text_content, top_n=12)

        metadata = extract_metadata_from_text(text_content)
        handles = extract_handles_and_social(html)
        onion_links_outbound = extract_onion_links(html)

        record = {
            "url": url,
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "title": title,
            "status_code": response.status_code,
            "load_time_s": round(elapsed, 3),
            "page_size_kb": round(len(response.content) / 1024.0, 2),
            "word_count": word_count,
            "language": language,
            "sentiment": sentiment,
            "keywords": keywords_rake,
            "snippet": snippet,
            "raw_text": text_content,
            "html_hash": html_sha256(html),
            "text_hash": text_sha256(text_content),
            "metadata": metadata,
            "social_handles": handles,
            "onion_links_outbound": onion_links_outbound
        }
        return record, None

    except Exception as e:
        return None, f"Error {url}: {e}"

# ==============================
# 🚀 Main Function
# ==============================
def scrape_data(max_workers=5):
    today = datetime.now().strftime("%Y-%m-%d")
    links_doc = db.links_data.find_one({"_id": today})

    if not links_doc:
        print(f"[!] No links found in DB for {today}")
        return

    links_data = links_doc.get("content", {})
    scraped_data = {}
    failed_urls = []

    total_links = sum(len(v) for v in links_data.values())
    success_count = fail_count = 0

    print(f"\n🔍 Starting scrape for {total_links} links...\n")
    for term, urls in links_data.items():
        scraped_data[term] = []
        print(f"[*] Scraping {len(urls)} links for '{term}'")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_single, url): url for url in urls}
            for i, future in enumerate(as_completed(futures), 1):
                print(f"    -> Progress: {i}/{len(urls)}", end='\r')
                result, error = future.result()
                if result:
                    scraped_data[term].append(result)
                    success_count += 1
                else:
                    failed_urls.append(error)
                    fail_count += 1
        print("\n")

    now = datetime.now(timezone.utc)

    # Store scraped results
    db.data_files.update_one(
        {"_id": f"{today}_scraped"},
        {
            "$set": {
                "date": today,
                "type": "scraped",
                "content": scraped_data
            },
            "$setOnInsert": {"created_at": now},
            "$currentDate": {"last_updated": True}
        },
        upsert=True
    )

    # Store failed URLs separately
    db.data_files.update_one(
        {"_id": f"{today}_failed"},
        {
            "$set": {
                "date": today,
                "type": "failed",
                "content": failed_urls
            },
            "$setOnInsert": {"created_at": now},
            "$currentDate": {"last_updated": True}
        },
        upsert=True
    )

    print("\n==== SCRAPING COMPLETE ====")
    print(f"Total links: {total_links}")
    print(f"✅ Successfully scraped: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📁 Saved as: {today}_scraped and {today}_failed in MongoDB")


if __name__ == "__main__":
    scrape_data()
