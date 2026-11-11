import joblib
from pathlib import Path
import pandas as pd
import streamlit as st

# Configure layout and browser tab metadata
st.set_page_config(
    page_title="Mental Health Predictor",
    page_icon="🧠",
    layout="wide"
)

# Robust model loading with caching
MODEL_PATH = Path(__file__).resolve().parent / "Mental_health_model.pkl"

@st.cache_resource
def load_trained_model():
    return joblib.load(MODEL_PATH)

try:
    model = load_trained_model()
except Exception as e:
    st.error(f"Failed to load model file 'Mental_health_model.pkl': {e}")
    st.stop()

top_countries = [
    "Other", "India", "USA", "Canada", "Australia",
    "UK", "Germany", "Mexico", "Turkey", "France"
]

# Header section
st.title("🧠 Mental Health Predictor")
st.markdown("Estimate student psychological balance using lifestyle habits and digital interaction metrics.")
st.divider()

# Input controls arranged in a 3-column layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Demographics")
    age = st.number_input("Age", min_value=1, max_value=100, value=21)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    country = st.text_input("Country", value="India")
    academic_level = st.selectbox(
        "Academic Level", 
        ["High School", "Undergraduate", "Graduate"]
    )

with col2:
    st.subheader("2. Digital Habits")
    most_used_platform = st.selectbox(
        "Most Used Platform",
        [
            "Facebook", "Instagram", "LinkedIn", "Snapchat", 
            "Twitter", "YouTube", "TikTok", "WhatsApp", 
            "WeChat", "LINE", "KakaoTalk", "VKontakte"
        ]
    )
    purpose_of_use = st.selectbox(
        "Purpose of Use", 
        ["Education", "Networking", "Entertainment", "News"]
    )
    avg_daily_usage_hours = st.slider("Daily Screen Time (Hours)", 1, 23, 5)
    daily_unlocks = st.number_input("Daily Phone Unlocks", min_value=1, max_value=500, value=80)

with col3:
    st.subheader("3. Lifestyle & Strain")
    study_hours = st.number_input("Daily Study (Hours)", min_value=1, max_value=24, value=4)
    physical_activity_hours = st.slider("Physical Activity (Hours)", 0, 23, 2)
    sleep_hours_per_night = st.slider("Nightly Sleep (Hours)", 1, 23, 7)
    stress_level = st.selectbox(
        "Reported Stress Level", 
        ["Low", "Medium", "High", "Very High"]
    )

st.divider()

# Inference and score rendering
if st.button("Predict Mental Health Score", use_container_width=True, type="primary"):
    with st.spinner("Processing feature vectors..."):
        country_group = country if country in top_countries else "Other"
        
        # DataFrame matching the exact scikit-learn feature columns
        input_data = pd.DataFrame([{
            "Age": age,
            "Gender": gender,
            "Country": country,
            "Academic_Level": academic_level,
            "Most_Used_Platform": most_used_platform,
            "Purpose_Of_Use": purpose_of_use,
            "Avg_Daily_Usage_Hours": avg_daily_usage_hours,
            "Daily_Unlocks": daily_unlocks,
            "Study_Hours": study_hours,
            "Physical_Activity_Hours": physical_activity_hours,
            "Sleep_Hours_Per_Night": sleep_hours_per_night,
            "Stress_Level": stress_level,
            "Grouped_countries": country_group
        }])
        
        try:
            raw_pred = model.predict(input_data)[0]
            score = round(float(raw_pred), 2)
            
            st.success("### Assessment Complete")
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.metric(label="Predicted Score Index", value=f"{score} / 10")
            
            with res_col2:
                if score <= 3.5:
                    st.info("**Favorable / Low Strain:** Balanced habits and regular recovery intervals.")
                elif score <= 6.5:
                    st.warning("**Moderate Pressure:** High digital interaction relative to restorative rest.")
                else:
                    st.error("**Elevated Strain Alert:** Lifestyle metrics suggest sustained fatigue and stress.")
                    
        except Exception as err:
            st.error(f"Inference pipeline failed: {err}")