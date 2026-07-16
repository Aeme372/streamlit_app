import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(
    page_title="서울시 공영주차장 안내",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 서울시 공영주차장 안내 시스템")

uploaded = st.file_uploader("CSV 업로드", type="csv")

if uploaded is None:
    st.info("공영주차장 CSV를 업로드하세요.")
    st.stop()


@st.cache_data
def load_data(file):

    for enc in ["cp949", "utf-8", "euc-kr"]:
        try:
            file.seek(0)
            return pd.read_csv(file, encoding=enc)
        except:
            pass

    raise Exception("CSV를 읽을 수 없습니다.")


df = load_data(uploaded)

# 자치구 추출
df["자치구"] = df["주소"].astype(str).str.extract(r"([가-힣]+구)")

# 위경도 숫자 변환
df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

# ---------- 사이드바 ----------
st.sidebar.title("검색 조건")

keyword = st.sidebar.text_input("🔍 주차장명")

gus = ["전체"] + sorted(df["자치구"].dropna().unique())

selected_gu = st.sidebar.selectbox(
    "🏙 자치구",
    gus
)

types = ["전체"] + sorted(df["주차장 종류명"].dropna().unique())

selected_type = st.sidebar.selectbox(
    "🅿 주차장 종류",
    types
)

# ---------- 필터 ----------

filtered = df.copy()

if keyword:
    filtered = filtered[
        filtered["주차장명"].str.contains(keyword, na=False)
    ]

if selected_gu != "전체":
    filtered = filtered[
        filtered["자치구"] == selected_gu
    ]

if selected_type != "전체":
    filtered = filtered[
        filtered["주차장 종류명"] == selected_type
    ]

# ---------- 통계 ----------

c1, c2, c3 = st.columns(3)

c1.metric("주차장 수", len(filtered))

c2.metric(
    "총 주차면",
    int(filtered["총 주차면"].fillna(0).sum())
)

c3.metric(
    "자치구 수",
    filtered["자치구"].nunique()
)

st.divider()

# ---------- 지도 ----------

st.subheader("🗺 지도")

map_df = filtered.dropna(subset=["위도", "경도"])

if len(map_df):

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[경도, 위도]",
        get_fill_color=[0,120,255,180],
        get_radius=40,
        pickable=True
    )

    view = pdk.ViewState(
        latitude=map_df["위도"].mean(),
        longitude=map_df["경도"].mean(),
        zoom=11
    )

    tooltip={
        "html":"""
        <b>{주차장명}</b><br/>
        주소 : {주소}<br/>
        종류 : {주차장 종류명}<br/>
        전화 : {전화번호}<br/>
        주차면 : {총 주차면}
        """
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip=tooltip
        )
    )

else:
    st.warning("위도·경도 정보가 없습니다.")

# ---------- 차트 ----------

left,right = st.columns(2)

with left:

    st.subheader("자치구별 주차장 수")

    chart = (
        filtered["자치구"]
        .value_counts()
        .reset_index()
    )

    chart.columns=["자치구","개수"]

    fig=px.bar(
        chart,
        x="자치구",
        y="개수"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with right:

    st.subheader("주차장 종류")

    chart2=(
        filtered["주차장 종류명"]
        .value_counts()
        .reset_index()
    )

    chart2.columns=["종류","개수"]

    fig2=px.pie(
        chart2,
        names="종류",
        values="개수"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# ---------- 테이블 ----------

st.subheader("📋 주차장 목록")

cols=[]

for c in [
    "주차장명",
    "자치구",
    "주소",
    "주차장 종류명",
    "총 주차면",
    "전화번호",
    "기본 주차 요금",
    "기본 주차 시간"
]:
    if c in filtered.columns:
        cols.append(c)

st.dataframe(
    filtered[cols],
    use_container_width=True
)

# ---------- 다운로드 ----------

csv = filtered.to_csv(index=False).encode("cp949")

st.download_button(
    "📥 필터 결과 다운로드",
    csv,
    "parking.csv",
    "text/csv"
)
