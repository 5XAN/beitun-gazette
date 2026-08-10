"""Dcard 台中板 - 以關鍵字篩選出好康/優惠相關討論

來源: https://www.dcard.tw/service/api/v2/forums/taichung/posts

注意: Dcard 有 Cloudflare 機器人防護,單純的 requests 呼叫經常會被擋下
(回傳 403)。此爬蟲會嘗試呼叫,若失敗則記錄警告並回傳空清單,不中斷整體排程。
若長期需要這個來源,建議改用瀏覽器自動化(如 Playwright)或官方合作管道。
"""
import logging

from config import DEAL_KEYWORDS, DISTRICT_KEYWORDS
from models import Item
from scrapers.base import BaseScraper

API_URL = "https://www.dcard.tw/service/api/v2/forums/taichung/posts"
POST_URL = "https://www.dcard.tw/f/taichung/p/{id}"

logger = logging.getLogger(__name__)


class DcardTaichungScraper(BaseScraper):
    source = "dcard"

    def __init__(self, district_keywords=DISTRICT_KEYWORDS):
        super().__init__()
        self.district_keywords = district_keywords

    def fetch(self, pages: int = 1, keywords=None):
        keywords = keywords or DEAL_KEYWORDS
        items = []
        before = None
        for _ in range(pages):
            params = {"limit": 30}
            if before:
                params["before"] = before
            try:
                resp = self.get(
                    API_URL,
                    params=params,
                    headers={"Accept": "application/json", "Referer": "https://www.dcard.tw/f/taichung"},
                )
                posts = resp.json()
            except Exception as exc:  # Cloudflare 403 / 非 JSON 回應等
                logger.warning("Dcard 爬取失敗,略過此來源: %s", exc)
                break

            if not posts:
                break
            for post in posts:
                title = post.get("title", "")
                if not any(kw in title for kw in keywords):
                    continue
                if self.district_keywords and not any(kw in title for kw in self.district_keywords):
                    continue
                items.append(
                    Item(
                        source=self.source,
                        category="社群情報",
                        title=title,
                        description=post.get("excerpt", ""),
                        url=POST_URL.format(id=post.get("id")),
                        published_at=post.get("createdAt", ""),
                    )
                )
            before = posts[-1].get("id")
        return items
