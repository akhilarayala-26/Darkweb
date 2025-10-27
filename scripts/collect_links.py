import requests
from bs4 import BeautifulSoup
import json
import os
import time
from urllib.parse import urlparse, parse_qs, unquote, quote_plus
from datetime import datetime

SEARCH_TERMS = ["drugs forum"]
LINKS_FOLDER = os.path.join("links")
os.makedirs(LINKS_FOLDER, exist_ok=True)

# Current token parameter required by Ahmia (update if site changes)
TOKEN = "32f457"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://ahmia.fi/",
    "Accept-Language": "en-US,en;q=0.9"
}

def collect_links():
    results = {}

    for term in SEARCH_TERMS:
        print(f"[*] Searching for: {term}")
        query = quote_plus(term)
        url = f"https://ahmia.fi/search/?q={query}&t={TOKEN}"

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

        print(f"  [+] Found {len(onion_links)} links for '{term}'")
        results[term] = list(onion_links)
        time.sleep(2)  # polite delay between searches

    if not any(results.values()):
        print("[!] No links found. The Ahmia token may have changed.")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(LINKS_FOLDER, f"links_{today}.json")
    with open(filename, "w") as outfile:
        json.dump(results, outfile, indent=4)

    print(f"[+] Saved onion links to {filename}")
    return filename

if __name__ == "__main__":
    collect_links()
