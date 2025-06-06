import streamlit as st
import requests
import pandas as pd
import altair as alt
import time
from datetime import datetime
import google.generativeai as genai



st.set_page_config(page_title="Pollution Tracker", layout="centered")

# Get Coordinates
def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=9cca211b2e1aa3778c855e09ba35522e"
    res = requests.get(url)
    if res.status_code == 200 and res.json():
        data = res.json()[0]
        return data['lat'], data['lon']
    return None, None

# Get Current AQI
def get_air_quality(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=9cca211b2e1aa3778c855e09ba35522e"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

# Get Historical AQI
def get_historical_air_quality(lat, lon, hours=24):
    end_time = int(time.time())
    start_time = end_time - hours * 3600
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_time}&end={end_time}&appid=9cca211b2e1aa3778c855e09ba35522e"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

# Gemini Chatbot Function
def ask_gemini(prompt):
    response_text = ""
    
    if prompt:
        genai.configure(api_key="AIzaSyDyHSktxPtcOk8w2h16phzpKwkjvgDBncU")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text
    return response_text

aqi_text = {
    1: ("Good 😊", "#2ECC71"),
    2: ("Fair 🙂", "#F1C40F"),
    3: ("Moderate 😐", "#E67E22"),
    4: ("Poor 😷", "#E74C3C"),
    5: ("Very Poor 😫", "#8E44AD")
}

# UI
st.title("🌍 Pollution Tracker")
st.markdown("Enter a city to view real-time AQI, pollutants, and ask Gemini AI about air quality.")

city = st.text_input("🏙️ Enter City")

if city:
    lat, lon = get_coordinates(city)
    if lat and lon:
        pollution_data = get_air_quality(lat, lon)
        if pollution_data:
            aqi = pollution_data['list'][0]['main']['aqi']
            components = pollution_data['list'][0]['components']
            aqi_status, aqi_color = aqi_text.get(aqi, ("Unknown", "#95A5A6"))

            st.markdown(f"""
                <div style="background-color:{aqi_color};padding:1rem;border-radius:10px">
                    <h3 style="color:white">Air Quality in {city.title()}</h3>
                    <h1 style="color:white;text-align:center;">AQI: {aqi} - {aqi_status}</h1>
                </div>
            """, unsafe_allow_html=True)

            df = pd.DataFrame(list(components.items()), columns=["Pollutant", "Concentration"])
            df["Pollutant"] = df["Pollutant"].str.upper()

            st.markdown("### 📊 Pollutant Concentration")
            col1, col2, col3 = st.columns(3)
            for i, row in df.iterrows():
                with [col1, col2, col3][i % 3]:
                    st.metric(label=row["Pollutant"], value=f"{row['Concentration']:.2f} μg/m³")

            st.markdown("### 📉 Bar Chart")
            st.altair_chart(
                alt.Chart(df).mark_bar().encode(
                    x=alt.X("Pollutant", sort="-y"),
                    y="Concentration",
                    tooltip=["Pollutant", "Concentration"]
                ).properties(width=600),
                use_container_width=True
            )

            st.markdown("### 🧁 Pie Chart")
            st.altair_chart(
                alt.Chart(df).mark_arc().encode(
                    theta="Concentration",
                    color="Pollutant",
                    tooltip=["Pollutant", "Concentration"]
                ).properties(width=600),
                use_container_width=True
            )

            st.markdown("### 🕰️ 24-Hour AQI Trend")
            hist_data = get_historical_air_quality(lat, lon)
            if hist_data and "list" in hist_data:
                hist_df = pd.DataFrame([
                    {"Datetime": datetime.utcfromtimestamp(entry["dt"]), "AQI": entry["main"]["aqi"]}
                    for entry in hist_data["list"]
                ])
                st.altair_chart(
                    alt.Chart(hist_df).mark_line(point=True).encode(
                        x="Datetime:T",
                        y=alt.Y("AQI", scale=alt.Scale(domain=[1, 5])),
                        tooltip=["Datetime", "AQI"]
                    ).properties(width=600),
                    use_container_width=True
                )
            else:
                st.info("No historical AQI data available.")

# Gemini Chat Section
st.markdown("---")
st.markdown("## 🤖 Ask Gemini AI about pollution")

if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = []

user_question = st.chat_input("Ask something like: 'How does PM2.5 affect health?'")
if user_question:
    st.session_state.gemini_chat.append(("user", user_question))
    reply = ask_gemini(user_question)
    st.session_state.gemini_chat.append(("bot", reply))

for role, msg in st.session_state.gemini_chat:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)
