import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

NOTIFY_HOUR = int(os.getenv("NOTIFY_HOUR", "9"))
NOTIFY_MINUTE = int(os.getenv("NOTIFY_MINUTE", "0"))

DB_PATH = os.path.join(os.path.dirname(__file__), "contests.db")

# 컴퓨터공학 관련 키워드 필터 (이 단어가 제목/분야에 포함된 공모전 우선)
CS_KEYWORDS = [
    "IT", "SW", "AI", "인공지능", "소프트웨어", "앱", "웹", "해킹", "보안",
    "데이터", "알고리즘", "개발", "프로그래밍", "코딩", "게임", "로봇",
    "IoT", "블록체인", "클라우드", "빅데이터", "머신러닝", "딥러닝", "UX", "UI",
    "ICT", "디지털", "스타트업", "창업", "핀테크", "정보",
]
