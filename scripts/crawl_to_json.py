"""
GitHub Actions에서 실행되는 크롤러 스크립트.
결과를 docs/data.json 으로 저장.
"""
import json
import time
import random
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

CATEGORY_KEYWORDS = {
    "AI/머신러닝":  ["ai", "인공지능", "머신러닝", "딥러닝", "llm", "gpt", "생성형"],
    "빅데이터":     ["빅데이터", "big data"],
    "데이터":       ["데이터", "data", "분석", "시각화"],
    "앱개발":       ["앱", "app", "ios", "android", "모바일", "flutter"],
    "웹개발":       ["웹", "web", "프론트엔드", "백엔드", "풀스택"],
    "IoT/임베디드": ["iot", "임베디드", "아두이노", "라즈베리", "하드웨어"],
    "게임/VR":      ["게임", "game", "vr", "ar", "메타버스", "unity"],
    "보안/해킹":    ["보안", "security", "해킹", "ctf", "취약점"],
    "블록체인":     ["블록체인", "blockchain", "nft", "web3"],
    "UI/UX":        ["ui", "ux", "디자인", "design", "figma"],
}

def classify(title):
    t = title.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in t for k in kws):
            return cat
    return "기타IT"

def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ["%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%y.%m.%d"]:
        try:
            return datetime.strptime(s[:10], fmt).strftime("%Y.%m.%d")
        except:
            continue
    return None

def days_left(deadline_str):
    if not deadline_str:
        return None
    try:
        d = datetime.strptime(deadline_str, "%Y.%m.%d")
        return (d - datetime.utcnow()).days
    except:
        return None

def get(url):
    time.sleep(random.uniform(0.8, 1.8))
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r

# ── 위비티 ──────────────────────────────────────────────
def crawl_wevity():
    results = []
    try:
        r = get("https://www.wevity.com/?class=contest&act=list&cid=6")
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")

        for item in soup.select(".list > li, ul.list > li")[:40]:
            try:
                a = item.select_one("a[href]")
                if not a:
                    continue
                title_el = a.select_one(".tit") or a.select_one("strong") or a
                title = title_el.get_text(strip=True)
                if not title:
                    continue

                href = a["href"]
                if not href.startswith("http"):
                    href = "https://www.wevity.com" + href

                org_el = item.select_one(".host, .organ, .company")
                org = org_el.get_text(strip=True) if org_el else ""

                date_el = item.select_one(".date, .dday, .period")
                date_str = date_el.get_text(strip=True) if date_el else ""
                m = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", date_str)
                deadline = parse_date(m.group(1)) if m else None

                results.append({
                    "title": title,
                    "organization": org,
                    "category": classify(title),
                    "source_site": "wevity",
                    "source_label": "위비티",
                    "url": href,
                    "deadline": deadline,
                    "days_left": days_left(deadline),
                })
            except:
                continue
    except Exception as e:
        print(f"[위비티] 오류: {e}")
    print(f"[위비티] {len(results)}개")
    return results

# ── 씽굿 ────────────────────────────────────────────────
def crawl_thinkgood():
    results = []
    urls = [
        "https://www.thinkgood.co.kr/competition/list",
        "https://www.thinkgood.co.kr/",
    ]
    for list_url in urls:
        try:
            r = get(list_url)
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "lxml")

            items = (
                soup.select(".competition-item, .contest-item, .list-item, .board-list li, ul.list li")
            )
            for item in items[:40]:
                try:
                    a = item.select_one("a[href]")
                    if not a:
                        continue
                    title_el = a.select_one("h3,.title,strong") or a
                    title = title_el.get_text(strip=True)
                    if not title or len(title) < 4:
                        continue

                    href = a["href"]
                    if not href.startswith("http"):
                        href = "https://www.thinkgood.co.kr" + href

                    date_el = item.select_one(".date,.deadline,.period")
                    date_str = date_el.get_text(strip=True) if date_el else ""
                    m = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", date_str)
                    deadline = parse_date(m.group(1)) if m else None

                    results.append({
                        "title": title,
                        "organization": "",
                        "category": classify(title),
                        "source_site": "thinkgood",
                        "source_label": "씽굿",
                        "url": href,
                        "deadline": deadline,
                        "days_left": days_left(deadline),
                    })
                except:
                    continue
            if results:
                break
        except Exception as e:
            print(f"[씽굿] 오류: {e}")
    print(f"[씽굿] {len(results)}개")
    return results

