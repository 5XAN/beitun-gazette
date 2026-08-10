import ssl
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.util.ssl_ import create_urllib3_context

from config import REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT, USER_AGENT


class RelaxedX509Adapter(HTTPAdapter):
    """部分 .gov.tw 網站的憑證缺少 Subject Key Identifier 擴充欄位,不符合
    Python 3.13 / OpenSSL 3.2 起預設開啟的嚴格 X.509 規範檢查(VERIFY_X509_STRICT)。
    這裡只關閉該項額外的嚴格性檢查,憑證鏈、有效期限、主機名稱仍照常驗證。
    """

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context()
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        kwargs["ssl_context"] = context
        super().init_poolmanager(*args, **kwargs)


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    adapter = RelaxedX509Adapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class BaseScraper:
    """共用的 session、逾時設定與請求間隔,避免對目標站造成負擔。"""

    source: str = "base"

    def __init__(self):
        self.session = make_session()

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY_SECONDS)
        return resp

    def post(self, url, **kwargs):
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        resp = self.session.post(url, **kwargs)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY_SECONDS)
        return resp

    def fetch(self, pages: int = 1):
        raise NotImplementedError
