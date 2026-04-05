"""
위비티(Wevity) 공모전 크롤러
https://www.wevity.com/?class=contest&act=list&cid=6
"""
from bs4 import BeautifulSoup
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date
import re

BASE_URL = "https://www.wevity.com"
LIST_URL = "https://www.wevity.com/?class=contest&act=list&cid=6"


class WevityCrawler(BaseCrawler):
    source_name = "wevity"
    source_display = "위비티"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            resp = self.get(LIST_URL)
            soup = BeautifulSoup(resp.content, "lxml")

            # 위비티 공모전 목록 파싱
            items = soup.select("ul.list > li") or soup.select(".list-body li") or soup.select("li.item")

            if not items:
                # 대안 셀렉터 시도
                items = soup.select(".contest-list li") or soup.select(".clist li")

            for item in items[:40]:
                try:
                    # 제목
                    title_el = item.select_one("a.tit") or item.select_one(".tit") or item.select_one("strong")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)

                    # 링크
                    link_el = item.select_one("a[href]")
                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = BASE_URL + href
                    if not href:
                        href = LIST_URL

                    # 주최기관
                    org_el = item.select_one(".organ") or item.select_one(".host") or item.select_one("span.company")
                    organization = org_el.get_text(strip=True) if org_el else ""

                    # 마감일
                    date_el = item.select_one(".date") or item.select_one(".dday") or item.select_one("span.period")
                    deadline_str = date_el.get_text(strip=True) if date_el else ""
                    # D-7 형태에서 날짜 추출 시도
                    deadline = None
                    date_match = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", deadline_str)
                    if date_match:
                        deadline = parse_korean_date(date_match.group(1))

                    # 썸네일
                    img_el = item.select_one("img")
                    thumbnail = img_el.get("src", "") if img_el else ""
                    if thumbnail and not thumbnail.startswith("http"):
                        thumbnail = BASE_URL + thumbnail

                    category = classify_category(title)

                    results.append({
                        "title": title,
                        "organization": organization,
                        "category": category,
                        "source_site": self.source_name,
                        "source_url": href,
                        "original_url": href,
                        "deadline": deadline,
                        "start_date": None,
                        "prize": "",
                        "description": "",
                        "thumbnail": thumbnail,
                    })
                except Exception as e:
                    print(f"[위비티] 아이템 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"[위비티] 크롤링 오류: {e}")

        print(f"[위비티] {len(results)}개 수집")
        return results
