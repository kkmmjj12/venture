"""
씽굿(Thinkcontest) 공모전 크롤러
https://www.thinkcontest.com
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date

BASE_URL  = "https://www.thinkcontest.com"
LIST_URL  = "https://www.thinkcontest.com/thinkgood/user/contest/list.do"
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Referer": BASE_URL,
}


class ThinkgoodCrawler(BaseCrawler):
    source_name    = "thinkgood"
    source_display = "씽굿"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "lxml")

            # 씽굿 리스트 아이템 — 여러 셀렉터 시도
            items = (
                soup.select("ul.contest_list li")
                or soup.select(".contest_list li")
                or soup.select(".list_con li")
                or soup.select(".board_list li")
                or soup.select("li.item")
                or soup.select(".con_list li")
            )

            for item in items[:40]:
                try:
                    # 제목
                    title_el = (
                        item.select_one(".tit")
                        or item.select_one("strong.name")
                        or item.select_one("a.name")
                        or item.select_one("h3")
                        or item.select_one(".con_title")
                        or item.select_one(".subject")
                    )
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    if not title:
                        continue

                    # 링크 — contest_pk 포함 URL 우선
                    link_el = item.select_one("a[href*='contest_pk']") or item.select_one("a[href]")
                    href = link_el["href"] if link_el else ""
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = BASE_URL + href

                    # 주최기관
                    org_el = (
                        item.select_one(".host")
                        or item.select_one(".organ")
                        or item.select_one(".organizer")
                        or item.select_one(".company")
                    )
                    organization = org_el.get_text(strip=True) if org_el else ""

                    # 마감일
                    date_el = (
                        item.select_one(".date")
                        or item.select_one(".deadline")
                        or item.select_one(".period")
                    )
                    deadline = None
                    if date_el:
                        date_text = date_el.get_text(strip=True)
                        m = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", date_text)
                        if m:
                            deadline = parse_korean_date(m.group(1))

                    # 썸네일
                    img_el = item.select_one("img")
                    thumbnail = img_el.get("src", "") if img_el else ""
                    if thumbnail and not thumbnail.startswith("http"):
                        thumbnail = BASE_URL + thumbnail

                    results.append({
                        "title":        title,
                        "organization": organization,
                        "category":     classify_category(title),
                        "source_site":  self.source_name,
                        "source_url":   href,
                        "original_url": href,
                        "deadline":     deadline,
                        "start_date":   None,
                        "prize":        "",
                        "description":  "",
                        "thumbnail":    thumbnail,
                    })
                except Exception as e:
                    print(f"[씽굿] 아이템 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"[씽굿] 크롤링 오류: {e}")

        print(f"[씽굿] {len(results)}개 수집")
        return results
