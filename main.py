"""
공모전 크롤러 진입점

사용법:
  python main.py          # 스케줄러 모드 (매일 자동 실행)
  python main.py --now    # 즉시 1회 실행 (테스트용)
  python main.py --crawl  # 크롤링만 (알림 없음)
"""
import sys
from db import init_db


def main():
    init_db()

    args = sys.argv[1:]

    if "--now" in args:
        from crawler import run_all
        print("[즉시 실행 모드]")
        run_all()

    elif "--crawl" in args:
        from crawler import run_crawl
        print("[크롤링 전용 모드]")
        run_crawl()

    else:
        from scheduler import start
        start()


if __name__ == "__main__":
    main()
