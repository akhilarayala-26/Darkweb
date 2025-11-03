# 🕵️‍♂️ Dark Web Data Pipeline — v2.0  

This project is a **fully automated data pipeline** designed to **collect, scrape, preprocess, and analyze** `.onion` (dark web) URLs.  
It integrates **FastAPI**, **MongoDB**, and a **React + TailwindCSS dashboard** to automate and visualize the entire dark web intelligence workflow — from raw data collection to advanced analytics.

---

## 🚀 Overview  

The system operates as a **modular, end-to-end data pipeline**, now enhanced with:
- ✅ **Automated ETL (Extract, Transform, Load)** into MongoDB  
- ✅ **FastAPI backend** for on-demand analytics  
- ✅ **Interactive React dashboard** for visualization and monitoring  
- ✅ **Scheduled scraping and preprocessing pipeline**

---

## ⚙️ System Architecture  

```
        ┌──────────────────────────┐
        │     React Dashboard      │
        │ (Tailwind + Recharts UI) │
        └────────────┬─────────────┘
                     │ REST API Calls
                     ▼
        ┌──────────────────────────┐
        │         FastAPI          │
        │   - /pipeline routes     │
        │   - /analytics routes    │
        └────────────┬─────────────┘
                     │
        ┌──────────────────────────┐
        │       Python Scripts     │
        │  (Scraping + Analytics)  │
        └────────────┬─────────────┘
                     │
        ┌──────────────────────────┐
        │         MongoDB          │
        │ (Storage + Aggregation)  │
        └──────────────────────────┘
```

---

## 🧩 Core Pipeline (in `scripts/`)

| Stage | Script | Description | Output |
|--------|---------|-------------|---------|
| 🔗 **Collect Onion Links** | `collect_links.py` | Crawls and gathers `.onion` URLs from seed sources. | `links/links_<date>.json` |
| 🧠 **Scrape Onion Data** | `scrape_data.py` | Extracts titles, metadata, and content from collected links. | `scraped/scraped_<date>.json` |
| ⚙️ **Process Fingerprints (ML Classification)** | `process_fingerprints.py` | Cleans and classifies scraped data using NLP/ML techniques. | `fingerprints/fingerprints_<date>.json` |
| 📚 **Group Links by Title** | `filter_by_title.py` | Identifies pages with duplicate titles to detect mirrors/clones. | `grouped_titles/grouped_titles_<date>.json` |

### 🔄 Automation Added
All above stages are now **automated**:
- Each stage runs sequentially on a single **button click** from the dashboard.
- Outputs are **directly stored in MongoDB**.
- Status and logs are viewable from the FastAPI or frontend console.

---

## ⚡ FastAPI Backend  

The backend exposes modular routes for:

### 🔧 `pipeline/` routes  
Handle scraping, processing, and data insertion into MongoDB.  
Triggered from frontend buttons or scheduled cron jobs.

### 📊 `analytics/` routes  
Provide analytical insights through on-demand API calls.

These include routes for:
- `/keywords` → Keyword Trends  
- `/repeated-domains` → Repeated or Mirrored Domains  
- `/source-summary` → Source Distribution Summary  
- `/time-trends` → Time-based Trends  
- `/site-evolution` → Site Evolution Analysis  

All routes are registered in the main FastAPI app:
```
app.include_router(pipeline.router)
app.include_router(analytics.router)
```

---

## 💻 Frontend Dashboard (React + TailwindCSS)

A **modern, responsive dashboard** for controlling the pipeline and viewing analytics.  

### 🧱 Pages
The React dashboard has **five key pages**, defined as:

```javascript
const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/keywords', icon: TrendingUp, label: 'Keyword Trends' },
  { path: '/titles', icon: FileText, label: 'Grouped Titles' },
  { path: '/sources', icon: Globe, label: 'Source Summary' },
  { path: '/trends', icon: Activity, label: 'Time Trends' },
];
```

Each page connects to the corresponding FastAPI endpoint and displays analytics results using Recharts.

---

## 📊 Analytics Modules (in `analytics/`)

| Script | Description | Output |
|---------|--------------|---------|
| `keyword_trends.py` | Detects trending keywords and topic clusters. | `reports/keyword_trends_<date>.json` |
| `repeated_domains.py` | Finds mirrored or duplicate domains. | `reports/repeated_domains_<date>.json` |
| `source_summary.py` | Summarizes link sources and categories. | `reports/source_summary_<date>.json` |
| `evolution_trends.py` | Tracks site or content changes over time. | `reports/site_evolution_<date>.json` |
| `category_stats.py` | Category-wise statistics (markets, forums, etc.). | `reports/category_stats_<date>.json` |

---

## 🧠 Tech Stack

| Layer | Technologies |
|--------|--------------|
| **Frontend** | React, Tailwind CSS, Recharts |
| **Backend** | FastAPI |
| **Database** | MongoDB |
| **Automation** | Python (Requests, BeautifulSoup, asyncio) |
| **ML/NLP** | Scikit-learn, NLTK, spaCy |
| **Visualization** | Recharts, Plotly, or Chart.js |


---

## 🧩 Future Enhancements

- Add **user authentication** and role-based analytics access.  
- Integrate **Celery + Redis** for background scraping tasks.  
- Implement **graph-based link clustering** for deep web relationships.  
- Real-time **socket updates** for live pipeline monitoring.  

---

🗓️ *Last updated:* 2025-11-03
