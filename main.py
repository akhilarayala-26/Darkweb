from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import pipeline, analytics

app = FastAPI(title="Dark Web Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline.router)
app.include_router(analytics.router)

@app.get("/")
def home():
    return {"message": "Dark Web Analytics API running successfully"}
