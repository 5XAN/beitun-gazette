import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Item:
    source: str  # 資料來源代碼,如 taichung_gov / tcpass / opendata / ptt / dcard
    category: str  # 分類,如 政策公告 / 店家優惠 / 開放資料 / 社群情報
    title: str
    url: str
    description: str = ""
    store_name: str = ""
    date_start: str = ""
    date_end: str = ""
    published_at: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def id(self) -> str:
        return hashlib.sha1(f"{self.source}:{self.url}".encode("utf-8")).hexdigest()
