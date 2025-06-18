from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sharepoint_sync import sync_data
import logging
from config import SYNC_INTERVAL

# ตั้งค่าระบบล็อก
logging.basicConfig()
logger = logging.getLogger("apscheduler")
logger.setLevel(logging.INFO)


def sync_job():
    """งานซิงค์ข้อมูลหลัก"""
    try:
        logger.info("🔄 Starting scheduled sync...")
        sync_data()
        logger.info("✅ Scheduled sync completed!")
    except Exception as e:
        logger.error(f"❌ Scheduled sync failed: {e}")


def start_scheduler():
    """เริ่มต้น scheduler"""
    scheduler = BackgroundScheduler()

    # ตั้งค่าตาม config (ค่าเริ่มต้น: ทุก 1 ชั่วโมง)
    scheduler.add_job(
        sync_job, trigger=IntervalTrigger(seconds=SYNC_INTERVAL), name="sharepoint_sync"
    )

    scheduler.start()
    logger.info(f"⏰ Scheduler started. Sync interval: {SYNC_INTERVAL} seconds")
    return scheduler
