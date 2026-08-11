"""產生北屯好康郵報的靜態網站(public/index.html),供 GitHub Pages 部署用。

直接重用 scrapers/ 底下已經驗證過的爬蟲模組,現爬現生成,不依賴本機 SQLite,
每次執行都是完整的最新快照。由 .github/workflows/weekly.yml 每週排程執行。
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scrapers.beitun_office import BeitunOfficeScraper
from scrapers.gov_subsidy import GovSubsidyScraper
from scrapers.tcpass_coupon import TcpassCouponScraper

PAGES = 5
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public")


def item_to_dict(item):
    return {
        "source": item.source,
        "category": item.category,
        "title": item.title,
        "description": item.description,
        "store_name": item.store_name,
        "url": item.url,
        "date_start": item.date_start,
        "date_end": item.date_end,
        "published_at": item.published_at,
    }


def safe_fetch(name, scraper):
    """單一來源失敗(例如 tcpass 對雲端主機 IP 回傳 403)不該讓整個網站建置失敗,
    失敗就記錄警告、回傳空清單,讓其他來源照常產出。"""
    try:
        return [item_to_dict(i) for i in scraper.fetch(pages=PAGES)]
    except Exception as exc:
        print(f"WARNING: {name} 爬取失敗,本次快照將略過此來源: {exc}", file=sys.stderr)
        return []


def main():
    beitun = safe_fetch("beitun_office", BeitunOfficeScraper())
    econ = safe_fetch("econ_subsidy", GovSubsidyScraper())
    stores = safe_fetch("tcpass", TcpassCouponScraper())
    items = beitun + econ + stores

    tz = timezone(timedelta(hours=8))
    snapshot = datetime.now(tz).strftime("%Y/%m/%d")

    os.makedirs(OUT_DIR, exist_ok=True)
    html = TEMPLATE.replace("__DATA_JSON__", json.dumps(items, ensure_ascii=False)).replace(
        "__SNAPSHOT__", snapshot
    )
    out_path = os.path.join(OUT_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"beitun_office={len(beitun)} econ_subsidy={len(econ)} tcpass={len(stores)}")
    print(f"wrote {out_path} ({len(html)} bytes)")


TEMPLATE = r"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>北屯好康郵報</title>
<style>
:root{
  --paper:#F6ECE0;
  --paper-alt:#EFE0CC;
  --paper-card:#FBF5EA;
  --ink:#2B1B14;
  --ink-soft:#6B5744;
  --red:#B62A1E;
  --red-bright:#D63A26;
  --gold:#A97C24;
  --teal:#1D6E5D;
  --line: rgba(43,27,20,0.16);
  --shadow: 0 1px 0 rgba(43,27,20,0.06);
}
@media (prefers-color-scheme: dark){
  :root{
    --paper:#1C130E;
    --paper-alt:#241A13;
    --paper-card:#221812;
    --ink:#F1E4D2;
    --ink-soft:#C9B49B;
    --red:#E2543C;
    --red-bright:#F16A4E;
    --gold:#D9A947;
    --teal:#4FB39C;
    --line: rgba(241,228,210,0.16);
    --shadow: 0 1px 0 rgba(0,0,0,0.3);
  }
}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;}
.gazette{
  background:var(--paper);
  color:var(--ink);
  font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei","Heiti TC",sans-serif;
  line-height:1.75;
  min-height:100vh;
}
.wrap{max-width:920px;margin:0 auto;padding:0 20px 64px;}

.masthead{
  background:var(--red);
  color:#FBF0E4;
  padding:28px 20px 22px;
  border-bottom:6px solid var(--gold);
}
.masthead-inner{max-width:920px;margin:0 auto;text-align:center;}
.eyebrow{font-size:12.5px;letter-spacing:.14em;opacity:.88;margin:0 0 6px;}
.masthead h1{
  font-family:"Noto Serif TC","Songti TC","PMingLiU",serif;
  font-weight:900;
  font-size:clamp(34px,7vw,52px);
  margin:0;
  text-wrap:balance;
  letter-spacing:.02em;
}
.masthead .sub{
  font-size:11.5px;
  letter-spacing:.24em;
  text-transform:uppercase;
  opacity:.78;
  margin:8px 0 0;
  font-family:Georgia,"Times New Roman",serif;
}
.masthead .meta{
  margin:16px auto 0;
  font-size:13px;
  opacity:.92;
  display:flex;
  flex-wrap:wrap;
  gap:6px 18px;
  justify-content:center;
  font-variant-numeric:tabular-nums;
  border-top:1px solid rgba(251,240,228,0.35);
  padding-top:12px;
  max-width:640px;
}

.lede{padding:30px 0 6px;}
.section-label{
  font-family:"Noto Serif TC","Songti TC",serif;
  font-weight:700;
  font-size:13px;
  letter-spacing:.18em;
  color:var(--red);
  margin:0 0 14px;
  display:flex;
  align-items:center;
  gap:10px;
}
.section-label::after{content:"";flex:1;height:1px;background:var(--line);}
.lede-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
@media (max-width:720px){ .lede-grid{grid-template-columns:1fr;} }
.lede-card{
  background:var(--paper-card);
  border:1px solid var(--line);
  padding:18px 16px 16px;
  position:relative;
  box-shadow:var(--shadow);
}
.lede-card .stamp{position:absolute; top:-10px; right:14px;}
.lede-card h3{
  font-family:"Noto Serif TC","Songti TC",serif;
  font-size:16.5px;
  line-height:1.5;
  margin:6px 0 0;
  text-wrap:balance;
}
.lede-card a{color:inherit;text-decoration:none;}
.lede-card a:hover h3{color:var(--red);}
.lede-card a:focus-visible{outline:2px solid var(--red); outline-offset:3px;}

.stamp{display:inline-flex;padding:3px;transform:rotate(-3deg);filter:drop-shadow(0 1px 1px rgba(0,0,0,.15));}
.stamp-inner{
  border:1.5px dashed rgba(255,255,255,.85);
  padding:2px 9px;
  font-size:10.5px;
  font-weight:700;
  letter-spacing:.06em;
  color:#fff;
  white-space:nowrap;
}
.stamp.red .stamp-inner{background:var(--red);}
.stamp.gold .stamp-inner{background:var(--gold);}
.stamp.teal .stamp-inner{background:var(--teal);}

.intro{font-size:14.5px;color:var(--ink-soft);max-width:62ch;margin:22px 0 0;}

.toolbar{display:flex;gap:10px;align-items:center;margin:18px 0 22px;flex-wrap:wrap;}
.toolbar input[type="search"]{
  flex:1;
  min-width:220px;
  font:inherit;
  font-size:14px;
  padding:10px 14px;
  border:1px solid var(--line);
  background:var(--paper-card);
  color:var(--ink);
  border-radius:2px;
}
.toolbar input[type="search"]:focus-visible{outline:2px solid var(--red); outline-offset:1px;}
.toolbar .count{font-size:12.5px;color:var(--ink-soft);font-variant-numeric:tabular-nums;white-space:nowrap;}

.ticket-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;}
.ticket{background:var(--paper-card);border:1px solid var(--line);box-shadow:var(--shadow);display:flex;flex-direction:column;}
.ticket a{color:inherit;text-decoration:none;display:flex;flex-direction:column;height:100%;padding:14px 15px 12px;}
.ticket a:focus-visible{outline:2px solid var(--red); outline-offset:-2px;}
.ticket .store{font-weight:700;font-size:14.5px;line-height:1.4;text-wrap:balance;}
.ticket .tear{border-top:1.5px dashed var(--line);margin:10px 0;}
.ticket .discount{font-size:13px;color:var(--ink-soft);flex:1;line-height:1.6;}
.ticket .valid{font-size:11px;color:var(--ink-soft);margin-top:10px;font-variant-numeric:tabular-nums;opacity:.85;}
.ticket:hover{border-color:var(--red);}
.ticket:hover .store{color:var(--red);}

.empty-note{font-size:13.5px;color:var(--ink-soft);padding:20px 0;}

.policy-group{margin-bottom:26px;}
.policy-group h4{font-size:13px;font-weight:700;color:var(--ink-soft);letter-spacing:.06em;margin:0 0 4px;}
.policy-list{list-style:none;margin:0;padding:0;}
.policy-list li{border-top:1px solid var(--line);padding:12px 0;display:flex;gap:14px;align-items:baseline;}
.policy-list li:last-child{border-bottom:1px solid var(--line);}
.policy-list .p-date{flex:0 0 auto;font-size:12px;color:var(--ink-soft);font-variant-numeric:tabular-nums;width:78px;}
.policy-list a{color:var(--ink);text-decoration:none;font-size:14px;line-height:1.6;}
.policy-list a:hover{color:var(--red);}
.policy-list a:focus-visible{outline:2px solid var(--red); outline-offset:2px;}

.colophon{
  margin-top:44px;
  padding-top:18px;
  border-top:2px solid var(--ink);
  font-size:12px;
  color:var(--ink-soft);
  display:flex;
  flex-wrap:wrap;
  gap:6px 20px;
  justify-content:space-between;
}
.colophon a{color:var(--ink-soft);}
.colophon .cols{display:flex; flex-direction:column; gap:4px;}

@media (prefers-reduced-motion:no-preference){
  .ticket, .lede-card, a{transition:color .15s ease, border-color .15s ease;}
}
</style>
</head>
<body>
<div class="gazette">
  <header class="masthead">
    <div class="masthead-inner">
      <p class="eyebrow">北屯限定 · 街坊好康快報</p>
      <h1>北屯好康郵報</h1>
      <p class="sub">Beitun Good-Deals Gazette</p>
      <div class="meta">
        <span id="metaSnapshot"></span>
        <span id="metaStore"></span>
        <span id="metaPolicy"></span>
      </div>
    </div>
  </header>

  <div class="wrap">
    <section class="lede">
      <p class="section-label">本期焦點</p>
      <div class="lede-grid" id="ledeGrid"></div>
      <p class="intro">整理自北屯區公所公告、台中通北屯特約店家與市府補助專區,只留下真的跟街坊生活有關的項目 —— 不是一般市政新聞轉貼。分成「居民福利」跟「商家企業補助」兩大類,分類是依標題關鍵字自動判斷,少數項目可能不夠精確。</p>
    </section>

    <section id="residentSection">
      <p class="section-label">居民福利版</p>

      <div class="policy-group">
        <h4>消費優惠 · 店家折扣</h4>
        <div class="toolbar">
          <input type="search" id="storeSearch" placeholder="搜尋店名或優惠內容,例如：咖啡、9折、東山" aria-label="搜尋店家優惠">
          <span class="count" id="storeCount"></span>
        </div>
        <div class="ticket-grid" id="ticketGrid"></div>
        <p class="empty-note" id="ticketEmpty" hidden>沒有符合的店家,換個關鍵字試試。</p>
      </div>

      <div class="policy-group" style="margin-top:32px;">
        <h4>生活補助 · 津貼與福利</h4>
        <ul class="policy-list" id="residentPolicyList"></ul>
      </div>
    </section>

    <section id="businessSection" style="margin-top:40px;">
      <p class="section-label">商家企業補助版</p>
      <div class="policy-group">
        <h4>給店家、公司與團體的獎勵/補助</h4>
        <ul class="policy-list" id="businessPolicyList"></ul>
      </div>
    </section>

    <footer class="colophon">
      <div class="cols">
        <span>資料來源：臺中市北屯區公所公告、台中通店家優惠(北屯)、臺中市政府經濟發展局補助專區</span>
        <span>每週一早上自動重新爬取更新,由 GitHub Actions 排程執行。「居民福利/商家企業補助」為關鍵字自動分類,僅供參考。</span>
      </div>
      <div class="cols">
        <span>由好康資料爬蟲整理製作</span>
      </div>
    </footer>
  </div>
</div>

<script id="deals-data" type="application/json">__DATA_JSON__</script>
<script>
(function(){
  var raw = document.getElementById('deals-data').textContent;
  var items = JSON.parse(raw);
  var SNAPSHOT = "__SNAPSHOT__";

  var stores = items.filter(function(i){ return i.source === 'tcpass'; });
  var beitun = items.filter(function(i){ return i.source === 'beitun_office'; });
  var econ = items.filter(function(i){ return i.source === 'econ_subsidy'; });
  var policyItems = beitun.concat(econ);

  // ---- 居民福利 / 商家企業補助 自動分類 ----
  // 依標題關鍵字判斷,店家優惠(消費者可直接使用)一律算居民福利;
  // 政策類項目先比對關鍵字,比對不到才依來源預設(區公所→居民、經發局→商家)。
  var RESIDENT_KEYWORDS = ['家用','弱勢家庭','家庭','禮金','津貼','獎學金','學生','子女','托育',
    '照顧','無障礙','用戶','市民','居民','敬老','身心障礙','低收入戶','中低收入','住宅','好康'];
  var BUSINESS_KEYWORDS = ['商圈','商店街','商場','產業發展','會展','地方產業','創新研發','SBIR',
    '協會','基金會','合作社','法人','廠商','事業','企業','審查申請流程','契約範本','低碳認證','產銷履歷','公司'];

  function classify(item){
    if (item.source === 'tcpass') return 'resident';
    var t = item.title;
    if (RESIDENT_KEYWORDS.some(function(k){ return t.indexOf(k) !== -1; })) return 'resident';
    if (BUSINESS_KEYWORDS.some(function(k){ return t.indexOf(k) !== -1; })) return 'business';
    return item.source === 'econ_subsidy' ? 'business' : 'resident';
  }

  var residentPolicy = policyItems.filter(function(i){ return classify(i) === 'resident'; });
  var businessPolicy = policyItems.filter(function(i){ return classify(i) === 'business'; });

  document.getElementById('metaSnapshot').textContent = '資料擷取於 ' + SNAPSHOT;
  document.getElementById('metaStore').textContent = stores.length + ' 家北屯特約店家';
  document.getElementById('metaPolicy').textContent =
    residentPolicy.length + ' 則居民福利 · ' + businessPolicy.length + ' 則商家企業補助';

  function fmtDate(s){ return s ? s.replace(/-/g,'/') : ''; }

  function findByTitleIncludes(list, needle){
    for (var i=0;i<list.length;i++){
      if (list[i].title.indexOf(needle) !== -1) return list[i];
    }
    return null;
  }

  var picks = [];
  var p1 = findByTitleIncludes(beitun, '重陽敬老禮金');
  var p2 = findByTitleIncludes(beitun, '住宅無障礙設施補助');
  var p3 = findByTitleIncludes(beitun, '減塑享好康');
  [p1, p2, p3].forEach(function(p){ if (p) picks.push(p); });
  if (picks.length < 3){
    beitun.forEach(function(b){ if (picks.indexOf(b) === -1 && picks.length < 3) picks.push(b); });
  }

  var ledeGrid = document.getElementById('ledeGrid');
  picks.forEach(function(p){
    var card = document.createElement('div');
    card.className = 'lede-card';
    card.innerHTML =
      '<span class="stamp gold"><span class="stamp-inner">北屯限定</span></span>' +
      '<a href="' + p.url + '" target="_blank" rel="noopener"><h3>' + p.title + '</h3></a>';
    ledeGrid.appendChild(card);
  });

  var ticketGrid = document.getElementById('ticketGrid');
  var storeCount = document.getElementById('storeCount');
  var ticketEmpty = document.getElementById('ticketEmpty');

  function renderStores(list){
    ticketGrid.innerHTML = '';
    list.forEach(function(s){
      var el = document.createElement('div');
      el.className = 'ticket';
      var valid = (s.date_start || s.date_end)
        ? '<div class="valid">效期 ' + fmtDate(s.date_start) + ' ~ ' + fmtDate(s.date_end) + '</div>'
        : '';
      el.innerHTML =
        '<a href="' + s.url + '" target="_blank" rel="noopener">' +
          '<div class="store">' + s.store_name + '</div>' +
          '<div class="tear"></div>' +
          '<div class="discount">' + s.description + '</div>' +
          valid +
        '</a>';
      ticketGrid.appendChild(el);
    });
    storeCount.textContent = list.length + ' / ' + stores.length + ' 家';
    ticketEmpty.hidden = list.length !== 0;
    ticketEmpty.textContent = stores.length === 0
      ? '店家優惠資料本週暫時無法取得,晚點再回來看看。'
      : '沒有符合的店家,換個關鍵字試試。';
  }
  renderStores(stores);

  document.getElementById('storeSearch').addEventListener('input', function(e){
    var q = e.target.value.trim().toLowerCase();
    if (!q){ renderStores(stores); return; }
    renderStores(stores.filter(function(s){
      return (s.store_name + s.description).toLowerCase().indexOf(q) !== -1;
    }));
  });

  function renderPolicy(list, elId){
    var ul = document.getElementById(elId);
    list.forEach(function(p){
      var li = document.createElement('li');
      var scopeLabel = p.source === 'beitun_office' ? '北屯限定' : '全市';
      var scopeClass = p.source === 'beitun_office' ? 'gold' : 'teal';
      li.innerHTML =
        '<span class="p-date">' + fmtDate(p.published_at) + '</span>' +
        '<a href="' + p.url + '" target="_blank" rel="noopener">' +
          '<span class="stamp ' + scopeClass + '" style="margin-right:8px;vertical-align:2px;">' +
            '<span class="stamp-inner">' + scopeLabel + '</span></span>' +
          p.title +
        '</a>';
      ul.appendChild(li);
    });
  }
  renderPolicy(residentPolicy, 'residentPolicyList');
  renderPolicy(businessPolicy, 'businessPolicyList');
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
