"""
링커리어 공모전 크롤러
https://linkareer.com/list/contest
"""
import requests
import json
from typing import List, Dict
from backend.crawlers.base import BaseCrawler, classify_category, parse_korean_date


GRAPHQL_URL = "https://api.linkareer.com/graphql"

QUERY = """
query ChallengeList($filter: ChallengeFilterInput, $orderBy: ChallengeOrderByInput, $page: Int, $pageSize: Int) {
  challengeList(filter: $filter, orderBy: $orderBy, page: $page, pageSize: $pageSize) {
    totalCount
    challenges {
      id
      title
      organizationName
      applicationEndAt
      applicationStartAt
      coverImageUrl
      prize
      categories {
        name
      }
      url
    }
  }
}
"""

GRAPHQL_PAYLOAD = {
    "operationName": "ChallengeList",
    "query": QUERY,
    "variables": {
        "filter": {"type": "CONTEST"},
        "orderBy": {"direction": "DESC", "field": "CREATED_AT"},
        "page": 1,
        "pageSize": 50,
    }
}


class LinkareerCrawler(BaseCrawler):
    source_name = "linkareer"
    source_display = "링커리어"

    def crawl(self) -> List[Dict]:
        results = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://linkareer.com",
                "Referer": "https://linkareer.com/",
            }
            resp = requests.post(
                GRAPHQL_URL,
                json=GRAPHQL_PAYLOAD,
                headers=headers,
                timeout=15
            )
            data = resp.json()
            challenges = data.get("data", {}).get("challengeList", {}).get("challenges", [])

            for item in challenges:
                title = item.get("title", "")
                cats = item.get("categories") or []
                cat_text = " ".join(c.get("name", "") for c in cats)
                category = classify_category(title, cat_text)

                deadline = parse_korean_date(
                    (item.get("applicationEndAt") or "")[:10]
                )
                start_date = parse_korean_date(
                    (item.get("applicationStartAt") or "")[:10]
                )

                comp_id = item.get("id", "")
                source_url = f"https://linkareer.com/cover/{comp_id}" if comp_id else "https://linkareer.com/list/contest"

                results.append({
                    "title": title,
                    "organization": item.get("organizationName", ""),
                    "category": category,
                    "source_site": self.source_name,
                    "source_url": source_url,
                    "original_url": source_url,
                    "deadline": deadline,
                    "start_date": start_date,
                    "prize": item.get("prize", ""),
                    "description": "",
                    "thumbnail": item.get("coverImageUrl", ""),
                })
        except Exception as e:
            print(f"[링커리어] 크롤링 오류: {e}")

        print(f"[링커리어] {len(results)}개 수집")
        return results
