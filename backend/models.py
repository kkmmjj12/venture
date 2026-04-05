from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    organization = Column(String(200))
    category = Column(String(100))           # AI, 빅데이터, 데이터분석 등
    source_site = Column(String(100))        # linkareer, wevity, thinkgood 등
    source_url = Column(String(1000))        # 원본 공모전 URL
    original_url = Column(String(1000))      # 공모전 공식 URL (있는 경우)
    deadline = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    prize = Column(String(500))              # 시상내역
    description = Column(Text)
    thumbnail = Column(String(1000))
    is_active = Column(Boolean, default=True)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        from datetime import timezone
        now = datetime.utcnow()
        days_left = None
        deadline_str = None
        if self.deadline:
            delta = self.deadline - now
            days_left = delta.days
            deadline_str = self.deadline.strftime("%Y.%m.%d")

        return {
            "id": self.id,
            "title": self.title,
            "organization": self.organization,
            "category": self.category,
            "source_site": self.source_site,
            "source_url": self.source_url,
            "original_url": self.original_url,
            "deadline": deadline_str,
            "days_left": days_left,
            "prize": self.prize,
            "description": self.description,
            "thumbnail": self.thumbnail,
            "is_active": self.is_active,
            "crawled_at": self.crawled_at.strftime("%Y.%m.%d") if self.crawled_at else None,
        }
