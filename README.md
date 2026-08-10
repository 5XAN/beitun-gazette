# 台中北屯好康資料爬蟲

整合台中市**北屯區**的政策補助、店家優惠與社群好康情報。目前的 scope 是北屯,但
架構上很容易換成其他行政區(見下方各來源的「如何換行政區」說明)。

有兩種用法:
1. **本機互動查詢**:`main.py` 爬進 SQLite,`app.py` 開 Streamlit 儀表板瀏覽/搜尋(見下方)。
2. **公開網站(北屯好康郵報)**:`scripts/build_site.py` 現爬現生成一頁式靜態網站,由
   `.github/workflows/weekly.yml` 每週一早上 8 點(台灣時間)自動重新執行並部署到
   GitHub Pages,不需要手動操作。

## 資料來源

`--source all`(預設)只會執行下面前 5 個「真好康」來源。`news` 是一般市政
新聞大雜燴,故意排除在 `all` 之外,需要 `--source news` 才會執行。

不含 PTT:原本有 `ptt` 來源(PTT TaichungBun 看板),已依需求移除。

| 來源代碼 | 說明 | 範圍 | 狀態 |
|---|---|---|---|
| `beitun_office` | 臺中市北屯區公所公告(敬老禮金、津貼、住宅補助等),已用關鍵字篩選並排除農業部轉知雜訊 | 北屯限定 | 穩定 |
| `tcpass` | 台中通 APP 店家優惠,已用 `permanentDistrict=114` 篩選為北屯特約店家 | 北屯限定 | 穩定 |
| `subsidy` | 臺中市政府經濟發展局 - 獎勵及補助專區(全市性補助,北屯居民同樣適用) | 全市 | 穩定 |
| `dcard` | Dcard 台中板,標題需同時符合好康關鍵字(免費/送/優惠等)與「北屯」 | 北屯限定 | 不穩定(見下方說明) |
| `opendata` | data.gov.tw 政府資料開放平臺(台中相關資料集) | 全市 | 需自行申請 API Key |
| `news` | 臺中市政府全球資訊網 - 熱門公告/市政新聞 | 全市 | 穩定,但**不是好康**,只是一般新聞,預設不執行 |

**如何換成其他行政區**:
- `tcpass_coupon.py` 的 `DISTRICT_BEITUN = "114"`,改成 `TcpassCouponScraper(district="其他代碼")`(代碼對照見檔案內註解或 `tcpass.html` 表單)
- `beitun_office.py` 的 `list_url` 換成該行政區公所的公告頁網址(各區公所大多是同一套 CMS,可直接沿用 `gov_list_base.py`)
- `config.py` 的 `DISTRICT_KEYWORDS` 改成該行政區名稱

> 早期版本踩過兩次同樣的坑:先是市府「熱門公告」是一般新聞大雜燴,後來換成
> 北屯區公所公告又混進大量農業部轉知農民的補助公文。兩次都是用「先看實際
> 抓到的內容,再補關鍵字篩選/排除清單」的方式修正,而不是假設來源內容天生
> 就是「好康」。

## 安裝

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## 執行爬蟲

```bash
# 爬全部「好康」來源(beitun_office/tcpass/subsidy/opendata/dcard),每個來源抓 3 頁
.venv\Scripts\python main.py --pages 3

# 只爬指定來源
.venv\Scripts\python main.py --source beitun_office tcpass --pages 5

# 想順便看一般市政新聞(非好康),要另外指名
.venv\Scripts\python main.py --source news --pages 3
```

資料會存到 `data/taichung_deals.db`(SQLite),重複執行不會產生重複資料(以 來源+網址 去重)。

## 開啟儀表板

```bash
.venv\Scripts\streamlit run app.py
```

瀏覽器開啟 http://localhost:8501,可依來源/分類/關鍵字篩選。

## 開放資料來源設定(選用)

`opendata` 來源呼叫 data.gov.tw 官方 API,需要免費 API Key:

1. 至 https://data.gov.tw 註冊會員
2. 於會員中心申請 API Key
3. 設定環境變數後再執行爬蟲:
   ```bash
   set DATA_GOV_TW_API_KEY=你的key
   .venv\Scripts\python main.py --source opendata
   ```

官方回應的 JSON 欄位名稱文件揭露有限,`scrapers/opendata_datagovtw.py` 的
`_parse_dataset()` 採容錯寫法;若解析結果不理想,建議先印出一筆原始 JSON
確認欄位後調整。

## Dcard 來源的已知限制

Dcard 有 Cloudflare 機器人防護,單純用 `requests` 呼叫其 API 經常會被判定為
機器人而回傳 403。目前 `dcard_taichung.py` 會嘗試呼叫,失敗時只記錄警告、
回傳空清單,不會讓整個排程中斷。若需要穩定取得 Dcard 資料,建議之後改用
Playwright 之類的瀏覽器自動化方案。

## 公開網站(GitHub Pages)

`scripts/build_site.py` 直接重用 `scrapers/` 裡的 `beitun_office`、`tcpass`、`subsidy`
三個模組(最穩定、真正是「好康」的來源),現爬現生成一頁式靜態網站到 `public/index.html`,
不依賴本機 SQLite。

```bash
.venv\Scripts\python scripts\build_site.py
```

`.github/workflows/weekly.yml` 會在每週一 00:00 UTC(台灣時間早上 8 點)自動跑這支腳本,
並用 `actions/deploy-pages` 部署到 GitHub Pages,也可以到 repo 的 Actions 頁籤手動觸發
(workflow_dispatch)。網址是 `https://<github帳號>.github.io/<repo名稱>/`。

## 本機排程建議(Streamlit 儀表板用)

若只是想在本機定期更新 SQLite 資料庫給 Streamlit 儀表板用,可用 Windows 工作排程器:

```bash
.venv\Scripts\python main.py --pages 3
```

## 爬蟲禮儀

- `scrapers/base.py` 內建每次請求間隔(預設 1 秒)與重試機制,避免對目標網站造成負擔。
- 請勿把爬取頻率調得太高,尤其是 PTT/Dcard 這類非官方資料來源的個人網站。
- 若之後要公開發布資料或做商業用途,建議先確認各來源的使用條款
  (市府公告、開放資料屬公開資訊;PTT/Dcard 內容版權仍屬原作者)。

## 專案結構

```
config.py                       # 共用設定(逾時、間隔、DB 路徑、關鍵字)
models.py                       # Item 資料結構
database.py                     # SQLite 初始化與 upsert
main.py                         # CLI 進入點,執行指定爬蟲並寫入資料庫
app.py                          # Streamlit 儀表板
scrapers/
    base.py                     # 共用 session(重試、逾時、SSL 相容性處理)
    gov_list_base.py            # 台中市政府體系網站共用的公告列表樣板(含關鍵字篩選/排除)
    beitun_office.py            # 北屯區公所公告(真好康,北屯限定)
    gov_subsidy.py              # 經濟發展局補助專區(真好康,全市)
    gov_announcements.py        # 市府公告/市政新聞(非好康,預設不執行)
    tcpass_coupon.py            # 台中通店家優惠(可設定 district,預設北屯)
    opendata_datagovtw.py       # data.gov.tw 開放資料
    dcard_taichung.py           # Dcard 台中板(關鍵字+行政區雙重篩選)
```
