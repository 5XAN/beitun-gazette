import argparse
import logging

from config import DATA_GOV_TW_API_KEY
from database import init_db, upsert_items
from scrapers.beitun_office import BeitunOfficeScraper
from scrapers.dcard_taichung import DcardTaichungScraper
from scrapers.gov_announcements import GovNewsScraper
from scrapers.gov_subsidy import GovSubsidyScraper
from scrapers.opendata_datagovtw import OpenDataScraper
from scrapers.tcpass_coupon import TcpassCouponScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 這些是真正符合「好康」且已限縮到北屯的來源,`--source all` 預設只跑這些。
# - beitun_office / tcpass: 直接鎖定北屯(區公所公告、店家優惠 district=114)
# - subsidy: 經濟發展局補助是全市性的,北屯居民同樣適用,保留當作補充
# - dcard: 城市看板,靠標題同時比對好康關鍵字 + 「北屯」來限縮
SCRAPERS = {
    "beitun_office": lambda: BeitunOfficeScraper(),
    "tcpass": lambda: TcpassCouponScraper(),
    "subsidy": lambda: GovSubsidyScraper(),
    "opendata": lambda: OpenDataScraper(api_key=DATA_GOV_TW_API_KEY),
    "dcard": lambda: DcardTaichungScraper(),
}

# 一般市政新聞,大雜燴、非好康,只有明確指定才會執行,不包含在 `all` 裡。
EXTRA_SCRAPERS = {
    "news": lambda: GovNewsScraper(),
}

ALL_SCRAPERS = {**SCRAPERS, **EXTRA_SCRAPERS}


def run(sources, pages):
    init_db()
    total_new = 0
    for name in sources:
        factory = ALL_SCRAPERS.get(name)
        if not factory:
            logger.warning("未知的來源: %s", name)
            continue
        logger.info("開始爬取: %s", name)
        try:
            scraper = factory()
            items = scraper.fetch(pages=pages)
        except Exception as exc:
            logger.error("爬取 %s 失敗: %s", name, exc)
            continue
        new_count = upsert_items(items)
        total_new += new_count
        logger.info("%s 完成,共取得 %d 筆,新增 %d 筆", name, len(items), new_count)
    logger.info("全部完成,共新增 %d 筆資料", total_new)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="台中好康資訊爬蟲")
    parser.add_argument(
        "--source",
        nargs="+",
        choices=list(ALL_SCRAPERS.keys()) + ["all"],
        default=["all"],
        help="要執行的來源,預設只跑真正的好康來源(不含一般市政新聞 news)",
    )
    parser.add_argument("--pages", type=int, default=3, help="每個來源要爬取的頁數")
    args = parser.parse_args()

    sources = list(SCRAPERS.keys()) if "all" in args.source else args.source
    run(sources, args.pages)
