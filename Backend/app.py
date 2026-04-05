from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import joblib
import numpy as np
import os
from utils.preprocessor import preprocessor

# Initialization of Fastapi
app = FastAPI(
    title="Sentiment Analyzer Api",
    description="API for sentiment analysis of product reviews",
)

# Configure Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models
MODEL_PATH = "models/best_model.pkl"
VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"
ENCODER_PATH = "models/label_encoder.pkl"

print("*"*50)
print("Loading Models...")
print("*"*50)

try:
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from path {MODEL_PATH}")
    print(f"Model type: {type(model).__name__}")
except Exception as e:
    print(f"Error Loading Model: {e}")
    model = None

try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"TF-IDF vectorizer loaded from {VECTORIZER_PATH}")
except Exception as e:
    print(f"Error Loading the vectorizer: {e}")
    vectorizer = None

try:
    encoder = joblib.load(ENCODER_PATH)
    print(f"Label-Encoder Loaded from {ENCODER_PATH}")
except Exception as e:
    print(f"Error Loading Label Encoder: {e}")
    encoder = None

print("*"*50)

# Defining the Request-Response Model
class ReviewRequest(BaseModel):
    text: str
    review_id: Optional[str] = None

class BatchReviewRequest(BaseModel):
    reviews: List[ReviewRequest]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool          # ✅ Fixed: using : not =, and bool value not type
    vectorizer_loaded: bool     # ✅ Fixed
    encoder_loaded: bool        # ✅ Fixed
    classes: List[str]

class SentimentResponse(BaseModel):
    review_id: Optional[str]
    text: str
    sentiment: str
    confidence: float
    probabilities: Optional[Dict[str, float]] = None

# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "Healthy" if model and vectorizer and encoder else "Degraded",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "encoder_loaded": encoder is not None,
        "classes": encoder.classes_.tolist() if encoder else []
    }

# Review Analysis Endpoint
@app.post("/analyze", response_model=SentimentResponse)  # ✅ Changed from GET to POST
async def analyze_sentiment(review: ReviewRequest):
    # Checking if model is loaded or not
    if model is None or vectorizer is None or encoder is None:  # ✅ Fixed condition
        raise HTTPException(status_code=503, detail="Model not loaded properly")
    
    if not review.text or not review.text.strip():  # ✅ Fixed condition
        raise HTTPException(status_code=400, detail="Review Text cannot be empty")
    
    try:
        processed_text = preprocessor.preprocess(review.text)

        if not processed_text:
            raise HTTPException(status_code=400, detail="Text contains no meaningful words after preprocessing")
        
        # Vectorize
        text_vectorized = vectorizer.transform([processed_text])

        # Predict
        prediction = model.predict(text_vectorized)[0]
        probabilities = model.predict_proba(text_vectorized)[0]  # ✅ Fixed typo: pridict_proba → predict_proba

        # Sentiment Labels
        sentiment = encoder.inverse_transform([prediction])[0]

        # Confidence score
        confidence = float(max(probabilities))

        return SentimentResponse(
            review_id=review.review_id,
            text=review.text,
            sentiment=sentiment,
            confidence=confidence
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing review: {str(e)}")
    

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Check if running in development mode
    if '--reload' in sys.argv:
        uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)  # Changed to 127.0.0.1
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)  # Changed to 127.0.0.1