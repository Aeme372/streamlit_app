import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장",
    layout="wide"
)

st.title("🚗 서울시 공영주차장 안내")

uploaded = st.file_uploader(
    "CSV 파일 업로드",
    type="csv"
)

if uploaded is not None:

    # 여러 인코딩 자동 시도
    try:
        df = pd.read_csv(uploaded, encoding="cp949")
    except:
        uploaded.seek(0)
        try:
            df = pd.read_csv(uploaded, encoding="utf-8")
        except:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, encoding="euc-kr")

    st.success(f"{len(df)}개의 데이터를 불러왔습니다.")

    st.write("### 컬럼 확인")
    st.write(df.columns.tolist())

    # 컬럼 선택
    lat_col = st.selectbox(
        "위도 컬럼",
        df.columns
    )

    lon_col = st.selectbox(
        "경도 컬럼",
        df.columns
    )

    name_col = st.selectbox(
        "주차장 이름 컬럼",
        df.columns
    )

    search = st.text_input("주차장 검색")

    if search:
        df = df[
            df[name_col]
            .astype(str)
            .str.contains(search, case=False, na=False)
        ]

    st.write("### 데이터")
    st.dataframe(df)

    # 지도 생성
    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11
    )

    for _, row in df.iterrows():

        try:
            lat = float(row[lat_col])
            lon = float(row[lon_col])
        except:
            continue

        folium.Marker(
            [lat, lon],
            popup=str(row[name_col]),
            tooltip=str(row[name_col])
        ).add_to(m)

    st.write("### 지도")

    st_folium(
        m,
        width=1200,
        height=700
    )
