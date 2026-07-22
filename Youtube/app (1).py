import streamlit as st

st.set_page_config(page_title="YouTube 댓글 분석기", page_icon="🎬", layout="wide")

st.title("🎬 YouTube 댓글 분석기")

api_key = st.secrets.get("YOUTUBE_API_KEY", "")

url = st.text_input("YouTube 영상 URL")

if st.button("분석 시작"):
    if not api_key:
        st.error("YOUTUBE_API_KEY가 secrets에 설정되어 있지 않습니다.")
    elif not url:
        st.warning("영상 URL을 입력하세요.")
    else:
        st.info("이 파일은 프로젝트의 시작 템플릿입니다. 이후 youtube_api.py, analyzer.py, visualization.py 등을 연결하여 완성합니다.")
        st.write("입력 URL:", url)
