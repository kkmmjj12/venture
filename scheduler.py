"""
APScheduler로 매일 지정 시간에 자동 실행
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config import NOTIFY_HOUR, NOTIFY_MINUTE
from crawler import run_all


def start():
    scheduler = BlockingScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        run_all,
        trigger=CronTrigger(hour=NOTIFY_HOUR, minute=NOTIFY_MINUTE),
        id="daily_contest_crawl",
        name="공모전 일일 크롤링",
        replace_existing=True,
    )
    print(f"스케줄러 시작: 매일 {NOTIFY_HOUR:02d}:{NOTIFY_MINUTE:02d} KST에 실행됩니다.")
    print("종료하려면 Ctrl+C를 누르세요.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("스케줄러 종료")
