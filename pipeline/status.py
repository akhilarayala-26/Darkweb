
from datetime import datetime
from db.mongo_client import db
from pipeline.constants import JOB_NAME, IST

jobs_collection = db["jobs"]

def has_run_today_ist() -> bool:
    record = jobs_collection.find_one({"job": JOB_NAME})
    if not record:
        return False

    today_ist = datetime.now(IST).date().isoformat()
    return record.get("last_success_date") == today_ist
