import sys
from datetime import datetime
from db.mongo_client import db
from utils.command_runner import execute_command

from pipeline.constants import JOB_NAME, IST
from pipeline.vpn import ensure_warp_connected
from pipeline.tor import ensure_tor_running

jobs_collection = db["jobs"]


def run_pipeline():
    """
    Orchestrates the full daily pipeline execution.

    Flow:
    1. Ensure VPN (WARP) is connected
    2. Auto-start Tor (macOS safe) and verify routing
    3. Execute scripts/run.py
    4. Persist execution metadata in MongoDB

    This function is fail-soft:
    - VPN/Tor failure will NOT crash FastAPI
    - Pipeline execution will be skipped safely
    """

    now_ist = datetime.now(IST)

    try:
        # 1️⃣ Ensure VPN first (college Wi-Fi requirement)
        ensure_warp_connected()

        # 2️⃣ Ensure Tor is running (auto-start on macOS)
        tor_ok = ensure_tor_running()
        if not tor_ok:
            print("⚠️ Tor unavailable. Skipping pipeline execution.")
            return

        # 3️⃣ Run the actual pipeline script
        print("🚀 Starting data collection pipeline...")
        execute_command(f'"{sys.executable}" run.py', cwd="scripts")

        # 4️⃣ Update MongoDB on success
        jobs_collection.update_one(
            {"job": JOB_NAME},
            {"$set": {
                "last_run": now_ist,
                "last_success_date": now_ist.date().isoformat(),
                "status": "success"
            }},
            upsert=True
        )

        print("✅ Pipeline executed successfully.")

    except Exception as e:
        # Fail-soft: log error but do not crash FastAPI
        print(f"❌ Pipeline execution failed: {e}")

        jobs_collection.update_one(
            {"job": JOB_NAME},
            {"$set": {
                "last_run": now_ist,
                "status": "failed",
                "error": str(e)
            }},
            upsert=True
        )
