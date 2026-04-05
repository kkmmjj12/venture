import requests
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# IT 카테고리 키워드 매핑
CATEGORY_KEYWORDS = {
    "AI/머신러닝": ["ai", "인공지능", "머신러닝", "딥러닝", "machine learning", "deep learning", "neural", "gpt", "llm"],
    "빅데이터": ["빅데이터", "big data", "데이터 분석", "데이터분석"],
    "데이터": ["데이터", "data", "통계", "분석"],
    "앱개발": ["앱", "app", "ios", "android", "모바일", "flutter", "react native"],
    "웹개발": ["웹", "web", "frontend", "backend", "프론트엔드", "백엔드", "풀스택"],
    "IoT/임베디드": ["iot", "임베디드", "embedded", "아두이노", "라즈베리", "하드웨어"],
    "게임/VR": ["게임", "game", "vr", "ar", "메타버스", "unity", "unreal"],
    "보안/해킹": ["보안", "security", "해킹", "hacking", "ctf", "암호화", "취약점"],
    "블록체인": ["블록체인", "blockchain", "nft", "web3", "crypto", "defi"],
    "UI/UX": ["ui", "ux", "디자인", "design", "figma", "프로토타입"],
}


def classify_category(title: str, description: str = "") -> str:
    """제목과 설명으로 카테고리 자동 분류"""
    text = (title + " " + (description or "")).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "기타IT"


def parse_korean_date(date_str: str) -> datetime | None:
    """한국식 날짜 문자열 파싱"""
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = [
        "%Y.%m.%d",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y년 %m월 %d일",
        "%Y.%m.%d.",
        "%y.%m.%d",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:10] if len(date_str) > 10 else date_str, fmt)
        except ValueError:
            continue
    return None


class BaseCrawler(ABC):
    source_name: str = "unknown"
    source_display: str = "Unknown"

    def get(self, url: str, **kwargs) -> requests.Response:
        time.sleep(random.uniform(0.5, 1.5))
        resp = requests.get(url, headers=HEADERS, timeout=15, **kwargs)
        resp.raise_for_status()
        return resp

    @abstractmethod
    def crawl(self) -> List[Dict]:
        """크롤링 실행, Competition dict 리스트 반환"""
        pass
