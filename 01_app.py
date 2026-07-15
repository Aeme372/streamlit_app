import streamlit as st
import requests
import random

st.set_page_config(
    page_title="오늘 뭐 먹지?",
    page_icon="🍽️",
    layout="wide"
)

# -----------------------------
# API KEY
# -----------------------------
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# -----------------------------
# 음식 데이터
# -----------------------------

foods = {

    "hot": [
        {
            "name":"냉면",
            "image":"https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=900",
            "calorie":"520 kcal",
            "protein":"18 g",
            "carb":"78 g",
            "fat":"9 g"
        },
        {
            "name":"초밥",
            "image":"https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=900",
            "calorie":"430 kcal",
            "protein":"24 g",
            "carb":"60 g",
            "fat":"8 g"
        },
        {
            "name":"샐러드",
            "image":"https://images.unsplash.com/photo-1546793665-c74683f339c1?w=900",
            "calorie":"320 kcal",
            "protein":"14 g",
            "carb":"21 g",
            "fat":"10 g"
        }
    ],

    "cold":[
        {
            "name":"김치찌개",
            "image":"https://images.unsplash.com/photo-1604908176997-4313d8e74776?w=900",
            "calorie":"610 kcal",
            "protein":"28 g",
            "carb":"35 g",
            "fat":"26 g"
        },
        {
            "name":"삼계탕",
            "image":"https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=900",
            "calorie":"720 kcal",
            "protein":"55 g",
            "carb":"18 g",
            "fat":"36 g"
        }
    ],

    "rain":[
        {
            "name":"파전",
            "image":"https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=900",
            "calorie":"680 kcal",
            "protein":"20 g",
            "carb":"62 g",
            "fat":"38 g"
        },
        {
            "name":"칼국수",
            "image":"https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=900",
            "calorie":"590 kcal",
            "protein":"21 g",
            "carb":"82 g",
            "fat":"13 g"
        }
    ],

    "snow":[
        {
            "name":"전골",
            "image":"https://images.unsplash.com/photo-1544025162-d76694265947?w=900",
            "calorie":"540 kcal",
            "protein":"38 g",
            "carb":"28 g",
            "fat":"20 g"
        }
    ],

    "normal":[
        {
            "name":"비빔밥",
            "image":"https://images.unsplash.com/photo-1512058564366-18510be2db19?w=900",
            "calorie":"560 kcal",
            "protein":"20 g",
            "carb":"70 g",
            "fat":"15 g"
        },
        {
            "name":"불고기",
            "image":"https://images.unsplash.com/photo-1600891964092-4316c288032e?w=900",
            "calorie":"640 kcal",
            "protein":"40 g",
            "carb":"26 g",
            "fat":"30 g"
        }
    ]
}

# -----------------------------
# 날씨 가져오기
# -----------------------------

def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    res = requests.get(url).json()

    return res

# -----------------------------
# 추천 알고리즘
# -----------------------------

def recommend(weather,temp):

    weather = weather.lower()

    if "rain" in weather:
        return random.choice(foods["rain"])

    if "snow" in weather:
        return random.choice(foods["snow"])

    if temp >= 28:
        return random.choice(foods["hot"])

    if temp <= 10:
        return random.choice(foods["cold"])

    return random.choice(foods["normal"])

# -----------------------------
# UI
# -----------------------------

st.title("🍽️ 오늘 날씨에 어울리는 음식 추천")

city = st.text_input(
    "도시 입력",
    value="Seoul"
)

if st.button("추천받기"):

    data = get_weather(city)

    if data["cod"] != 200:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    temp = data["main"]["temp"]

    weather = data["weather"][0]["main"]

    desc = data["weather"][0]["description"]

    food = recommend(weather,temp)

    col1,col2 = st.columns([1,1])

    with col1:

        st.subheader("🌤️ 오늘의 날씨")

        st.metric(
            "기온",
            f"{temp:.1f}°C"
        )

        st.write(desc)

    with col2:

        st.subheader("🍴 추천 음식")

        st.image(food["image"],use_container_width=True)

        st.success(food["name"])

        st.write(f"🔥 칼로리 : {food['calorie']}")

        st.write(f"🥩 단백질 : {food['protein']}")

        st.write(f"🍚 탄수화물 : {food['carb']}")

        st.write(f"🥑 지방 : {food['fat']}")
