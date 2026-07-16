import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="공영주차장 안내", layout="wide")

st.title("🚗 서울시 공영주차장 안내")

uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success(f"{len(df)}개의 주차장 정보를 불러왔습니다.")

    keyword = st.text_input("주차장 검색")

    if keyword:
        df = df[df["주차장명"].str.contains(keyword, na=False)]

    if "주차장종류" in df.columns:
        kinds = ["전체"] + list(df["주차장종류"].dropna().unique())

        selected = st.selectbox("주차장 종류", kinds)

        if selected != "전체":
            df = df[df["주차장종류"] == selected]

    st.dataframe(df)

    center = [37.5665, 126.9780]

    if len(df) > 0:

        if "위도" in df.columns and "경도" in df.columns:

            center = [df.iloc[0]["위도"], df.iloc[0]["경도"]]

    m = folium.Map(location=center, zoom_start=11)

    for _, row in df.iterrows():

        if pd.isna(row["위도"]) or pd.isna(row["경도"]):
            continue

        popup = f"""
        <b>{row['주차장명']}</b><br>
        주소 : {row['주소']}<br>
        종류 : {row['주차장종류']}<br>
        요금 : {row['요금정보']}
        """

        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=popup,
            tooltip=row["주차장명"]
        ).add_to(m)

    st_folium(m, width=1200, height=700)
