import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="주차장 정보 시스템",
    layout="wide"
)

st.title("🚗 주차장 정보 검색 시스템")

st.write("CSV 파일(cp949)을 업로드하세요.")

uploaded_file = st.file_uploader(
    "주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    # CP949 인코딩
    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success("데이터 업로드 완료!")

    st.subheader("원본 데이터")

    st.dataframe(df)

    ####################################
    # 필요한 컬럼 확인
    ####################################

    required = [
        "주차장명",
        "자치구",
        "위도",
        "경도",
        "요금(시간당)",
        "주차장종류",
        "무료여부"
    ]

    for col in required:
        if col not in df.columns:
            st.error(f"{col} 컬럼이 없습니다.")
            st.stop()

    ####################################
    # 사이드바
    ####################################

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구",
        ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장종류"].dropna().unique().tolist())
    )

    fee_type = st.sidebar.selectbox(
        "무료/유료",
        ["전체", "무료", "유료"]
    )

    hours = st.sidebar.slider(
        "예상 주차 시간(시간)",
        1,
        24,
        2
    )

    ####################################
    # 필터링
    ####################################

    filtered = df.copy()

    if gu != "전체":
        filtered = filtered[filtered["자치구"] == gu]

    if parking_type != "전체":
        filtered = filtered[
            filtered["주차장종류"] == parking_type
        ]

    if fee_type != "전체":
        filtered = filtered[
            filtered["무료여부"] == fee_type
        ]

    ####################################
    # 예상요금 계산
    ####################################

    filtered["예상주차요금"] = filtered.apply(
        lambda x: 0
        if x["무료여부"] == "무료"
        else x["요금(시간당)"] * hours,
        axis=1
    )

    ####################################
    # 가장 저렴한 곳
    ####################################

    cheapest = filtered.sort_values(
        "예상주차요금"
    ).head(1)

    st.subheader("💰 가장 저렴한 주차장")

    if len(cheapest) > 0:

        c = cheapest.iloc[0]

        st.success(
            f"""
            주차장 : {c['주차장명']}

            자치구 : {c['자치구']}

            예상요금 : {c['예상주차요금']:,}원
            """
        )

    ####################################
    # 결과 테이블
    ####################################

    st.subheader("검색 결과")

    st.dataframe(
        filtered[
            [
                "주차장명",
                "자치구",
                "주차장종류",
                "무료여부",
                "요금(시간당)",
                "예상주차요금"
            ]
        ],
        use_container_width=True
    )

    ####################################
    # 지도
    ####################################

    st.subheader("📍 주차장 위치")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position='[경도, 위도]',
        get_radius=80,
        get_fill_color='[255,0,0,160]',
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=filtered["위도"].mean(),
        longitude=filtered["경도"].mean(),
        zoom=11
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "text":
            """
주차장 : {주차장명}

자치구 : {자치구}

요금 : {요금(시간당)}원
            """
        }
    )

    st.pydeck_chart(deck)

else:

    st.info("CSV 파일을 업로드해주세요.")
