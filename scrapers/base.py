import hashlib
import requests
from bs4 import BeautifulSoup
from config import CS_KEYWORDS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def make_uid(source: str, identifier: str) -> str:
    return hashlib.md5(f"{source}:{identifier}".encode()).hexdigest()


def is_cs_related(text: str) -> bool:
    text_upper = text.upper()
    return any(kw.upper() in text_upper for kw in CS_KEYWORDS)


def fetch(url: str, **kwargs) -> BeautifulSoup | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, **kwargs)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return BeautifulSoup(resp.text, "lxml")
    except Exception as e:
        print(f"[FETCH ERROR] {url}: {e}")
        return None


class BaseScraper:
    source_name: str = ""

    def scrape(self) -> list[dict]:
        raise NotImplementedError
