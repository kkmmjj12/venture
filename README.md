# Venture 🚀

> 캠퍼스 밖으로 — 컴퓨터공학 재학생을 위한 공모전 자동 수집 + 텔레그램 일일 알림 봇

## 기능
- **자동 크롤링**: 위비티(wevity.com), 씽굿(thinkcontest.com) 매일 수집
- **중복 제거**: SQLite로 이미 알림된 공모전 재전송 없음
- **CS 우선 필터**: IT/SW/AI/개발 관련 공모전 상단 배치 (💻)
- **GitHub Actions**: 서버 없이 매일 오전 9시(KST) 자동 실행

## 텔레그램 알림 예시
```
🚀 Venture | 오늘의 신규 공모전 (5건)

💻 2024 AI 아이디어 해커톤
   주최: 과학기술정보통신부  |  마감: 2024.05.31
   🔗 바로가기

📋 제15회 대학생 창업경진대회
   주최: 중소벤처기업부  |  마감: 2024.06.15
   🔗 바로가기
```

## 빠른 시작

### 1. 텔레그램 봇 만들기
1. 텔레그램에서 [@BotFather](https://t.me/BotFather) 검색
2. `/newbot` 명령 → 봇 이름: `Venture` → **토큰** 복사
3. 봇에게 아무 메시지 보내기

### 2. GitHub Secrets 설정
레포 → Settings → Secrets and variables → Actions → New repository secret

| 이름 | 값 |
|------|-----|
| `TELEGRAM_BOT_TOKEN` | BotFather에서 받은 토큰 |
| `TELEGRAM_CHAT_ID` | 내 채팅 ID (`setup_telegram.py`로 확인) |

### 3. 로컬 실행 (선택)
```bash
pip install -r requirements.txt
cp .env.example .env  # 값 입력 후
python main.py --now  # 즉시 1회 테스트
python main.py        # 스케줄러 모드
```

### 4. CHAT_ID 확인 방법
```bash
python setup_telegram.py
```

## GitHub Actions 스케줄
- **자동**: 매일 KST 09:00 (UTC 00:00)
- **수동**: Actions 탭 → `Venture Daily Crawl` → `Run workflow`

## 스크래핑 대상 사이트
| 사이트 | 카테고리 |
|--------|---------|
| [위비티](https://www.wevity.com) | IT/SW, 기획·아이디어, 과학·공학 |
| [씽굿](https://www.thinkcontest.com) | IT/SW, 과학·기술, 창업·아이디어 |

## 사이트 추가 방법
`scrapers/` 폴더에 `base.py`를 상속하는 파일 추가 후 `scrapers/__init__.py`의 `ALL_SCRAPERS`에 등록
