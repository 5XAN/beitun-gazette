"""臺中市北屯區公所 - 公告訊息/最新消息

北屯在地的政策好康(敬老禮金、托育補助、急難救助等)大多從這裡公告,
比市府本部或經濟發展局的公告更貼近北屯居民。

來源: https://www.beitun.taichung.gov.tw/832030/Lpsimplelist
"""
from config import IRRELEVANT_BENEFIT_KEYWORDS, POLICY_BENEFIT_KEYWORDS
from scrapers.gov_list_base import TaichungGovListScraper


class BeitunOfficeScraper(TaichungGovListScraper):
    source = "beitun_office"
    category = "北屯區公所公告"
    list_url = "https://www.beitun.taichung.gov.tw/832030/Lpsimplelist"
    keywords = POLICY_BENEFIT_KEYWORDS
    exclude_keywords = IRRELEVANT_BENEFIT_KEYWORDS
