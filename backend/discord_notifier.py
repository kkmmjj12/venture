"""
디스코드 웹훅 알림 모듈
매일 지정 시간에 공모전 정보를 Discord 채널에 전송
"""
import requests
import os
from datetime import datetime, timedelta
from typing import List
from backend.models import Competition

SOURCE_COLORS = {
    "linkareer": 0x0066FF,
    "wevity": 0x00C851,
    "thinkgood": 0xFF8800,
    "gonmofair": 0x9C27B0,
}

SOURCE_DISPLAY = {
    "linkareer": "링커리어",
    "wevity": "위비티",
    "thinkgood": "씽굿",
    "campuspick": "캠퍼스픽",
    "gonmofair": "공모전박람회",
}


def get_dday_emoji(days_left: int) -> str:
    if days_left is None:
        return "📅"
    if days_left < 0:
        return "❌"
    if days_left <= 3:
        return "🔥"
    if days_left <= 7:
        return "⚠️"
    if days_left <= 14:
        return "📌"
    return "📅"


def send_daily_update(competitions: List[Competition], webhook_url: str) -> bool:
    """일일 공모전 업데이트를 Discord로 전송"""
    if not webhook_url:
        print("[Discord] DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
        return False

    now = datetime.utcnow()
    today = now.date()

    # 오늘 새로 추가된 공모전
    new_today = [c for c in competitions if c.crawled_at and c.crawled_at.date() == today]

    # 마감 임박 (7일 이내)
    closing_soon = []
    for c in competitions:
        if c.deadline:
            delta = c.deadline - now
            if 0 <= delta.days <= 7:
                closing_soon.append((c, delta.days))
    closing_soon.sort(key=lambda x: x[1])

    # 전체 활성 공모전 수
    active_count = sum(1 for c in competitions if c.is_active)

    embeds = []

    # 헤더 임베드
    embeds.append({
        "title": f"\U0001f3c6 IT 공모전 일일 업데이트 - {now.strftime('%Y년 %m월 %d일')}",
        "description": (
            f"📊 **전체 공모전**: {active_count}개\n"
            f"🆕 **오늘 새로 등록**: {len(new_today)}개\n"
            f"🔥 **마감 임박 (7일 이내)**: {len(closing_soon)}개"
        ),
        "color": 0x6C63FF,
        "footer": {"text": "Venture | 매일 자동 업데이트"},
        "timestamp": now.isoformat() + "Z",
    })

    # 마감 임박 공모전
    if closing_soon:
        lines = []
        for comp, days in closing_soon[:8]:
            source = SOURCE_DISPLAY.get(comp.source_site, comp.source_site)
            emoji = get_dday_emoji(days)
            if days == 0:
                dday = "오늘 마감!"
            else:
                dday = f"D-{days}"
            lines.append(f"{emoji} **{dday}** [{comp.title[:35]}...]({comp.source_url})\n　　`{source}` · {comp.organization or '주최미상'}")

        embeds.append({
            "title": "⏰ 마감 임박 공모전",
            "description": "\n\n".join(lines),
            "color": 0xFF6B6B,
        })

    # 오늘 새로 등록된 공모전
    if new_today:
        lines = []
        for comp in new_today[:8]:
            source = SOURCE_DISPLAY.get(comp.source_site, comp.source_site)
            deadline_str = comp.deadline.strftime("%m.%d") if comp.deadline else "미정"
            lines.append(f"🆕 [{comp.title[:35]}...]({comp.source_url})\n　　`{source}` · 마감 **{deadline_str}** · {comp.category}")

        embeds.append({
            "title": "🆕 오늘 새로 등록된 공모전",
            "description": "\n\n".join(lines),
            "color": 0x00C851,
        })

    payload = {
        "username": "Venture 알리미",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        "embeds": embeds[:10],  # Discord 최대 10개
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code in (200, 204):
            print(f"[Discord] 알림 전송 성공")
            return True
        else:
            print(f"[Discord] 전송 실패: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"[Discord] 전송 오류: {e}")
        return False


def send_test_message(webhook_url: str) -> bool:
    """테스트 메시지 전송"""
    if not webhook_url:
        return False
    payload = {
        "username": "Venture 알리미",
        "embeds": [{
            "title": "✅ 연결 테스트 성공!",
            "description": "IT 공모전 크롤러와 Discord가 정상 연결되었습니다.\n매일 새로운 공모전 정보를 여기에서 받아보세요!",
            "color": 0x6C63FF,
            "footer": {"text": "Venture"},
        }]
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return resp.status_code in (200, 204)
    except Exception:
        return False
