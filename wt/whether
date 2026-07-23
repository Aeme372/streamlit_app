import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# =========================
# 기본 설정
# =========================

st.set_page_config(
    page_title="Weather Analyzer",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Analyzer")
st.write("CSV 날씨 데이터를 분석하는 웹 앱")


# =========================
# CSV 업로드
# =========================

uploaded_file = st.sidebar.file_uploader(
    "날씨 CSV 업로드",
    type=["csv"]
)


if uploaded_file is None:

    st.info("CSV 파일을 업로드해주세요.")

    example = pd.DataFrame(
        {
            "날짜": [
                "2026-07-01",
                "2026-07-02",
                "2026-07-03",
                "2026-07-04",
                "2026-07-05"
            ],
            "최고기온": [31, 33, 29, 35, 30],
            "최저기온": [22, 24, 21, 25, 20],
            "평균기온": [26, 28, 25, 30, 25],
            "강수량": [0, 12, 30, 0, 5],
            "습도": [60, 70, 90, 55, 65]
        }
    )

    st.subheader("예시 데이터")

    st.dataframe(example)

    st.stop()



# =========================
# 데이터 불러오기
# =========================

try:

    df = pd.read_csv(uploaded_file)

except:

    st.error("CSV 파일을 읽을 수 없습니다.")
    st.stop()



# =========================
# 컬럼 확인
# =========================

required_columns = [
    "날짜",
    "최고기온",
    "최저기온",
    "평균기온",
    "강수량",
    "습도"
]


missing = []

for col in required_columns:

    if col not in df.columns:
        missing.append(col)


if missing:

    st.error(
        f"필요한 컬럼이 없습니다: {missing}"
    )

    st.stop()



# =========================
# 데이터 처리
# =========================

df["날짜"] = pd.to_datetime(
    df["날짜"]
)


number_columns = [
    "최고기온",
    "최저기온",
    "평균기온",
    "강수량",
    "습도"
]


for col in number_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


df = df.dropna()


df["월"] = df["날짜"].dt.month



# =========================
# 사이드바 필터
# =========================

st.sidebar.header("필터")


start_date = st.sidebar.date_input(
    "시작 날짜",
    df["날짜"].min()
)


end_date = st.sidebar.date_input(
    "종료 날짜",
    df["날짜"].max()
)



filtered = df[
    (df["날짜"] >= pd.to_datetime(start_date))
    &
    (df["날짜"] <= pd.to_datetime(end_date))
]



rain_filter = st.sidebar.checkbox(
    "비 온 날만 보기"
)


if rain_filter:

    filtered = filtered[
        filtered["강수량"] > 0
    ]



# =========================
# 데이터 미리보기
# =========================

st.subheader("📄 데이터")


st.dataframe(
    filtered,
    use_container_width=True
)



# =========================
# 주요 통계
# =========================

st.subheader("📊 주요 분석")


col1,col2,col3,col4 = st.columns(4)


col1.metric(
    "평균 기온",
    f"{filtered['평균기온'].mean():.1f}℃"
)


col2.metric(
    "최고 기온",
    f"{filtered['최고기온'].max():.1f}℃"
)


col3.metric(
    "총 강수량",
    f"{filtered['강수량'].sum():.1f}mm"
)


col4.metric(
    "평균 습도",
    f"{filtered['습도'].mean():.1f}%"
)



# =========================
# 기온 그래프
# =========================

st.subheader("🌡️ 기온 변화")


fig_temp = px.line(
    filtered,
    x="날짜",
    y=[
        "최고기온",
        "최저기온",
        "평균기온"
    ],
    markers=True,
    title="날짜별 기온 변화"
)


st.plotly_chart(
    fig_temp,
    use_container_width=True
)



# =========================
# 강수량 그래프
# =========================

st.subheader("🌧️ 강수량")


fig_rain = px.bar(
    filtered,
    x="날짜",
    y="강수량",
    title="날짜별 강수량"
)


st.plotly_chart(
    fig_rain,
    use_container_width=True
)



# =========================
# 습도 그래프
# =========================

st.subheader("💧 습도")


fig_humidity = px.line(
    filtered,
    x="날짜",
    y="습도",
    markers=True
)


st.plotly_chart(
    fig_humidity,
    use_container_width=True
)



# =========================
# 월별 분석
# =========================

st.subheader("📅 월별 평균")


monthly = (
    filtered
    .groupby("월")
    [["평균기온","강수량","습도"]]
    .mean()
    .reset_index()
)


st.dataframe(monthly)



fig_month = px.bar(
    monthly,
    x="월",
    y="평균기온",
    title="월별 평균 기온"
)


st.plotly_chart(
    fig_month,
    use_container_width=True
)



# =========================
# 폭염 탐지
# =========================

st.subheader("🔥 이상 기후 탐지")


heat_days = filtered[
    filtered["최고기온"] >= 33
]


if len(heat_days):

    st.warning(
        f"폭염 가능 날짜 {len(heat_days)}일 발견"
    )

    st.dataframe(
        heat_days
    )

else:

    st.success(
        "폭염 기준 날짜가 없습니다."
    )



# =========================
# 이상치 탐지(IQR)
# =========================

q1 = filtered["평균기온"].quantile(0.25)

q3 = filtered["평균기온"].quantile(0.75)

iqr = q3-q1


lower = q1 - 1.5*iqr

upper = q3 + 1.5*iqr


outlier = filtered[
    (filtered["평균기온"] < lower)
    |
    (filtered["평균기온"] > upper)
]


st.write(
    "평균기온 이상치"
)


if len(outlier):

    st.dataframe(outlier)

else:

    st.write(
        "이상치 없음"
    )



# =========================
# 다운로드
# =========================

st.subheader("📥 결과 다운로드")


csv = filtered.to_csv(
    index=False,
    encoding="utf-8-sig"
)


st.download_button(
    "분석 결과 CSV 다운로드",
    csv,
    "weather_result.csv",
    "text/csv"
)



st.success(
    "분석 완료!"
)
