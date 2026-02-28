import os
import json
from datetime import datetime, timezone
from collections import defaultdict
from urllib.parse import urlparse
from pymongo import MongoClient

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================
# ✅ MONGO CONNECTION
# ==============================
uri = os.getenv("MONGO_URI", "mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone")
client = MongoClient(uri)
db = client["darkweb_pipeline_c2"]

print(f"[MongoDB] Connected to cluster: {uri.split('@')[-1].split('/')[0]}")
print(f"[MongoDB] Using database: {db.name}")

# ==============================
# 🔧 HELPER FUNCTIONS
# ==============================

def extract_base_domain(url):
    """Extract the base .onion domain from a URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return url


def jaccard_similarity(set_a, set_b):
    """Compute Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def get_metadata_set(record):
    """Extract a combined set of identifiers from record metadata."""
    meta = record.get("metadata", {})
    handles = record.get("social_handles", {})
    items = set()
    for wallet in meta.get("btc_wallets", []):
        items.add(f"btc:{wallet}")
    for email in meta.get("emails", []):
        items.add(f"email:{email}")
    for pgp in meta.get("pgp_keys", []):
        items.add(f"pgp:{pgp[:64]}")  # Use first 64 chars as key identifier
    for tg in handles.get("telegram", []):
        items.add(f"tg:{tg}")
    for x_handle in handles.get("x", []):
        items.add(f"x:{x_handle}")
    return items