# ── 캠퍼스픽 ────────────────────────────────────────────
def crawl_campuspick():
    results = []
    try:
        r = get("https://campuspick.com/contest")
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.select(".item, .contest-item, ul.list li, .card")
        for item in items[:40]:
            try:
                a = item.select_one("a[href]")
                if not a:
                    continue
                title_el = a.select_one("strong,.title,p.name") or a
                title = title_el.get_text(strip=True)
                if not title or len(title) < 4:
                    continue

                href = a["href"]
                if not href.startswith("http"):
                    href = "https://campuspick.com" + href

                date_el = item.select_one(".date,.deadline,.period")
                date_str = date_el.get_text(strip=True) if date_el else ""
                m = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", date_str)
                deadline = parse_date(m.group(1)) if m else None

                results.append({
                    "title": title,
                    "organization": "",
                    "category": classify(title),
                    "source_site": "campuspick",
                    "source_label": "캠퍼스픽",
                    "url": href,
                    "deadline": deadline,
                    "days_left": days_left(deadline),
                })
            except:
                continue
    except Exception as e:
        print(f"[캠퍼스픽] 오류: {e}")
    print(f"[캠퍼스픽] {len(results)}개")
    return results

# ── 공모전박람회 ─────────────────────────────────────────
def crawl_gonmofair():
    results = []
    try:
        r = get("https://www.gonmofair.co.kr/module/contest/list.php")
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.select(".contest_list li, .list_wrap li, table.board tbody tr, ul.board_list li")
        for item in items[:40]:
            try:
                a = item.select_one("a[href]")
                if not a:
                    continue
                title = a.get_text(strip=True)
                if not title or len(title) < 4:
                    continue

                href = a["href"]
                if not href.startswith("http"):
                    href = "https://www.gonmofair.co.kr/" + href.lstrip("/")

                date_el = item.select_one(".date,td.date,.deadline")
                date_str = date_el.get_text(strip=True) if date_el else ""
                m = re.search(r"(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})", date_str)
                deadline = parse_date(m.group(1)) if m else None

                results.append({
                    "title": title,
                    "organization": "",
                    "category": classify(title),
                    "source_site": "gonmofair",
                    "source_label": "공모전박람회",
                    "url": href,
                    "deadline": deadline,
                    "days_left": days_left(deadline),
                })
            except:
                continue
    except Exception as e:
        print(f"[공모전박람회] 오류: {e}")
    print(f"[공모전박람회] {len(results)}개")
    return results

# ── 링커리어 ────────────────────────────────────────────
def crawl_linkareer():
    results = []
    try:
        r = requests.post(
            "https://api.linkareer.com/graphql",
            json={
                "query": """{ challengeList(filter:{type:CONTEST},
                  orderBy:{direction:DESC,field:CREATED_AT}, page:1, pageSize:50) {
                  challenges { id title organizationName applicationEndAt } } }"""
            },
            headers={**HEADERS, "Content-Type": "application/json",
                     "Origin": "https://linkareer.com",
                     "Referer": "https://linkareer.com/"},
            timeout=15,
        )
        challenges = r.json().get("data", {}).get("challengeList", {}).get("challenges", [])
        for c in challenges:
            deadline = parse_date((c.get("applicationEndAt") or "")[:10])
            results.append({
                "title": c.get("title", ""),
                "organization": c.get("organizationName", ""),
                "category": classify(c.get("title", "")),
                "source_site": "linkareer",
                "source_label": "링커리어",
                "url": f"https://linkareer.com/cover/{c['id']}",
                "deadline": deadline,
                "days_left": days_left(deadline),
            })
    except Exception as e:
        print(f"[링커리어] 오류: {e}")
    print(f"[링커리어] {len(results)}개")
    return results

# ── 메인 ────────────────────────────────────────────────
def main():
    all_items = []
    for fn in [crawl_linkareer, crawl_wevity, crawl_thinkgood, crawl_campuspick, crawl_gonmofair]:
        all_items.extend(fn())

    # 중복 제거 (같은 제목)
    seen = set()
    unique = []
    for item in all_items:
        key = item["title"].strip()[:30]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # 마감일 있는 것 먼저, 그 다음 마감일 없는 것
    unique.sort(key=lambda x: (
        x["days_left"] is None,
        x["days_left"] if x["days_left"] is not None else 9999
    ))

    output = {
        "updated": datetime.utcnow().strftime("%Y.%m.%d %H:%M UTC"),
        "total": len(unique),
        "contests": unique,
    }

    with open("docs/data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n총 {len(unique)}개 저장 완료 → docs/data.json")

if __name__ == "__main__":
    main()
