"""
링커리어 공모전 크롤러
https://linkareer.com/list/contest
"""
import requests
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date

GRAPHQL_URL = "https://api.linkareer.com/graphql"

QUERY = """
{
  activities(filterBy: {activityTypeID: 1}) {
    nodes {
      id
      title
      organizationName
      homepageURL
      posterImage { url }
      categories { name }
    }
  }
}
"""


class LinkareerCrawler(BaseCrawler):
    source_name    = "linkareer"
    source_display = "링커리어"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            headers = {
                "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Accept":       "application/json",
                "Origin":       "https://linkareer.com",
                "Referer":      "https://linkareer.com/list/contest",
            }
            resp  = requests.post(GRAPHQL_URL, json={"query": QUERY}, headers=headers, timeout=15)
            data  = resp.json()
            nodes = data.get("data", {}).get("activities", {}).get("nodes", [])

            for item in nodes:
                title = item.get("title", "").strip()
                if not title:
                    continue

                comp_id      = str(item.get("id", ""))
                # 링커리어 공모전 상세 페이지
                linkareer_url = f"https://linkareer.com/activity/{comp_id}" if comp_id else "https://linkareer.com/list/contest"

                cats     = item.get("categories") or []
                cat_text = " ".join(c.get("name", "") for c in cats)
                category = classify_category(title, cat_text)

                poster   = (item.get("posterImage") or {}).get("url", "")
                homepage = item.get("homepageURL", "") or ""

                results.append({
                    "title":        title,
                    "organization": item.get("organizationName", ""),
                    "category":     category,
                    "source_site":  self.source_name,
                    "source_url":   linkareer_url,   # 링커리어 상세 페이지
                    "original_url": homepage or linkareer_url,
                    "deadline":     None,
                    "start_date":   None,
                    "prize":        "",
                    "description":  "",
                    "thumbnail":    poster,
                })

        except Exception as e:
            print(f"[링커리어] 크롤링 오류: {e}")

        print(f"[링커리어] {len(results)}개 수집")
        return results
