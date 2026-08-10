"""臺中市政府經濟發展局 - 獎勵及補助專區

這是實際的政策好康(補助金、獎勵金、津貼等),不是一般新聞稿。
來源: https://www.economic.taichung.gov.tw/41064/Lpsimplelist
"""
from scrapers.gov_list_base import TaichungGovListScraper


class GovSubsidyScraper(TaichungGovListScraper):
    source = "econ_subsidy"
    category = "政策補助"
    list_url = "https://www.economic.taichung.gov.tw/41064/Lpsimplelist"
