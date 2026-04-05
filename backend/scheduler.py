"""
APScheduler 기반 자동 실행 스케줄러
- 주기적 크롤링 (기본 6시간마다)
- 매일 Discord 알림 (기본 오전 9시)
"""
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


_scheduler = None


def run_crawl_job():
    """크롤링 실행 (스케줄러에서 호출)"""
    from backend.crawler_runner import run_all_crawlers
    print("[스케줄러] 정기 크롤링 시작...")
    run_all_crawlers()


def run_discord_job():
    """Discord 알림 (스케줄러에서 호출)"""
    from backend.database import SessionLocal
    from backend.models import Competition
    from backend.discord_notifier import send_daily_update

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        print("[스케줄러] Discord webhook URL 미설정, 알림 건너뜀")
        return

    db = SessionLocal()
    try:
        competitions = db.query(Competition).filter(Competition.is_active == True).all()
        send_daily_update(competitions, webhook_url)
    finally:
        db.close()


def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    interval_hours = int(os.getenv("CRAWL_INTERVAL_HOURS", "6"))
    notify_hour = int(os.getenv("DAILY_NOTIFY_HOUR", "9"))
    notify_minute = int(os.getenv("DAILY_NOTIFY_MINUTE", "0"))

    _scheduler = BackgroundScheduler(timezone="Asia/Seoul")

    # 주기적 크롤링
    _scheduler.add_job(
        run_crawl_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id="crawl_job",
        name=f"정기 크롤링 ({interval_hours}시간마다)",
        replace_existing=True,
    )

    # 매일 Discord 알림
    _scheduler.add_job(
        run_discord_job,
        trigger=CronTrigger(hour=notify_hour, minute=notify_minute, timezone="Asia/Seoul"),
        id="discord_job",
        name=f"일일 Discord 알림 ({notify_hour:02d}:{notify_minute:02d})",
        replace_existing=True,
    )

    _scheduler.start()
    print(f"[스케줄러] 시작 - 크롤링: {interval_hours}시간마다, Discord: 매일 {notify_hour:02d}:{notify_minute:02d}")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        print("[스케줄러] 종료")
