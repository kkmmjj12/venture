"""
위비티 (wevity.com) 공모전 스크래퍼
- IT/SW 카테고리: c=6
- 전체 목록:     c=1
"""
from .base import BaseScraper, fetch, make_uid, is_cs_related

BASE_URL = "https://www.wevity.com"

# 카테고리: IT/SW(6), 기획·아이디어(2), 디자인(3), 과학·공학(7)
CATEGORY_PARAMS = {
    "IT/SW": "6",
    "기획·아이디어": "2",
    "과학·공학": "7",
}


class WevityScraper(BaseScraper):
    source_name = "위비티(wevity.com)"

    def scrape(self) -> list[dict]:
        results = []
        for cat_name, cat_id in CATEGORY_PARAMS.items():
            url = f"{BASE_URL}/?c=find&s={cat_id}&gp=1"
            soup = fetch(url)
            if not soup:
                continue
            items = self._parse(soup, cat_name)
            results.extend(items)
            print(f"  [wevity] {cat_name}: {len(items)}개")
        return results

    def _parse(self, soup, cat_name: str) -> list[dict]:
        contests = []
        # wevity 목록: <ul class="list"> 안의 <li> 태그
        items = soup.select("ul.list > li") or soup.select(".list-item") or soup.select("li.item")

        # fallback: 링크 패턴으로 탐색
        if not items:
            items = soup.select("a[href*='detail']")

        for item in items:
            try:
                # 제목
                title_el = (
                    item.select_one(".tit") or
                    item.select_one(".title") or
                    item.select_one("strong") or
                    item.select_one("h3")
                )
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title:
                    continue

                # URL
                link_el = item.select_one("a") or item
                href = link_el.get("href", "")
                if href and not href.startswith("http"):
                    href = BASE_URL + "/" + href.lstrip("/")

                # 마감일
                deadline = ""
                for sel in [".date", ".deadline", ".d-day", ".period"]:
                    dl = item.select_one(sel)
                    if dl:
                        deadline = dl.get_text(strip=True)
                        break

                # 주최
                organizer = ""
                for sel in [".host", ".organizer", ".org"]:
                    org = item.select_one(sel)
                    if org:
                        organizer = org.get_text(strip=True)
                        break

                uid = make_uid("wevity", href or title)
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
                print(f"  [wevity parse error] {e}")
                continue
        return contests
