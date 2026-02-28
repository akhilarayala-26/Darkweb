from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import pipeline, analytics, dashboard

from scheduler import start_scheduler
from pipeline.runner import run_pipeline
from pipeline.status import has_run_today_ist
from pipeline.vpn import ensure_warp_connected   # ✅ NEW

app = FastAPI(title="Dark Web Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def startup_event():
    # 🔐 1️⃣ ENSURE VPN FIRST (before MongoDB is touched)
    ensure_warp_connected()

    # ⏱️ 2️⃣ Start scheduler
    start_scheduler()

    # 🧠 3️⃣ Now MongoDB is safe to access
    if not has_run_today_ist():
        print("⚠️ Pipeline not run today (IST). Triggering now...")
        run_pipeline()
    else:
        print("✅ Pipeline already executed today (IST). Skipping.")


@app.get("/")
def home():
    return {"message": "Dark Web Analytics API running successfully"}
