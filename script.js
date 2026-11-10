const API_URL = "http://127.0.0.1:2200/predict";

const form = document.getElementById("prediction-form");
const submitBtn = document.getElementById("submit-btn");
const btnLoader = document.getElementById("btn-loader");
const btnCaption = submitBtn.querySelector(".btn-caption");

// State Panes
const stateIdle = document.getElementById("state-idle");
const stateError = document.getElementById("state-error");
const stateComputed = document.getElementById("state-computed");

// Render Targets
const scoreMetric = document.getElementById("score-metric");
const gaugeFill = document.getElementById("gauge-fill");
const classificationTag = document.getElementById("classification-tag");
const classificationNotes = document.getElementById("classification-notes");
const statRatio = document.getElementById("stat-ratio");
const statStrain = document.getElementById("stat-strain");
const errorTitle = document.getElementById("error-title");
const errorDetail = document.getElementById("error-detail");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  // Exact matching payload for Pydantic StudentData schema
  const payload = {
    age: parseInt(document.getElementById("age").value, 10),
    gender: document.getElementById("gender").value,
    country: document.getElementById("country").value.trim(),
    academic_level: document.getElementById("academic_level").value,
    most_used_platform: document.getElementById("most_used_platform").value,
    purpose_of_use: document.getElementById("purpose_of_use").value,
    avg_daily_usage_hours: parseInt(document.getElementById("avg_daily_usage_hours").value, 10),
    daily_unlocks: parseInt(document.getElementById("daily_unlocks").value, 10),
    study_hours: parseInt(document.getElementById("study_hours").value, 10),
    physical_activity_hours: parseInt(document.getElementById("physical_activity_hours").value, 10),
    sleep_hours_per_night: parseInt(document.getElementById("sleep_hours_per_night").value, 10),
    stress_level: document.getElementById("stress_level").value,
  };

  setPending(true);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });

    const responseBody = await res.json();

    if (!res.ok) {
      let formattedMsg = "Data validation rejected by FastAPI.";
      if (Array.isArray(responseBody.detail)) {
        formattedMsg = responseBody.detail
          .map((err) => `${err.loc.slice(1).join(".")}: ${err.msg}`)
          .join(" | ");
      } else if (typeof responseBody.detail === "string") {
        formattedMsg = responseBody.detail;
      }
      throw new Error(formattedMsg);
    }

    renderPrediction(responseBody.predicted_mental_health_score, payload);
  } catch (err) {
    renderFailure("Prediction Failed", err.message || "Could not connect to FastAPI server.");
  } finally {
    setPending(false);
  }
});

function setPending(isPending) {
  submitBtn.disabled = isPending;
  if (isPending) {
    btnLoader.classList.remove("hidden");
    btnCaption.textContent = "Calculating Vectors...";
  } else {
    btnLoader.classList.add("hidden");
    btnCaption.textContent = "Run Neural Inference";
  }
}

// Numerical count-up animation
function animateScore(target, element, duration = 1000) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease-out cubic
    const ease = 1 - Math.pow(1 - progress, 3);
    const currentVal = start + (target - start) * ease;
    
    element.textContent = currentVal.toFixed(2);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

function renderPrediction(score, payload) {
  stateIdle.classList.add("hidden");
  stateError.classList.add("hidden");
  stateComputed.classList.remove("hidden");

  // Animate numerical score
  animateScore(score, scoreMetric);

  // Normalize gauge percentage assuming a 0 to 10 scale
  const gaugePercent = Math.min(Math.max((score / 10) * 100, 5), 100);
  setTimeout(() => {
    gaugeFill.style.width = `${gaugePercent}%`;
  }, 100);

  // Calculate lifestyle screen-to-sleep ratio
  const ratio = (payload.avg_daily_usage_hours / (payload.sleep_hours_per_night || 1)).toFixed(2);
  statRatio.textContent = `${ratio}x Screen/Sleep`;
  statStrain.textContent = `${payload.stress_level} Strain`;

  // Qualitative analysis based on score
  if (score <= 3.5) {
    classificationTag.textContent = "Resilient / Low Strain";
    classificationTag.style.color = "#81b29a";
    classificationTag.style.borderColor = "rgba(129, 178, 154, 0.4)";
    classificationNotes.textContent = "Metrics suggest balanced habits and sufficient nightly rest intervals.";
  } else if (score <= 6.5) {
    classificationTag.textContent = "Moderate Pressure";
    classificationTag.style.color = "#e2b16a";
    classificationTag.style.borderColor = "rgba(226, 177, 106, 0.4)";
    classificationNotes.textContent = "Notable digital screen usage observed relative to recovery hours.";
  } else {
    classificationTag.textContent = "High Strain Alert";
    classificationTag.style.color = "#ef7d7d";
    classificationTag.style.borderColor = "rgba(239, 125, 125, 0.4)";
    classificationNotes.textContent = "Sustained lifestyle indicators suggest elevated fatigue and strain.";
  }
}

function renderFailure(title, detail) {
  stateIdle.classList.add("hidden");
  stateComputed.classList.add("hidden");
  stateError.classList.remove("hidden");

  errorTitle.textContent = title;
  errorDetail.textContent = detail;
}