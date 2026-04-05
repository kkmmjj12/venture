"""
Telegram 알림 모듈
python-telegram-bot v20 사용 (async)
"""
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

MAX_PER_MESSAGE = 10  # 한 메시지에 공모전 최대 개수


def _build_message(contests: list[dict], page: int, total_pages: int) -> str:
    cs_only = [c for c in contests if c.get("is_cs")]
    others = [c for c in contests if not c.get("is_cs")]
    ordered = cs_only + others

    lines = []
    if page == 1:
        lines.append(f"🚀 *Venture | 오늘의 신규 공모전* ({len(contests)}건)")
        lines.append("")

    for c in ordered:
        badge = "💻" if c.get("is_cs") else "📋"
        title = c["title"].replace("*", "\\*").replace("_", "\\_").replace("[", "\\[")
        line = f"{badge} *{title}*"
        if c.get("organizer"):
            line += f"\n   주최: {c['organizer']}"
        if c.get("deadline"):
            line += f"  |  마감: {c['deadline']}"
        if c.get("url"):
            line += f"\n   🔗 [바로가기]({c['url']})"
        lines.append(line)
        lines.append("")

    if total_pages > 1:
        lines.append(f"_({page}/{total_pages} 페이지)_")

    return "\n".join(lines)


async def _send(bot: Bot, text: str):
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


async def _send_all(contests: list[dict]):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    if not contests:
        await _send(bot, "✅ 오늘은 신규 공모전이 없습니다.")
        return

    # MAX_PER_MESSAGE 단위로 쪼개서 전송
    chunks = [
        contests[i:i + MAX_PER_MESSAGE]
        for i in range(0, len(contests), MAX_PER_MESSAGE)
    ]
    total = len(chunks)
    for idx, chunk in enumerate(chunks, 1):
        msg = _build_message(chunk, idx, total)
        await _send(bot, msg)
        if idx < total:
            await asyncio.sleep(1)  # 텔레그램 rate limit 방지


class TelegramNotifier:
    def send(self, contests: list[dict]):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("[Telegram] BOT_TOKEN 또는 CHAT_ID가 설정되지 않았습니다.")
            return
        asyncio.run(_send_all(contests))
        print(f"[Telegram] {len(contests)}개 공모전 알림 전송 완료")
