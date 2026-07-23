import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ==========================
# 설정
# ==========================

st.set_page_config(
    page_title="AI CSV Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI CSV 데이터 분석기")
st.write(
    "CSV 파일을 업로드하면 데이터를 자동으로 분석합니다."
)


# ==========================
# 파일 업로드
# ==========================

uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)


if uploaded_file is None:

    st.info(
        "CSV 파일을 업로드해주세요."
    )

    st.markdown(
        """
        지원 예시:

        - 날씨 데이터
        - 성적 데이터
        - 매출 데이터
        - 운동 기록
        - 실험 데이터

        컬럼명이 정해져 있지 않아도 됩니다.
        """
    )

    st.stop()



# ==========================
# CSV 읽기
# ==========================

try:

    uploaded_file.seek(0)

    try:
        df = pd.read_csv(
            uploaded_file,
            encoding="utf-8"
        )

    except:

        uploaded_file.seek(0)

        df = pd.read_csv(
            uploaded_file,
            encoding="cp949"
        )


except Exception as e:

    st.error(
        "CSV 파일을 읽을 수 없습니다."
    )

    st.write(e)

    st.stop()



if df.empty:

    st.error(
        "비어있는 CSV 파일입니다."
    )

    st.stop()



# ==========================
# 기본 정보
# ==========================

st.success(
    "CSV 로딩 완료"
)


col1,col2,col3 = st.columns(3)

col1.metric(
    "행 개수",
    len(df)
)

col2.metric(
    "컬럼 개수",
    len(df.columns)
)

col3.metric(
    "결측치",
    int(df.isna().sum().sum())
)



st.subheader("📄 데이터 미리보기")

st.dataframe(
    df.head(20),
    use_container_width=True
)



# ==========================
# 데이터 타입 변환
# ==========================


# 숫자 컬럼 찾기

# ==========================
# 숫자 컬럼 자동 탐색 (수정)
# ==========================

numeric_columns = []

for col in df.columns:

    converted = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    # 전체 데이터 중 70% 이상이 숫자인 경우만 선택
    ratio = converted.notna().mean()

    if ratio >= 0.7:

        df[col] = converted

        numeric_columns.append(col)




# 날짜 컬럼 찾기

date_column = None


for col in df.columns:

    try:

        converted = pd.to_datetime(
            df[col]
        )

        valid_ratio = converted.notna().mean()


        if valid_ratio > 0.5:

            date_column = col

            df[col] = converted

            break


    except:

        pass



# ==========================
# 날짜 처리
# ==========================

if date_column:

    st.sidebar.success(
        f"날짜 발견: {date_column}"
    )

    df["분석날짜"] = df[date_column]


else:

    st.sidebar.warning(
        "날짜 컬럼 없음"
    )



# ==========================
# 분석 컬럼 선택
# ==========================

if len(numeric_columns)==0:

    st.error(
        "분석 가능한 숫자 데이터가 없습니다."
    )

    st.stop()



st.sidebar.header(
    "분석 설정"
)


selected_columns = st.sidebar.multiselect(

    "분석할 숫자 컬럼 선택",

    numeric_columns,

    default=numeric_columns[:3]

)



if len(selected_columns)==0:

    st.warning(
        "컬럼을 선택하세요."
    )

    st.stop()



# ==========================
# 통계 분석
# ==========================


st.header(
    "📊 통계 분석"
)


for col in selected_columns:


    st.subheader(
        f"📌 {col}"
    )


    a,b,c,d = st.columns(4)

value = pd.to_numeric(
    df[col],
    errors="coerce"
)

a.metric(
    "평균",
    f"{value.mean():.2f}"
)

b.metric(
    "최대",
    f"{value.max():.2f}"
)

c.metric(
    "최소",
    f"{value.min():.2f}"
)

d.metric(
    "표준편차",
    f"{value.std():.2f}"
)



# ==========================
# 그래프
# ==========================


st.header(
    "📈 시각화"
)



for col in selected_columns:


    st.subheader(
        col
    )


    if date_column:


        fig = px.line(

            df,

            x="분석날짜",

            y=col,

            markers=True,

            title=f"{col} 변화"

        )


    else:


        fig = px.histogram(

            df,

            x=col,

            title=f"{col} 분포"

        )


    st.plotly_chart(

        fig,

        use_container_width=True

    )



# ==========================
# 상관관계
# ==========================


if len(selected_columns)>=2:


    st.header(
        "🔗 상관관계"
    )


    corr = df[selected_columns].corr()


    fig_corr = px.imshow(

        corr,

        text_auto=True,

        color_continuous_scale="RdBu"

    )


    st.plotly_chart(

        fig_corr,

        use_container_width=True

    )



# ==========================
# 이상치 탐지
# ==========================


st.header(
    "⚠️ 이상 데이터 탐지"
)



data = pd.to_numeric(
    df[col],
    errors="coerce"
).dropna()


q1 = data.quantile(0.25)

q3 = data.quantile(0.75)

iqr = q3-q1


outlier = data[
    (data < q1-1.5*iqr)
    |
    (data > q3+1.5*iqr)
]



# ==========================
# 데이터 다운로드
# ==========================


st.header(
    "📥 다운로드"
)


csv = df.to_csv(

    index=False,

    encoding="utf-8-sig"

)


st.download_button(

    "분석 결과 다운로드",

    csv,

    "analysis_result.csv",

    "text/csv"

)


st.success(
    "분석 완료!"
)
