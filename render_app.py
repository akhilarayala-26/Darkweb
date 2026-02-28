"""Lightweight entry point for Render deployment.
Only serves the dashboard API — no pipeline/scheduler/VPN/ML dependencies.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import dashboard

app = FastAPI(title="Dark Web Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)


@app.get("/")
def home():
    return {"message": "Dark Web Analytics API running successfully"}
