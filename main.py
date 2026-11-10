import json
from pathlib import Path
from typing import Annotated, Literal
from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import warnings
from sklearn.exceptions import InconsistentVersionWarning

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Absolute path resolution for model persistence
MODEL_PATH = Path(__file__).resolve().parent / "Mental_health_model.pkl"
model = joblib.load(MODEL_PATH)

top_countries = [
    "Other",
    "India",
    "USA",
    "Canada",
    "Australia",
    "UK",
    "Germany",
    "Mexico",
    "Turkey",
    "France",
]


class StudentData(BaseModel):
    # Standard Python snake_case field names
    age: Annotated[
        int, Field(..., gt=0, lt=100, description="Age of the student")
    ]
    gender: Annotated[
        Literal["Male", "Female", "Other"],
        Field(..., description="Gender of the student"),
    ]
    country: Annotated[str, Field(..., description="Country of the student")]
    academic_level: Annotated[
        Literal["Undergraduate", "Graduate", "High School"],
        Field(..., description="Academic level of the student"),
    ]
    most_used_platform: Annotated[
        Literal[
            "Facebook",
            "LinkedIn",
            "Instagram",
            "Snapchat",
            "Twitter",
            "YouTube",
            "TikTok",
            "LINE",
            "KakaoTalk",
            "VKontakte",
            "WhatsApp",
            "WeChat",
        ],
        Field(..., description="Most used platform by the student"),
    ]
    purpose_of_use: Annotated[
        Literal["Networking", "Education", "Entertainment", "News"],
        Field(..., description="Purpose of use for the student"),
    ]
    avg_daily_usage_hours: Annotated[
        int,
        Field(
            ...,
            gt=0,
            lt=24,
            description="Average daily usage hours of the student",
        ),
    ]
    daily_unlocks: Annotated[
        int, Field(..., gt=0, description="Daily unlocks of the student")
    ]
    study_hours: Annotated[
        int, Field(..., gt=0, description="Study hours of the student")
    ]
    physical_activity_hours: Annotated[
        int,
        Field(
            ...,
            gt=0,
            lt=24,
            description="Physical activity hours of the student",
        ),
    ]
    sleep_hours_per_night: Annotated[
        int,
        Field(
            ...,
            gt=0,
            lt=24,
            description="Sleep hours per night of the student",
        ),
    ]
    stress_level: Annotated[
        Literal["Medium", "Low", "Very High", "High"],
        Field(..., description="Stress level of the student"),
    ]


class PredictionResponse(BaseModel):
    predicted_mental_health_score: float = Field(
        ..., description="Predicted mental health score of the student"
    )


@app.get("/")
def greeting():
    return {"message": "Welcome to the Mental Health Prediction API!"}


@app.post("/predict", response_model=PredictionResponse)
def predict_mental_health(data: StudentData):
    try:
        country_group = (
            data.country if data.country in top_countries else "Other"
        )

        # Keys must match the exact column names the model was trained on
        input_data = pd.DataFrame(
            [
                {
                    "Age": data.age,
                    "Gender": data.gender,
                    "Country": data.country,
                    "Academic_Level": data.academic_level,
                    "Most_Used_Platform": data.most_used_platform,
                    "Purpose_Of_Use": data.purpose_of_use,
                    "Avg_Daily_Usage_Hours": data.avg_daily_usage_hours,
                    "Daily_Unlocks": data.daily_unlocks,
                    "Study_Hours": data.study_hours,
                    "Physical_Activity_Hours": data.physical_activity_hours,
                    "Sleep_Hours_Per_Night": data.sleep_hours_per_night,
                    "Stress_Level": data.stress_level,
                    "Grouped_countries": country_group,
                }
            ]
        )

        raw_prediction = model.predict(input_data)[0]

        return PredictionResponse(
            predicted_mental_health_score=round(float(raw_prediction), 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Inference error: {str(e)}"
        )