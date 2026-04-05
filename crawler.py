"""
크롤링 + DB 저장 + 알림 전송 핵심 로직
"""
from scrapers import ALL_SCRAPERS
from db import init_db, save_contests, get_pending_notification, mark_notified
from notifier import TelegramNotifier


def run_crawl() -> list[dict]:
    """모든 스크래퍼 실행 → 신규 공모전만 DB 저장 → 새 목록 반환"""
    print("=" * 50)
    print("공모전 크롤링 시작...")
    all_contests = []
    for ScraperClass in ALL_SCRAPERS:
        scraper = ScraperClass()
        print(f"[{scraper.source_name}] 스크래핑 중...")
        try:
            contests = scraper.scrape()
            all_contests.extend(contests)
        except Exception as e:
            print(f"[ERROR] {scraper.source_name}: {e}")

    new_contests = save_contests(all_contests)
    print(f"총 {len(all_contests)}개 수집 → 신규 {len(new_contests)}개 저장")
    return new_contests


def run_notify():
    """미전송 공모전을 텔레그램으로 전송"""
    pending = get_pending_notification()
    if not pending:
        print("전송할 신규 공모전 없음")
        return

    notifier = TelegramNotifier()
    notifier.send(pending)
    mark_notified([c["uid"] for c in pending])


def run_all():
    """크롤링 + 알림 한 번에 실행"""
    init_db()
    run_crawl()
    run_notify()
