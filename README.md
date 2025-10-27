# 🕵️‍♂️ Dark Web Data Pipeline

This project is a **modular and extensible data pipeline** designed to **collect, scrape, process, and analyze** `.onion` (dark web) URLs.  
It automates the complete workflow — from **data collection to advanced analytics** — enabling efficient monitoring, pattern discovery, and research on the dark web ecosystem.

---

## 🚀 Pipeline Overview

The pipeline consists of **two major stages**:

### 1. 🧩 Core Data Processing (in `scripts/`)
1. **🔗 Collect Onion Links**  
   * **Script:** `collect_links.py`  
   * **Description:** Crawls and gathers `.onion` URLs from predefined sources or seed lists.  
   * **Output:** `links_<date>.json` inside the `links/` folder.

2. **🧠 Scrape Onion Data**  
   * **Script:** `scrape_data.py`  
   * **Description:** Extracts titles, descriptions, and metadata from collected links.  
   * **Output:** `scraped_<date>.json` inside the `scraped/` folder.

3. **⚙️ Process Fingerprints (ML Classification)**  
   * **Script:** `process_fingerprints.py`  
   * **Description:** Cleans scraped data, generates content fingerprints, and classifies links using ML/NLP techniques.  
   * **Output:** `fingerprints_<date>.json` inside the `fingerprints/` folder.

4. **📚 Group Links by Title**  
   * **Script:** `filter_by_title.py`  
   * **Description:** Identifies pages sharing the same title across multiple onion links (useful for detecting mirrors or clones).  
   * **Output:** `grouped_titles_<date>.json` inside the `grouped_titles/` folder.

---

### 2. 📊 Analytics & Insights (in `analytics/`)
After processing, the data flows into the **Analytics Layer**, which generates statistical, behavioral, and semantic insights about the collected domains.

| Script | Description | Output |
| ------- | ------------ | ------- |
| `generate_reports.py` | Compiles all individual analytics outputs into a master report. | `reports/master_report_<date>.json` |
| `keyword_trends.py` | Detects frequently used keywords and topic clusters across scraped content. | `reports/keyword_trends_<date>.json` |
| `domain_activity.py` | Tracks active/inactive onion domains and uptime trends. | `reports/domain_activity_<date>.json` |
| `sentiment_trends.py` | Analyzes sentiment patterns in textual content over time. | `reports/sentiment_trends_<date>.json` |
| `category_stats.py` | Generates statistics for classified site categories (forums, markets, etc.). | `reports/category_stats_<date>.json` |
| `repeated_domains.py` | Detects repeated or mirrored onion domains. | `reports/repeated_domains_<date>.json` |
| `domain_url_activity.py` | Maps URL-level activity (homepages, subpages, redirects). | `reports/domain_url_activity_<date>.json` |
| `same_site_evolution.py` | Tracks how a site's content or title evolves across snapshots. | `reports/same_site_evolution_<date>.json` |

---

