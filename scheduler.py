from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pipeline.runner import run_pipeline
from pipeline.constants import IST

scheduler = BackgroundScheduler(timezone=IST)

def start_scheduler():
    scheduler.add_job(
        run_pipeline,
        CronTrigger(hour=10, minute=0),  # 10 AM IST (change if needed)
        id="daily_pipeline_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()
