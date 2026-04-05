"""
씽굿(Thinkgood) 공모전 크롤러
https://www.thinkgood.co.kr/
"""
from bs4 import BeautifulSoup
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date
import re

BASE_URL = "https://www.thinkgood.co.kr"
LIST_URL = "https://www.thinkgood.co.kr/competition/list"


class ThinkgoodCrawler(BaseCrawler):
    source_name = "thinkgood"
    source_display = "씽굿"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            resp = self.get(LIST_URL)
            soup = BeautifulSoup(resp.content, "lxml")

            # 씽굿 공모전 목록 파싱
            items = (
                soup.select(".competition-item")
                or soup.select(".contest-item")
                or soup.select(".board-list li")
                or soup.select(".list-item")
            )

            for item in items[:40]:
                try:
                    title_el = item.select_one("h3") or item.select_one(".title") or item.select_one("a.name")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)

                    link_el = item.select_one("a[href]")
                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = BASE_URL + href
                    if not href:
                        href = LIST_URL

                    org_el = item.select_one(".host") or item.select_one(".organizer") or item.select_one(".company")
                    organization = org_el.get_text(strip=True) if org_el else ""

                    date_el = item.select_one(".deadline") or item.select_one(".date") or item.select_one(".period")
                    deadline_str = date_el.get_text(strip=True) if date_el else ""
                    deadline = None
                    date_match = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", deadline_str)
                    if date_match:
                        deadline = parse_korean_date(date_match.group(1))

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
                    print(f"[씽굿] 아이템 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"[씽굿] 크롤링 오류: {e}")

        print(f"[씽굿] {len(results)}개 수집")
        return results
