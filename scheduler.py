from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from services.database import Database
from services.notifications import EmailService

scheduler = BackgroundScheduler()
db = Database()
email_service = EmailService()

def cleanup_old_records():
    try:
        # Get records older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        archived_count = db.archive_old_records(cutoff_date)
        
        # Send summary email
        report_data = {
            'job_type': 'Daily Cleanup',
            'archived_records': archived_count,
            'timestamp': datetime.now(),
            'status': 'SUCCESS'
        }
        
        email_service.send_admin_report(report_data)
        print(f"Cleanup completed at {datetime.now()}. Archived {archived_count} records.")
        
    except Exception as e:
        print(f"Error in cleanup job: {str(e)}")
        email_service.send_alert('Cleanup job failed', str(e))

# Run every day at midnight
scheduler.add_job(cleanup_old_records, 'cron', hour=0)
scheduler.start() 