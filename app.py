import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from PIL import Image
from streamlit_mic_recorder import mic_recorder
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Healthcare AI Agent",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
h1 {
    text-align:center;
    color:#1E88E5;
}
.stButton > button{
    width:100%;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# ENVIRONMENT
# -----------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect(
    "health.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS medication(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
time TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bmi_logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
weight REAL,
height REAL,
bmi REAL,
date TEXT
)
""")

conn.commit()

# -----------------------------
# TITLE
# -----------------------------
st.title("🏥 Smart Healthcare Monitoring AI Agent")

# -----------------------------
# SIDEBAR
# -----------------------------
menu = st.sidebar.radio(
    "Choose Feature",
    [
        "Dashboard",
        "Medication Tracker",
        "BMI Calculator",
        "Nutrition Advisor",
        "Symptom Checker",
        "AI Health Assistant",
        "Voice Assistant",
        "Image Analysis",
        "Reports"
    ]
)

# -----------------------------
# DASHBOARD
# -----------------------------
if menu == "Dashboard":

    st.header("📊 Health Dashboard")

    df = pd.read_sql(
        "SELECT * FROM bmi_logs",
        conn
    )

    if len(df) > 0:

        latest_bmi = round(
            df.iloc[-1]["bmi"],
            2
        )

        st.metric(
            "Latest BMI",
            latest_bmi
        )

        fig = px.line(
            df,
            x="date",
            y="bmi",
            title="BMI Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info(
            "No BMI records available."
        )

# -----------------------------
# MEDICATION TRACKER
# -----------------------------
elif menu == "Medication Tracker":

    st.header("💊 Medication Tracker")

    medicine = st.text_input(
        "Medicine Name"
    )

    med_time = st.time_input(
        "Reminder Time"
    )

    if st.button(
        "Save Medication"
    ):

        cursor.execute(
            """
            INSERT INTO medication(name,time)
            VALUES (?,?)
            """,
            (
                medicine,
                str(med_time)
            )
        )

        conn.commit()

        st.success(
            "Medication Saved"
        )

    meds = pd.read_sql(
        "SELECT * FROM medication",
        conn
    )

    st.dataframe(meds)

# -----------------------------
# BMI
# -----------------------------
elif menu == "BMI Calculator":

    st.header("⚖️ BMI Calculator")

    weight = st.number_input(
        "Weight (kg)",
        min_value=1.0
    )

    height = st.number_input(
        "Height (m)",
        min_value=0.5
    )

    if st.button(
        "Calculate BMI"
    ):

        bmi = weight / (height ** 2)

        cursor.execute(
            """
            INSERT INTO bmi_logs
            (weight,height,bmi,date)
            VALUES (?,?,?,?)
            """,
            (
                weight,
                height,
                bmi,
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            )
        )

        conn.commit()

        st.success(
            f"Your BMI is {round(bmi,2)}"
        )

# -----------------------------
# NUTRITION ADVISOR
# -----------------------------
elif menu == "Nutrition Advisor":

    st.header("🥗 Nutrition Advisor")

    goal = st.selectbox(
        "Select Goal",
        [
            "Weight Loss",
            "Weight Gain",
            "Healthy Lifestyle"
        ]
    )

    if st.button(
        "Generate Diet Plan"
    ):

        prompt = f"""
        Create a healthy Indian diet plan for:
        {goal}
        """

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            st.write(
                response.choices[0].message.content
            )

        except Exception as e:
            st.error(str(e))

# -----------------------------
# SYMPTOM CHECKER
# -----------------------------
elif menu == "Symptom Checker":

    st.header("🩺 Symptom Checker")

    symptoms = st.text_area(
        "Enter Symptoms"
    )

    if st.button(
        "Analyze Symptoms"
    ):

        prompt = f"""
        Symptoms:
        {symptoms}

        Explain possible causes.
        Add a disclaimer that this is not a diagnosis.
        """

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            st.write(
                response.choices[0].message.content
            )

        except Exception as e:
            st.error(str(e))

# -----------------------------
# AI ASSISTANT
# -----------------------------
elif menu == "AI Health Assistant":

    st.header("🤖 AI Health Assistant")

    question = st.text_area(
        "Ask your health question"
    )

    if st.button(
        "Ask Assistant"
    ):

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role":"user",
                        "content":question
                    }
                ]
            )

            st.write(
                response.choices[0].message.content
            )

        except Exception as e:
            st.error(str(e))

# -----------------------------
# VOICE ASSISTANT
# -----------------------------
elif menu == "Voice Assistant":

    st.header("🎤 Voice Assistant")

    audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording"
    )

    if audio:
        st.success(
            "Audio Recorded Successfully"
        )

# -----------------------------
# IMAGE ANALYSIS
# -----------------------------
elif menu == "Image Analysis":

    st.header("📸 Image Analysis")

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=[
            "png",
            "jpg",
            "jpeg"
        ]
    )

    if uploaded_file:

        image = Image.open(
            uploaded_file
        )

        st.image(
            image,
            use_container_width=True
        )

        description = st.text_input(
            "Describe the image"
        )

        if st.button(
            "Analyze Image"
        ):

            prompt = f"""
            Analyze this healthcare image.

            Description:
            {description}

            Provide:
            - Possible identification
            - Health information
            - Safety recommendations
            """

            try:

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role":"user",
                            "content":prompt
                        }
                    ]
                )

                st.write(
                    response.choices[0].message.content
                )

            except Exception as e:
                st.error(str(e))

# -----------------------------
# REPORTS
# -----------------------------
elif menu == "Reports":

    st.header("📄 Reports")

    logs = pd.read_sql(
        "SELECT * FROM bmi_logs",
        conn
    )

    st.dataframe(logs)

    csv = logs.to_csv(
        index=False
    )

    st.download_button(
        "Download CSV Report",
        csv,
        "health_report.csv",
        "text/csv"
    )