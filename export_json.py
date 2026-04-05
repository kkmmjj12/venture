"""
competitions.db → docs/data.json 내보내기
GitHub Actions에서 크롤링 후 자동 실행됨
"""
import json
import os
from datetime import datetime, timezone
from backend.database import SessionLocal, init_db
from backend.models import Competition

OUTPUT = os.path.join(os.path.dirname(__file__), "docs", "data.json")

SOURCE_LABEL = {
    "linkareer":  "링커리어",
    "wevity":     "위비티",
    "thinkgood":  "씽굿",
    "gonmofair":  "공모전박람회",
    "campuspick": "캠퍼스픽",
}


def export():
    init_db()
    db = SessionLocal()
    now = datetime.utcnow()

    try:
        rows = (
            db.query(Competition)
            .filter(Competition.is_active == True)
            .order_by(Competition.crawled_at.desc())
            .limit(500)
            .all()
        )

        contests = []
        for c in rows:
            days_left = None
            deadline_str = None
            if c.deadline:
                delta = c.deadline - now
                days_left = delta.days
                deadline_str = c.deadline.strftime("%Y.%m.%d")

            contests.append({
                "title":        c.title,
                "url":          c.source_url or c.original_url or "",
                "organization": c.organization or "",
                "deadline":     deadline_str,
                "days_left":    days_left,
                "category":     c.category or "기타IT",
                "source_site":  c.source_site or "",
                "source_label": SOURCE_LABEL.get(c.source_site, c.source_site or ""),
                "thumbnail":    c.thumbnail or "",
                "prize":        c.prize or "",
            })

    finally:
        db.close()

    payload = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M KST"),
        "total":   len(contests),
        "contests": contests,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[export] docs/data.json 저장 완료 ({len(contests)}개)")


if __name__ == "__main__":
    export()