class UnionFind:
    """Union-Find data structure for clustering mirror sites."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

    def clusters(self):
        groups = defaultdict(list)
        for i in range(len(self.parent)):
            groups[self.find(i)].append(i)
        return list(groups.values())


# ==============================
# 🔍 MIRROR DETECTION LOGIC
# ==============================

def detect_mirrors_in_group(title, urls, scraped_lookup):
    """
    Detect mirror sites within a single title group.

    Returns a list of mirror clusters found in this group.
    Each cluster contains URLs that are mirrors of each other.
    """
    # Filter to URLs that have scraped data
    valid = []
    for url in urls:
        if url in scraped_lookup:
            valid.append((url, scraped_lookup[url]))

    if len(valid) < 2:
        return []

    n = len(valid)
    uf = UnionFind(n)
    pair_info = {}  # (i, j) -> {type, confidence, shared_meta}

    # ─── Layer 1: Exact text_hash match ───
    hash_groups = defaultdict(list)
    for idx, (url, record) in enumerate(valid):
        text_hash = record.get("text_hash", "")
        if text_hash:
            hash_groups[text_hash].append(idx)

    for text_hash, indices in hash_groups.items():
        if len(indices) > 1:
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    a, b = indices[i], indices[j]
                    # Only merge if different base domains
                    domain_a = extract_base_domain(valid[a][0])
                    domain_b = extract_base_domain(valid[b][0])
                    if domain_a != domain_b:
                        uf.union(a, b)
                        pair_info[(min(a, b), max(a, b))] = {
                            "type": "exact",
                            "confidence": 1.0,
                            "text_hash": text_hash
                        }

    # ─── Layer 2: TF-IDF cosine similarity (near mirrors) ───
    texts = []
    text_indices = []
    for idx, (url, record) in enumerate(valid):
        raw_text = record.get("raw_text", "").strip()
        if raw_text and len(raw_text) > 50:  # Skip very short / empty pages
            texts.append(raw_text)
            text_indices.append(idx)

    if len(texts) >= 2:
        try:
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.95
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_matrix)

            NEAR_THRESHOLD = 0.85

            for i in range(len(texts)):
                for j in range(i + 1, len(texts)):
                    if sim_matrix[i][j] >= NEAR_THRESHOLD:
                        a, b = text_indices[i], text_indices[j]
                        domain_a = extract_base_domain(valid[a][0])
                        domain_b = extract_base_domain(valid[b][0])
                        if domain_a != domain_b:
                            key = (min(a, b), max(a, b))
                            # Don't overwrite exact matches with near matches
                            if key not in pair_info:
                                uf.union(a, b)
                                pair_info[key] = {
                                    "type": "near",
                                    "confidence": round(float(sim_matrix[i][j]), 4)
                                }
        except Exception as e:
            print(f"  [!] TF-IDF failed for group '{title[:50]}': {e}")

    # ─── Layer 3: Metadata overlap (operator linking) ───
    meta_sets = []
    for idx, (url, record) in enumerate(valid):
        meta_sets.append(get_metadata_set(record))

    for i in range(n):
        if not meta_sets[i]:
            continue
        for j in range(i + 1, n):
            if not meta_sets[j]:
                continue
            jsim = jaccard_similarity(meta_sets[i], meta_sets[j])
            if jsim > 0.5:
                domain_a = extract_base_domain(valid[i][0])
                domain_b = extract_base_domain(valid[j][0])
                if domain_a != domain_b:
                    key = (min(i, j), max(i, j))
                    if key not in pair_info:
                        shared = meta_sets[i] & meta_sets[j]
                        uf.union(i, j)
                        pair_info[key] = {
                            "type": "operator-linked",
                            "confidence": round(jsim, 4),
                            "shared_identifiers": list(shared)
                        }

    # ─── Build clusters ───
    clusters_result = []
    for cluster_indices in uf.clusters():
        if len(cluster_indices) < 2:
            continue

        # Get unique domains in this cluster
        cluster_urls = [valid[i][0] for i in cluster_indices]
        cluster_domains = list(set(extract_base_domain(u) for u in cluster_urls))

        if len(cluster_domains) < 2:
            continue  # Same domain, different paths — not a mirror

        # Determine best match type and confidence
        best_type = "near"
        best_confidence = 0.0
        shared_metadata = []

        for i in cluster_indices:
            for j in cluster_indices:
                if i < j:
                    key = (i, j)
                    if key in pair_info:
                        info = pair_info[key]
                        if info["type"] == "exact":
                            best_type = "exact"
                            best_confidence = 1.0
                        elif info["confidence"] > best_confidence and best_type != "exact":
                            best_type = info["type"]
                            best_confidence = info["confidence"]
                        if "shared_identifiers" in info:
                            shared_metadata.extend(info["shared_identifiers"])

        clusters_result.append({
            "title": title,
            "mirror_type": best_type,
            "confidence": best_confidence if best_confidence > 0 else 0.85,
            "num_mirrors": len(cluster_domains),
            "domains": cluster_domains,
            "urls": cluster_urls,
            "shared_metadata": list(set(shared_metadata)),
            "text_hash": pair_info.get((cluster_indices[0], cluster_indices[1] if len(cluster_indices) > 1 else cluster_indices[0]), {}).get("text_hash", "")
        })

    return clusters_result


# ==============================
# 🚀 MAIN FUNCTION
# ==============================

def detect_mirrors():
    """
    Main entry point: detect mirror sites across all grouped titles.

    Reads from:
      - grouped_titles_data (title -> URLs mapping)
      - data_files (scraped content for each URL)

    Writes to:
      - mirror_data (detected mirror clusters)
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # ─── Load grouped titles ───
    grouped_doc = db.grouped_titles_data.find_one({"_id": today})
    if not grouped_doc:
        print(f"[!] No grouped titles found for {today}")
        return

    grouped = grouped_doc.get("content", {})
    print(f"\n🔍 Analyzing {len(grouped)} title groups for mirrors...\n")

    # ─── Load all scraped data into a URL -> record lookup ───
    scraped_lookup = {}
    scraped_docs = db.data_files.find({"type": "scraped"})
    for doc in scraped_docs:
        content = doc.get("content", {})
        for term, records in content.items():
            for record in records:
                url = record.get("url", "")
                if url:
                    scraped_lookup[url] = record

    print(f"[*] Loaded {len(scraped_lookup)} scraped records from MongoDB\n")

    # ─── Detect mirrors per group ───
    all_clusters = []
    cluster_id = 0

    for title, urls in grouped.items():
        # Deduplicate URLs within the group
        unique_urls = list(set(urls))
        if len(unique_urls) < 2:
            continue

        clusters = detect_mirrors_in_group(title, unique_urls, scraped_lookup)

        if clusters:
            print(f"  ✅ '{title[:60]}...' → {len(clusters)} mirror cluster(s)")
            for c in clusters:
                cluster_id += 1
                c["cluster_id"] = cluster_id
                all_clusters.append(c)
                # Print details
                print(f"      Cluster {cluster_id} ({c['mirror_type']}, conf: {c['confidence']}):")
                for domain in c["domains"][:5]:
                    print(f"        - {domain}")
                if len(c["domains"]) > 5:
                    print(f"        ... and {len(c['domains']) - 5} more")

    # ─── Summary stats ───
    summary = {
        "total_groups_analyzed": len(grouped),
        "total_mirror_clusters": len(all_clusters),
        "total_mirrored_domains": sum(c["num_mirrors"] for c in all_clusters),
        "exact_matches": sum(1 for c in all_clusters if c["mirror_type"] == "exact"),
        "near_matches": sum(1 for c in all_clusters if c["mirror_type"] == "near"),
        "operator_linked": sum(1 for c in all_clusters if c["mirror_type"] == "operator-linked")
    }

    # ─── Store results in MongoDB ───
    result_doc = {
        "_id": today,
        "mirror_clusters": all_clusters,
        "summary": summary,
        "created_at": datetime.now(timezone.utc),
        "last_updated": datetime.now(timezone.utc)
    }

    db.mirror_data.replace_one({"_id": today}, result_doc, upsert=True)

    # ─── Print summary ───
    print("\n" + "=" * 50)
    print("🪞 MIRROR DETECTION COMPLETE")
    print("=" * 50)
    print(f"  Groups analyzed:     {summary['total_groups_analyzed']}")
    print(f"  Mirror clusters:     {summary['total_mirror_clusters']}")
    print(f"  Mirrored domains:    {summary['total_mirrored_domains']}")
    print(f"  ├─ Exact matches:    {summary['exact_matches']}")
    print(f"  ├─ Near matches:     {summary['near_matches']}")
    print(f"  └─ Operator-linked:  {summary['operator_linked']}")
    print(f"\n📁 Results saved to MongoDB: mirror_data (id: {today})")


if __name__ == "__main__":
    detect_mirrors()
