import pandas as pd
import streamlit as st

from database import connect, init_db

st.set_page_config(page_title="台中好康資訊", page_icon="🎁", layout="wide")

init_db()


@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    with connect() as conn:
        return pd.read_sql_query(
            "SELECT source, category, title, description, store_name, url, "
            "date_start, date_end, published_at, scraped_at, first_seen_at "
            "FROM items ORDER BY first_seen_at DESC",
            conn,
        )


st.title("🎁 台中好康資訊")
st.caption("整合台中市政府公告、店家優惠、開放資料與社群情報")

df = load_data()

if df.empty:
    st.info("目前資料庫是空的,請先在終端機執行 `python main.py` 爬取資料。")
    st.stop()

source_labels = {
    "beitun_office": "北屯區公所公告",
    "tcpass": "店家優惠(台中通/北屯)",
    "econ_subsidy": "政策補助(經發局)",
    "opendata": "開放資料",
    "dcard": "Dcard 社群情報(北屯)",
    "taichung_gov_news": "市政新聞(非好康)",
}
df["來源"] = df["source"].map(source_labels).fillna(df["source"])

col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    sources = st.multiselect("來源", sorted(df["來源"].unique()), default=sorted(df["來源"].unique()))
with col2:
    categories = st.multiselect("分類", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
with col3:
    keyword = st.text_input("關鍵字搜尋(標題/描述)")

filtered = df[df["來源"].isin(sources) & df["category"].isin(categories)]
if keyword:
    mask = filtered["title"].str.contains(keyword, case=False, na=False) | filtered[
        "description"
    ].str.contains(keyword, case=False, na=False)
    filtered = filtered[mask]

st.write(f"共 {len(filtered)} 筆結果")

for _, row in filtered.iterrows():
    with st.container(border=True):
        st.markdown(f"**[{row['title']}]({row['url']})**  \n`{row['來源']}` · `{row['category']}`")
        if row["description"]:
            st.write(row["description"])
        meta = []
        if row["date_start"] or row["date_end"]:
            meta.append(f"活動期間: {row['date_start']} ~ {row['date_end']}")
        if row["published_at"]:
            meta.append(f"發布日期: {row['published_at']}")
        if meta:
            st.caption(" | ".join(meta))
