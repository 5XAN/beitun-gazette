import os

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
    "TaichungGoodDealsBot/1.0"
)

REQUEST_TIMEOUT = 20
REQUEST_DELAY_SECONDS = 1.0  # 每次請求間隔,避免對目標網站造成負擔

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "taichung_deals.db")

DATA_GOV_TW_API_KEY = os.environ.get("DATA_GOV_TW_API_KEY", "")

# 用來從社群/論壇雜訊中篩選出「好康」相關內容的關鍵字
DEAL_KEYWORDS = ["優惠", "折扣", "好康", "補助", "免費", "送", "抽獎", "限時", "特價", "折價"]

# 用來將社群/論壇內容限縮到北屯地區的關鍵字(PTT/Dcard 貼文常見「[贈送] 北屯/xxx」格式)
DISTRICT_KEYWORDS = ["北屯"]

# 政府公告用詞和社群不同(較正式),用來從區公所公告大雜燴中篩出真正的補助/津貼/好康
POLICY_BENEFIT_KEYWORDS = [
    "補助", "津貼", "禮金", "獎學金", "獎助", "好康", "優惠",
    "免費", "減免", "補貼", "核發", "發放",
]

# 區公所公告板常轉知中央部會給農民/業者的公文,標題也會有「補助」但和一般
# 居民無關,用來排除這類雜訊(即使命中 POLICY_BENEFIT_KEYWORDS 也要濾掉)
IRRELEVANT_BENEFIT_KEYWORDS = [
    "農業部", "農糧署", "保險費", "肥料", "農機", "水稻", "香蕉",
    "畜牧", "農田", "農產", "農會", "農民", "農場", "種牛", "生態保育",
]
