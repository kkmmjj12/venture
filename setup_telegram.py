"""
텔레그램 봇 설정 도우미
처음 설정할 때 한 번만 실행하세요: python setup_telegram.py
"""
import asyncio
from telegram import Bot


async def get_chat_id(token: str):
    bot = Bot(token=token)
    print("봇에게 아무 메시지나 보내주세요 (텔레그램 앱에서)...")
    print("5초 후 업데이트를 확인합니다...")
    await asyncio.sleep(5)
    updates = await bot.get_updates()
    if not updates:
        print("메시지를 받지 못했습니다. 봇에게 메시지를 먼저 보낸 후 다시 실행하세요.")
        return
    chat_id = updates[-1].message.chat_id
    print(f"\n✅ 당신의 CHAT_ID: {chat_id}")
    print(f"\n.env 파일에 다음을 추가하세요:")
    print(f"TELEGRAM_CHAT_ID={chat_id}")


def main():
    print("=== 텔레그램 봇 설정 도우미 ===\n")
    print("1. https://t.me/BotFather 에서 봇을 만드세요")
    print("2. /newbot 명령으로 봇 생성 후 토큰을 받으세요\n")
    token = input("BOT_TOKEN을 입력하세요: ").strip()
    if not token:
        print("토큰이 입력되지 않았습니다.")
        return
    asyncio.run(get_chat_id(token))


if __name__ == "__main__":
    main()
