"""
공모전박람회 크롤러
https://www.gonmofair.co.kr/
"""
from bs4 import BeautifulSoup
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date
import re

BASE_URL = "https://www.gonmofair.co.kr"
LIST_URL = "https://www.gonmofair.co.kr/module/contest/list.php"


class GonmofairCrawler(BaseCrawler):
    source_name = "gonmofair"
    source_display = "공모전박람회"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            resp = self.get(LIST_URL)
            soup = BeautifulSoup(resp.content, "lxml")

            items = (
                soup.select(".contest_list li")
                or soup.select(".list_wrap li")
                or soup.select("ul.board_list li")
                or soup.select(".item_list li")
                or soup.select("table.board tbody tr")
            )

            for item in items[:40]:
                try:
                    title_el = item.select_one("a") or item.select_one(".tit") or item.select_one("td.title")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue

                    link_el = item.select_one("a[href]")
                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = BASE_URL + "/" + href.lstrip("/")
                    if not href:
                        href = LIST_URL

                    org_el = item.select_one(".host") or item.select_one(".organizer") or item.select_one("td.host")
                    organization = org_el.get_text(strip=True) if org_el else ""

                    date_el = item.select_one(".date") or item.select_one("td.date") or item.select_one(".deadline")
                    deadline_str = date_el.get_text(strip=True) if date_el else ""
                    deadline = None
                    date_match = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", deadline_str)
                    if date_match:
                        deadline = parse_korean_date(date_match.group(1))

                    img_el = item.select_one("img")
                    thumbnail = img_el.get("src", "") if img_el else ""
                    if thumbnail and not thumbnail.startswith("http"):
                        thumbnail = BASE_URL + "/" + thumbnail.lstrip("/")

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
                    print(f"[공모전박람회] 아이템 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"[공모전박람회] 크롤링 오류: {e}")

        print(f"[공모전박람회] {len(results)}개 수집")
        return results
