from fastapi import APIRouter, Query
from typing import List, Dict
from analytics.keyword_trends import keyword_trends
from analytics.repeated_domains import repeated_domains_analysis
from analytics.source_summary import generate_source_summary
from analytics.evolution_trends import get_time_trends, get_site_evolution
from analytics.unique_domains import group_unique_domains_by_day  

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/keywords")
def fetch_keywords(limit: int = Query(30, description="Number of top keywords to return")):
    try:
        trends = keyword_trends(top_n=limit)
        return {"keywords": trends}
    except Exception as e:
        return {"error": str(e)}

@router.get("/repeated-domains")
def get_repeated_domains():
    data = repeated_domains_analysis()
    return data

@router.get("/source-summary")
def get_source_summary():
    try:
        summary_data = generate_source_summary()
        return {"sources": summary_data}
    except Exception as e:
        return {"error": str(e)}

@router.get("/time-trends")
async def time_trends(days: int = 30):
    result = await get_time_trends(days)
    print("Time Trends Result:", result)
    return result

@router.get("/site-evolution")
async def site_evolution():
    result = await get_site_evolution()
    print("Site Evolution Result:", result)
    return result


# 🆕 New Route for Daily Unique Domains
@router.get("/daily-domains")
def get_daily_unique_domains():

    try:
        data = group_unique_domains_by_day()
        return {"daily_domains": data}
    except Exception as e:
        return {"error": str(e)}
