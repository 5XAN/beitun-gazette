"""臺中市政府全球資訊網 - 熱門公告/市政新聞

注意: 這是「一般市政新聞」的大雜燴(工程進度、活動報導、人事異動...等),
不是優惠或補助。內容量大但和「好康」關聯度低,所以預設不列入 main.py 的
`all` 批次,只有明確指定 `--source news` 才會執行。若要找真正的政策好康,
請用 gov_subsidy.py(經濟發展局補助專區)。

來源: https://www.taichung.gov.tw/8868/8872/9962
"""
from scrapers.gov_list_base import TaichungGovListScraper


class GovNewsScraper(TaichungGovListScraper):
    source = "taichung_gov_news"
    category = "市政新聞(非好康)"
    list_url = "https://www.taichung.gov.tw/8868/8872/9962"
