"""
캠퍼스픽 공모전 크롤러
https://campuspick.com/contest
"""
from bs4 import BeautifulSoup
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date
import re

BASE_URL = "https://campuspick.com"
LIST_URL = "https://campuspick.com/contest"


class CampuspickCrawler(BaseCrawler):
    source_name = "campuspick"
    source_display = "캠퍼스픽"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            resp = self.get(LIST_URL)
            soup = BeautifulSoup(resp.content, "lxml")

            items = (
                soup.select(".contest-item")
                or soup.select(".item")
                or soup.select("ul.list li")
                or soup.select(".card-item")
                or soup.select("li[class*='contest']")
            )

            for item in items[:40]:
                try:
                    title_el = item.select_one("strong") or item.select_one(".title") or item.select_one("h3") or item.select_one("p.name")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)
                    if not title:
                        continue

                    link_el = item.select_one("a[href]")
                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = BASE_URL + href
                    if not href:
                        href = LIST_URL

                    org_el = item.select_one(".host") or item.select_one(".organizer") or item.select_one("span.company")
                    organization = org_el.get_text(strip=True) if org_el else ""

                    date_el = item.select_one(".date") or item.select_one(".deadline") or item.select_one("span.period")
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
                    print(f"[캠퍼스픽] 아이템 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"[캠퍼스픽] 크롤링 오류: {e}")

        print(f"[캠퍼스픽] {len(results)}개 수집")
        return results
