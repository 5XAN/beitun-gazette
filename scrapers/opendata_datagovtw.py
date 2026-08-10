"""政府資料開放平臺 (data.gov.tw) - 台中相關資料集搜尋

需要 API Key: 至 https://data.gov.tw 註冊帳號後,於「會員中心」申請 API Key,
並設定環境變數 DATA_GOV_TW_API_KEY。

注意: data.gov.tw 的 v2 API 回應格式官方文件揭露有限,以下解析採取寬鬆、
容錯的寫法(多種可能欄位名稱都會嘗試),第一次串接後建議印出原始 JSON
確認實際欄位,再視需要調整 _parse_dataset()。
"""
from models import Item
from scrapers.base import BaseScraper

API_URL = "https://data.gov.tw/api/v2/rest/dataset"
DATASET_PAGE_URL = "https://data.gov.tw/dataset/{id}"


class OpenDataScraper(BaseScraper):
    source = "opendata"

    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key

    def fetch(self, pages: int = 1, keyword: str = "台中"):
        if not self.api_key:
            raise RuntimeError(
                "缺少 DATA_GOV_TW_API_KEY,請至 https://data.gov.tw 申請 API Key 後"
                "設定環境變數,例如: set DATA_GOV_TW_API_KEY=your_key"
            )
        items = []
        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}
        for page in range(1, pages + 1):
            resp = self.post(API_URL, json={"q": keyword, "page": page}, headers=headers)
            payload = resp.json()
            datasets = self._extract_datasets(payload)
            if not datasets:
                break
            for ds in datasets:
                item = self._parse_dataset(ds)
                if item:
                    items.append(item)
        return items

    @staticmethod
    def _extract_datasets(payload: dict):
        result = payload.get("result", payload)
        for key in ("datasets", "data", "results"):
            if isinstance(result.get(key), list):
                return result[key]
        return []

    def _parse_dataset(self, ds: dict):
        ds_id = ds.get("id") or ds.get("DatasetID") or ""
        title = ds.get("title") or ds.get("DatasetName") or ""
        if not title:
            return None
        description = ds.get("description") or ds.get("DatasetDescription") or ""
        category = ds.get("category") or ds.get("CategoryName") or "開放資料"
        url = DATASET_PAGE_URL.format(id=ds_id) if ds_id else API_URL
        return Item(
            source=self.source,
            category=f"開放資料/{category}",
            title=title,
            description=description,
            url=url,
        )
