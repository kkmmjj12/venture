import sqlite3
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contests (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                uid         TEXT UNIQUE NOT NULL,   -- 사이트별 고유 ID (URL 또는 title+deadline)
                title       TEXT NOT NULL,
                url         TEXT,
                organizer   TEXT,
                deadline    TEXT,
                category    TEXT,
                source      TEXT,                   -- 출처 사이트
                is_cs       INTEGER DEFAULT 0,       -- 컴공 관련 여부
                found_at    TEXT DEFAULT (datetime('now', 'localtime')),
                notified    INTEGER DEFAULT 0        -- 알림 전송 여부
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notify_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sent_at     TEXT DEFAULT (datetime('now', 'localtime')),
                count       INTEGER
            )
        """)
        conn.commit()


def is_new(uid: str) -> bool:
    """이미 DB에 있는 공모전이면 False"""
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM contests WHERE uid = ?", (uid,)).fetchone()
        return row is None


def save_contests(contests: list[dict]) -> list[dict]:
    """새로운 공모전만 저장하고 반환"""
    new_ones = []
    with get_conn() as conn:
        for c in contests:
            if is_new(c["uid"]):
                conn.execute("""
                    INSERT OR IGNORE INTO contests
                        (uid, title, url, organizer, deadline, category, source, is_cs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["uid"], c["title"], c.get("url", ""), c.get("organizer", ""),
                    c.get("deadline", ""), c.get("category", ""),
                    c.get("source", ""), int(c.get("is_cs", False)),
                ))
                new_ones.append(c)
        conn.commit()
    return new_ones


def mark_notified(uids: list[str]):
    with get_conn() as conn:
        conn.executemany(
            "UPDATE contests SET notified = 1 WHERE uid = ?",
            [(uid,) for uid in uids],
        )
        conn.execute(
            "INSERT INTO notify_log (count) VALUES (?)", (len(uids),)
        )
        conn.commit()


def get_pending_notification() -> list[dict]:
    """아직 알림 안 보낸 공모전 조회 (CS 관련 우선 정렬)"""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM contests
            WHERE notified = 0
            ORDER BY is_cs DESC, found_at DESC
        """).fetchall()
        return [dict(r) for r in rows]
