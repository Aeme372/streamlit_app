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

from googleapiclient.discovery import build


def get_youtube(api_key: str):
    return build("youtube", "v3", developerKey=api_key)


def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


def get_video_info(youtube, video_id: str):
    resp = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()
    if not resp.get("items"):
        return None
    item = resp["items"][0]
    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "statistics": item["statistics"],
    }


def get_comments(youtube, video_id: str, max_results: int = 100):
    comments = []
    token = None
    while len(comments) < max_results:
        res = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            pageToken=token,
            textFormat="plainText",
        ).execute()

        for item in res["items"]:
            s = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": s["authorDisplayName"],
                "text": s["textDisplay"],
                "likes": s["likeCount"],
                "published": s["publishedAt"],
            })

        token = res.get("nextPageToken")
        if not token:
            break
    return comments

from collections import Counter
import re
from kiwipiepy import Kiwi

kiwi = Kiwi()

STOPWORDS = {
    "이","그","저","것","수","등","더","좀","및","에서","으로","를","을","은","는","이","가"
}

POSITIVE = {"좋다","최고","추천","감사","행복","재밌다","멋지다","훌륭"}
NEGATIVE = {"싫다","별로","최악","실망","화난","짜증","나쁘다"}

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def extract_keywords(comments, top_n=30):
    words=[]
    for c in comments:
        text = clean_text(c)
        for t in kiwi.tokenize(text):
            if t.tag.startswith("N") and len(t.form)>1 and t.form not in STOPWORDS:
                words.append(t.form)
    return Counter(words).most_common(top_n)

def sentiment(comment):
    score=0
    for token in kiwi.tokenize(clean_text(comment)):
        if token.form in POSITIVE:
            score += 1
        elif token.form in NEGATIVE:
            score -= 1
    if score>0:
        return "긍정"
    if score<0:
        return "부정"
    return "중립"

def analyze_comments(comments):
    sentiments=[sentiment(c) for c in comments]
    lengths=[len(c) for c in comments]
    return {
        "sentiments": Counter(sentiments),
        "lengths": lengths,
        "keywords": extract_keywords(comments)
    }
import plotly.express as px
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def sentiment_pie(counter):
    fig=px.pie(names=list(counter.keys()), values=list(counter.values()), title="감성 분석")
    st.plotly_chart(fig, use_container_width=True)

def keyword_bar(keywords):
    if not keywords: return
    words=[k for k,v in keywords]
    counts=[v for k,v in keywords]
    fig=px.bar(x=words,y=counts,title="TOP 키워드")
    st.plotly_chart(fig,use_container_width=True)

def comment_length_hist(lengths):
    fig=px.histogram(x=lengths, nbins=20, title="댓글 길이")
    st.plotly_chart(fig,use_container_width=True)

def draw_wordcloud(text,font_path="fonts/NanumGothic.ttf"):
    wc=WordCloud(font_path=font_path,width=1000,height=600,background_color="white").generate(text)
    fig,ax=plt.subplots(figsize=(10,6))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)
"""
wordcloud_util.py
"""

from collections import Counter
from kiwipiepy import Kiwi
from wordcloud import WordCloud

kiwi=Kiwi()

STOPWORDS={"이","그","저","수","등","및","에서","으로","하다","있다"}

def tokenize(text:str):
    words=[]
    for t in kiwi.tokenize(text):
        if t.tag.startswith("N") and len(t.form)>1 and t.form not in STOPWORDS:
            words.append(t.form)
    return words

def frequencies(comments):
    all_words=[]
    for c in comments:
        all_words.extend(tokenize(c))
    return Counter(all_words)

def make_wordcloud(comments,font_path="fonts/NanumGothic.ttf",
                   width=1200,height=700):
    freq=frequencies(comments)
    wc=WordCloud(
        font_path=font_path,
        width=width,
        height=height,
        background_color="white"
    ).generate_from_frequencies(freq)
    return wc
