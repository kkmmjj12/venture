"""
씽굿 (thinkcontest.com) 공모전 스크래퍼
- IT/SW 카테고리 페이지 사용
"""
from .base import BaseScraper, fetch, make_uid, is_cs_related

BASE_URL = "https://www.thinkcontest.com"

CATEGORIES = {
    "IT/SW": f"{BASE_URL}/Contest/list/it/0/0/1",
    "과학·기술": f"{BASE_URL}/Contest/list/science/0/0/1",
    "창업·아이디어": f"{BASE_URL}/Contest/list/startup/0/0/1",
}


class ThinkcontestScraper(BaseScraper):
    source_name = "씽굿(thinkcontest.com)"

    def scrape(self) -> list[dict]:
        results = []
        for cat_name, url in CATEGORIES.items():
            soup = fetch(url)
            if not soup:
                continue
            items = self._parse(soup, cat_name)
            results.extend(items)
            print(f"  [thinkcontest] {cat_name}: {len(items)}개")
        return results

    def _parse(self, soup, cat_name: str) -> list[dict]:
        contests = []
        # 씽굿 목록 카드
        items = (
            soup.select(".list_wrap li") or
            soup.select(".contest_list li") or
            soup.select("ul.list li") or
            soup.select(".item_box")
        )

        for item in items:
            try:
                title_el = (
                    item.select_one(".tit") or
                    item.select_one(".title") or
                    item.select_one("strong") or
                    item.select_one("p.name")
                )
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title:
                    continue

                link_el = item.select_one("a")
                href = link_el.get("href", "") if link_el else ""
                if href and not href.startswith("http"):
                    href = BASE_URL + href

                deadline = ""
                for sel in [".date", ".deadline", ".dday", ".period"]:
                    dl = item.select_one(sel)
                    if dl:
                        deadline = dl.get_text(strip=True)
                        break

                organizer = ""
                for sel in [".host", ".organizer", ".company"]:
                    org = item.select_one(sel)
                    if org:
                        organizer = org.get_text(strip=True)
                        break

                uid = make_uid("thinkcontest", href or title)
                contests.append({
                    "uid": uid,
                    "title": title,
                    "url": href,
                    "organizer": organizer,
                    "deadline": deadline,
                    "category": cat_name,
                    "source": self.source_name,
                    "is_cs": is_cs_related(title + " " + cat_name),
                })
            except Exception as e:
                print(f"  [thinkcontest parse error] {e}")
                continue
        return contests
