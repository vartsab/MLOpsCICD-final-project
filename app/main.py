import os
from fastapi import FastAPI, Response
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from pathlib import Path
import time
import logging
import joblib
import numpy as np

from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# --------------------------------------------------
# Basic logging to stdout so Kubernetes/Loki can read it later
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AIOps Quality Inference Service", version="1.0.0")

# --------------------------------------------------
# Paths / model globals
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "model.pkl"
MODEL_VERSION = os.getenv("MODEL_VERSION", "0.3.0")
model = None

# --------------------------------------------------
# Prometheus metrics
# --------------------------------------------------
REQUEST_COUNT = Counter(
    "inference_requests_total",
    "Total number of inference requests"
)

DRIFT_COUNT = Counter(
    "inference_drift_detected_total",
    "Total number of requests where drift was detected"
)

PREDICTION_LATENCY = Histogram(
    "inference_request_latency_seconds",
    "Inference request latency in seconds"
)

# --------------------------------------------------
# Request/Response schemas
# --------------------------------------------------
class PredictRequest(BaseModel):
    features: List[float] = Field(..., min_length=3, max_length=3, description="Input feature vector with exactly 3 values")


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prediction: int
    score: float
    drift_detected: bool
    model_version: str


# --------------------------------------------------
# Model loading
# --------------------------------------------------
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    loaded_model = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded successfully from {MODEL_PATH}")
    return loaded_model


@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


# --------------------------------------------------
# Core prediction function
# --------------------------------------------------
def predict(data: List[float]) -> dict:
    features_array = np.array([data], dtype=float)
    prediction = int(model.predict(features_array)[0])

    if hasattr(model, "predict_proba"):
        score = float(model.predict_proba(features_array)[0][1])
    else:
        score = float(prediction)

    return {
        "prediction": prediction,
        "score": round(score, 4)
    }


# --------------------------------------------------
# Mock drift detector
# --------------------------------------------------
def detect_drift(data: List[float]) -> bool:
    return any(abs(x) > 5 for x in data)


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "model_loaded": model is not None
    }


# --------------------------------------------------
# Metrics endpoint
# --------------------------------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------
@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    start_time = time.time()
    REQUEST_COUNT.inc()

    logger.info(f"Incoming request features={request.features}")

    result = predict(request.features)
    drift_detected = detect_drift(request.features)

    if drift_detected:
        DRIFT_COUNT.inc()
        logger.warning("Drift detected")

    latency_seconds = time.time() - start_time
    PREDICTION_LATENCY.observe(latency_seconds)
    latency_ms = round(latency_seconds * 1000, 2)

    logger.info(
        f"Prediction completed prediction={result['prediction']} "
        f"score={result['score']} drift_detected={drift_detected} "
        f"latency_ms={latency_ms}"
    )

    return PredictResponse(
        prediction=result["prediction"],
        score=result["score"],
        drift_detected=drift_detected,
        model_version=MODEL_VERSION
    )
