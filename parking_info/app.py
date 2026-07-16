import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="서울시 공영주차장 지도",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 서울시 공영주차장 지도")

uploaded_file = st.file_uploader(
    "공영주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    # 인코딩 자동 처리
    encodings = ["cp949", "utf-8", "euc-kr"]

    df = None

    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            break
        except:
            pass

    if df is None:
        st.error("CSV 파일을 읽을 수 없습니다.")
        st.stop()

    st.success(f"{len(df)}개의 데이터를 불러왔습니다.")

    st.write("### 컬럼")
    st.write(df.columns.tolist())

    # 필요한 컬럼 존재 여부 확인
    required = ["주차장명", "주소", "위도", "경도"]

    if not all(col in df.columns for col in required):
        st.error("CSV에 '주차장명', '주소', '위도', '경도' 컬럼이 있어야 합니다.")
        st.stop()

    # 숫자형 변환
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

    # 좌표 없는 행 제거
    df = df.dropna(subset=["위도", "경도"])

    if len(df) == 0:
        st.error("위도·경도 데이터가 없습니다.")
        st.stop()

    # 검색
    keyword = st.text_input("주차장 검색")

    if keyword:
        df = df[df["주차장명"].str.contains(keyword, na=False)]

    # 종류 필터
    if "주차장 종류명" in df.columns:

        kinds = ["전체"] + sorted(df["주차장 종류명"].dropna().unique())

        selected = st.selectbox(
            "주차장 종류",
            kinds
        )

        if selected != "전체":
            df = df[df["주차장 종류명"] == selected]

    st.subheader("주차장 목록")

    show_cols = [
        c for c in [
            "주차장명",
            "주소",
            "주차장 종류명",
            "총 주차면",
            "기본 주차 요금",
            "전화번호"
        ] if c in df.columns
    ]

    st.dataframe(
        df[show_cols],
        use_container_width=True
    )

    st.subheader("지도")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[경도, 위도]",
        get_radius=40,
        get_fill_color=[255, 0, 0, 180],
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df["위도"].mean(),
        longitude=df["경도"].mean(),
        zoom=11,
        pitch=0,
    )

    tooltip = {
        "html": """
        <b>{주차장명}</b><br/>
        주소 : {주소}<br/>
        종류 : {주차장 종류명}<br/>
        요금 : {기본 주차 요금}<br/>
        전화 : {전화번호}
        """
    }

    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=view_state,
            layers=[layer],
            tooltip=tooltip,
        )
    )
