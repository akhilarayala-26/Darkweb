import sys
from fastapi import APIRouter, BackgroundTasks
from utils.command_runner import execute_command

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])

@router.post("/run-scripts")
async def run_scripts(background_tasks: BackgroundTasks):
    def task():
        execute_command(f'"{sys.executable}" run.py', cwd="scripts")
    background_tasks.add_task(task)
    return {"message": "🚀 scripts/run.py started in background"}


@router.post("/run-analytics")
async def run_analytics(background_tasks: BackgroundTasks):
    def task():
        execute_command(f'"{sys.executable}" analytics/run_analytics.py')
    background_tasks.add_task(task)
    return {"message": "📊 analytics/run_analytics.py started in background"}

