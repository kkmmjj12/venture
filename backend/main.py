import os
from fastapi import FastAPI, Depends, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from backend.database import init_db, get_db
from backend.models import Competition
from backend.scheduler import start_scheduler, stop_scheduler
from backend.crawler_runner import run_all_crawlers, seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    init_db()

    # DB가 비어있으면 샘플 데이터 + 크롤링
    from backend.database import SessionLocal
    db = SessionLocal()
    seed_if_empty(db)
    db.close()

    # 크롤링 실행 (백그라운드)
    import threading
    threading.Thread(target=run_all_crawlers, daemon=True).start()

    # 스케줄러 시작
    start_scheduler()

    yield

    # 종료
    stop_scheduler()


app = FastAPI(
    title="IT 공모전 크롤러",
    description="국내 IT 공모전 정보 수집 및 제공 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───── API 엔드포인트 ─────

@app.get("/api/competitions")
def list_competitions(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    source: Optional[str] = Query(None, description="출처 사이트 필터"),
    sort: Optional[str] = Query("latest", description="정렬: latest | deadline | deadline_asc"),
    search: Optional[str] = Query(None, description="검색어"),
    include_expired: bool = Query(False, description="만료된 공모전 포함"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    query = db.query(Competition)

    if not include_expired:
        query = query.filter(Competition.is_active == True)

    if category and category != "전체":
        query = query.filter(Competition.category == category)

    if source:
        query = query.filter(Competition.source_site == source)

    if search:
        query = query.filter(
            or_(
                Competition.title.ilike(f"%{search}%"),
                Competition.organization.ilike(f"%{search}%"),
            )
        )

    # 정렬
    now = datetime.utcnow()
    if sort == "deadline":
        # 마감 임박순 (마감일 있는 것 먼저, 가까운 순)
        query = query.order_by(
            Competition.deadline.is_(None),
            Competition.deadline.asc(),
        )
    elif sort == "latest":
        query = query.order_by(Competition.crawled_at.desc())
    else:
        query = query.order_by(Competition.crawled_at.desc())

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [c.to_dict() for c in items],
    }


@app.get("/api/competitions/{comp_id}")
def get_competition(comp_id: int, db: Session = Depends(get_db)):
    comp = db.query(Competition).filter(Competition.id == comp_id).first()
    if not comp:
        return JSONResponse(status_code=404, content={"error": "공모전을 찾을 수 없습니다."})
    return comp.to_dict()


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = (
        db.query(Competition.category, func.count(Competition.id).label("count"))
        .filter(Competition.is_active == True)
        .group_by(Competition.category)
        .all()
    )
    total = db.query(Competition).filter(Competition.is_active == True).count()
    categories = [{"name": "전체", "count": total}]
    categories += [{"name": r.category or "기타IT", "count": r.count} for r in rows]
    return categories


@app.get("/api/sources")
def get_sources(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = (
        db.query(Competition.source_site, func.count(Competition.id).label("count"))
        .filter(Competition.is_active == True)
        .group_by(Competition.source_site)
        .all()
    )
    SOURCE_DISPLAY = {
        "linkareer": "링커리어",
        "wevity": "위비티",
        "thinkgood": "씽굿",
        "gonmofair": "공모전박람회",
    }
    return [
        {"id": r.source_site, "name": SOURCE_DISPLAY.get(r.source_site, r.source_site), "count": r.count}
        for r in rows
    ]


@app.post("/api/refresh")
def refresh_competitions(background_tasks: BackgroundTasks):
    """수동으로 크롤링 트리거"""
    background_tasks.add_task(run_all_crawlers)
    return {"message": "크롤링을 시작했습니다. 잠시 후 새로고침 해주세요."}


@app.post("/api/discord/test")
def test_discord():
    """Discord 연결 테스트"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        return JSONResponse(
            status_code=400,
            content={"error": ".env 파일에 DISCORD_WEBHOOK_URL을 설정해주세요."}
        )
    from backend.discord_notifier import send_test_message
    success = send_test_message(webhook_url)
    if success:
        return {"message": "Discord 테스트 메시지를 전송했습니다!"}
    return JSONResponse(status_code=500, content={"error": "Discord 전송에 실패했습니다."})


@app.post("/api/discord/notify")
def manual_discord_notify(db: Session = Depends(get_db)):
    """수동으로 Discord 일일 알림 전송"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not webhook_url:
        return JSONResponse(
            status_code=400,
            content={"error": ".env 파일에 DISCORD_WEBHOOK_URL을 설정해주세요."}
        )
    competitions = db.query(Competition).filter(Competition.is_active == True).all()
    from backend.discord_notifier import send_daily_update
    success = send_daily_update(competitions, webhook_url)
    if success:
        return {"message": f"Discord에 {len(competitions)}개 공모전 정보를 전송했습니다!"}
    return JSONResponse(status_code=500, content={"error": "Discord 전송에 실패했습니다."})


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    now = datetime.utcnow()
    total = db.query(Competition).filter(Competition.is_active == True).count()
    closing_soon = db.query(Competition).filter(
        Competition.is_active == True,
        Competition.deadline != None,
        Competition.deadline <= now.replace(hour=0, minute=0) + __import__('datetime').timedelta(days=8),
        Competition.deadline >= now,
    ).count()
    return {"total": total, "closing_soon": closing_soon}


# ───── 정적 파일 서빙 ─────
import pathlib
frontend_dir = pathlib.Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def root():
        return FileResponse(str(frontend_dir / "index.html"))
