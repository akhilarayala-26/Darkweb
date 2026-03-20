import time
from pymongo import MongoClient

def test_get_topics():
    TOPIC_DB_MAP = {
        "drugs": {"db": "darkweb_pipeline"},
        "credit_card": {"db": "darkweb_pipeline_c1"},
        "weapons": {"db": "darkweb_pipeline_c2"},
    }
    client = MongoClient('mongodb+srv://reddyhashish:Hasini120@cluster0.ckmru0d.mongodb.net/capestone')
    
    for topic_id, info in TOPIC_DB_MAP.items():
        t0 = time.time()
        db = client[info["db"]]
        pipeline = [
            {"$project": {"content_array": {"$objectToArray": "$content"}}},
            {"$unwind": "$content_array"},
            {"$project": {"records_count": {"$size": {"$ifNull": ["$content_array.v.records", []]}}}},
            {"$group": {"_id": None, "total": {"$sum": "$records_count"}}}
        ]
        res = list(db["fingerprints_data"].aggregate(pipeline))
        fp_count = res[0]["total"] if res else 0

        dates = [doc["_id"] for doc in db["fingerprints_data"].find({}, {"_id": 1})]
        
        print(f'{topic_id} took {time.time() - t0:.2f}s, count: {fp_count}')

if __name__ == "__main__":
    test_get_topics()
