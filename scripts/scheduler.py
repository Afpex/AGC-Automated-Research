# scripts/scheduler.py
def schedule_tasks():
    schedule.every().day.at("06:00").do(run_pipeline)
    schedule.every().monday.do(generate_weekly_report)