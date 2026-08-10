"""台中市政府體系網站共用的公告列表樣板。

市府本部與各局處(經濟發展局、社會局...等)網站用的是同一套 CMS,清單頁固定是
section.listTable > table > tbody > tr,每列有 2~3 個 td.title:標題連結、
(可能有)主政機關、日期。子類別只要指定 list_url/source/category 即可重用解析邏輯。
"""
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import Item
from scrapers.base import BaseScraper


class TaichungGovListScraper(BaseScraper):
    list_url: str = ""
    category: str = "政策公告"
    keywords: list | None = None  # 設定後只保留標題含關鍵字的公告,避免抓到一般新聞大雜燴
    exclude_keywords: list | None = None  # 設定後,標題含這些字就算命中 keywords 也排除

    def fetch(self, pages: int = 3):
        if not self.list_url:
            raise NotImplementedError("子類別必須設定 list_url")
        items = []
        for page in range(1, pages + 1):
            resp = self.get(self.list_url, params={"Page": page, "PageSize": 30})
            soup = BeautifulSoup(resp.text, "lxml")
            # 不同局處網站的外層 section class 不一致(listTable / list 等),
            # 用 td.title 本身當作可靠的錨點,不依賴外層容器的 class 名稱。
            rows = soup.select("table tr:has(td.title)")
            if not rows:
                break
            for row in rows:
                cells = row.select("td.title")
                if not cells:
                    continue
                link = cells[0].find("a")
                if not link or not link.get("href"):
                    continue
                title = link.get_text(strip=True)
                if self.keywords and not any(kw in title for kw in self.keywords):
                    continue
                if self.exclude_keywords and any(kw in title for kw in self.exclude_keywords):
                    continue
                agency = cells[1].get_text(strip=True) if len(cells) >= 3 else ""
                date = cells[-1].get_text(strip=True) if len(cells) >= 2 else ""
                items.append(
                    Item(
                        source=self.source,
                        category=self.category,
                        title=title,
                        description=agency,
                        url=urljoin(self.list_url, link["href"]),
                        published_at=date,
                    )
                )
        return items
