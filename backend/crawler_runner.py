"""
모든 크롤러를 순서대로 실행하고 DB에 저장
"""
from backend.database import SessionLocal
from backend.models import Competition
from backend.crawlers.linkareer import LinkareerCrawler
from backend.crawlers.wevity import WevityCrawler
from backend.crawlers.thinkgood import ThinkgoodCrawler
from backend.crawlers.campuspick import CampuspickCrawler
from backend.crawlers.gonmofair import GonmofairCrawler
from datetime import datetime


CRAWLERS = [
    LinkareerCrawler,
    WevityCrawler,
    ThinkgoodCrawler,
    CampuspickCrawler,
    GonmofairCrawler,
]


def upsert_competition(db, data: dict) -> bool:
    """중복 체크 후 삽입 또는 업데이트"""
    existing = db.query(Competition).filter(
        Competition.title == data["title"],
        Competition.source_site == data["source_site"],
    ).first()

    if existing:
        # 업데이트
        for key, val in data.items():
            if key not in ("crawled_at",) and val is not None:
                setattr(existing, key, val)
        existing.updated_at = datetime.utcnow()
        return False  # updated
    else:
        comp = Competition(
            title=data["title"],
            organization=data.get("organization", ""),
            category=data.get("category", "기타IT"),
            source_site=data.get("source_site", ""),
            source_url=data.get("source_url", ""),
            original_url=data.get("original_url", ""),
            deadline=data.get("deadline"),
            start_date=data.get("start_date"),
            prize=data.get("prize", ""),
            description=data.get("description", ""),
            thumbnail=data.get("thumbnail", ""),
            is_active=True,
            crawled_at=datetime.utcnow(),
        )
        db.add(comp)
        return True  # inserted


def seed_if_empty(_db):
    pass  # 실제 크롤링 데이터만 사용


def run_all_crawlers():
    db = SessionLocal()
    total_new = 0
    total_updated = 0

    try:
        for CrawlerClass in CRAWLERS:
            crawler = CrawlerClass()
            try:
                items = crawler.crawl()
                for item in items:
                    is_new = upsert_competition(db, item)
                    if is_new:
                        total_new += 1
                    else:
                        total_updated += 1
                db.commit()
            except Exception as e:
                print(f"[크롤러] {CrawlerClass.source_name} 오류: {e}")
                db.rollback()

        # 마감된 공모전 비활성화
        now = datetime.utcnow()
        expired = db.query(Competition).filter(
            Competition.deadline < now,
            Competition.is_active == True
        ).all()
        for comp in expired:
            comp.is_active = False
        db.commit()

        # 크롤링 결과가 없으면 샘플 데이터 사용
        seed_if_empty(db)

        print(f"[크롤러] 완료 - 신규: {total_new}개, 업데이트: {total_updated}개, 만료처리: {len(expired)}개")

    finally:
        db.close()

    return {"new": total_new, "updated": total_updated, "expired": len(expired)}
