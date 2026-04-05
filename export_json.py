"""
DB에서 공모전 데이터를 docs/data.json 으로 내보내기
GitHub Actions에서 크롤링 후 자동 실행됨
"""
import json
import os
from datetime import datetime
from db import get_conn

OUTPUT = os.path.join(os.path.dirname(__file__), "docs", "data.json")


def export():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT title, url, organizer, deadline, category, source, is_cs
            FROM contests
            ORDER BY is_cs DESC, found_at DESC
            LIMIT 500
        """).fetchall()

    contests = [dict(r) for r in rows]
    for c in contests:
        c["is_cs"] = bool(c["is_cs"])

    payload = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M KST"),
        "total": len(contests),
        "contests": contests,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[export] docs/data.json 저장 완료 ({len(contests)}개)")


if __name__ == "__main__":
    from db import init_db
    init_db()
    export()
