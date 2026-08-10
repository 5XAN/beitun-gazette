"""台中通 - 店家優惠

來源: https://tcpass.taichung.gov.tw/coupon/index
分頁機制: 表單 POST 到 /coupon/query,page 參數從 0 開始。
permanentDistrict 用行政區代碼篩選(北屯區 = 114,全區 = 000)。
"""
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from models import Item
from scrapers.base import BaseScraper

INDEX_URL = "https://tcpass.taichung.gov.tw/coupon/index"
QUERY_URL = "https://tcpass.taichung.gov.tw/coupon/query"

DISTRICT_ALL = "000"
DISTRICT_BEITUN = "114"


class TcpassCouponScraper(BaseScraper):
    source = "tcpass"

    def __init__(self, district: str = DISTRICT_BEITUN):
        super().__init__()
        self.district = district

    def fetch(self, pages: int = 3):
        resp = self.get(INDEX_URL)
        soup = BeautifulSoup(resp.text, "lxml")
        csrf_input = soup.select_one('input[name="_csrf"]')
        csrf_token = csrf_input["value"] if csrf_input else ""

        items = []
        for page in range(pages):
            data = {
                "page": str(page),
                "pageSize": "30",
                "permanentDistrict": self.district,
                "category": "",
                "keyword": "",
                "posterDate": "",
                "closeDate": "",
                "_csrf": csrf_token,
            }
            resp = self.post(QUERY_URL, data=data)
            soup = BeautifulSoup(resp.text, "lxml")
            page_items = self._parse(soup)
            if not page_items:
                break
            items.extend(page_items)
        return items

    def _parse(self, soup: BeautifulSoup):
        items = []
        for li in soup.select("div.discount_list li"):
            title_el = li.select_one("p.title")
            if not title_el:
                continue
            txt_el = li.select_one("p.txt")
            date_el = li.select_one("p.date")
            link_el = li.select_one("a.more")

            date_start, date_end = "", ""
            if date_el:
                date_text = date_el.get_text(strip=True)
                if "~" in date_text:
                    date_start, date_end = (p.strip() for p in date_text.split("~", 1))
                else:
                    date_start = date_text

            title = title_el.get_text(strip=True)
            items.append(
                Item(
                    source=self.source,
                    category="店家優惠",
                    title=title,
                    description=txt_el.get_text(strip=True) if txt_el else "",
                    store_name=title,
                    url=urljoin(INDEX_URL, link_el["href"]) if link_el and link_el.get("href") else INDEX_URL,
                    date_start=date_start,
                    date_end=date_end,
                )
            )
        return items
