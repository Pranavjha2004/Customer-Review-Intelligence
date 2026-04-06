from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import joblib
import numpy as np
import os
from utils.preprocessor import preprocessor

import nltk
import sys

# Configure NLTK data path for production
if os.environ.get("RENDER"):
    # Running on Render
    nltk_data_dir = "/opt/render/nltk_data"
    os.makedirs(nltk_data_dir, exist_ok=True)
    nltk.data.path.append(nltk_data_dir)
else:
    # Running locally
    nltk_data_dir = None

# Download NLTK data with proper path
for package in ['punkt', 'stopwords', 'wordnet']:
    try:
        nltk.data.find(f'tokenizers/{package}')
    except LookupError:
        nltk.download(package, download_dir=nltk_data_dir)

# Initialization of Fastapi
app = FastAPI(
    title="Sentiment Analyzer Api",
    description="API for sentiment analysis of product reviews",
)

# Configure CORS - Add your production URLs
ALLOWED_ORIGINS = [
    "http://localhost:5173",           # Local Vite
    "http://127.0.0.1:5173",          # Local Vite alternative
    "https://customer-review-intelligence.vercel.app",  # REPLACE with your Netlify URL   # REPLACE with your Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
    print(f"✅ Model loaded from path {MODEL_PATH}")
    print(f"   Model type: {type(model).__name__}")
except Exception as e:
    print(f"❌ Error Loading Model: {e}")
    model = None

try:
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"✅ TF-IDF vectorizer loaded from {VECTORIZER_PATH}")
    print(f"   Features: {len(vectorizer.get_feature_names_out())}")
except Exception as e:
    print(f"❌ Error Loading the vectorizer: {e}")
    vectorizer = None

try:
    encoder = joblib.load(ENCODER_PATH)
    print(f"✅ Label-Encoder Loaded from {ENCODER_PATH}")
    print(f"   Classes: {encoder.classes_}")
except Exception as e:
    print(f"❌ Error Loading Label Encoder: {e}")
    encoder = None

print("*"*50)

# Test model with sample (optional, good for debugging)
if all([model, vectorizer, encoder]):
    try:
        test_text = "good product"
        test_processed = preprocessor.preprocess(test_text)
        if test_processed:
            test_vec = vectorizer.transform([test_processed])
            test_pred = model.predict(test_vec)[0]
            test_label = encoder.inverse_transform([test_pred])[0]
            print(f"✅ Model test successful: '{test_text}' -> {test_label}")
    except Exception as e:
        print(f"⚠️ Model test warning: {e}")

# Defining the Request-Response Model
class ReviewRequest(BaseModel):
    text: str
    review_id: Optional[str] = None

class BatchReviewRequest(BaseModel):
    reviews: List[ReviewRequest]

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    vectorizer_loaded: bool
    encoder_loaded: bool
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

# Root endpoint for quick check
@app.get("/")
async def root():
    return {
        "message": "Sentiment Analysis API is running",
        "status": "active",
        "endpoints": ["/health", "/analyze", "/docs"]
    }

# Review Analysis Endpoint
@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(review: ReviewRequest):
    # Checking if model is loaded or not
    if model is None or vectorizer is None or encoder is None:
        raise HTTPException(status_code=503, detail="Model not loaded properly")
    
    if not review.text or not review.text.strip():
        raise HTTPException(status_code=400, detail="Review Text cannot be empty")
    
    try:
        print(f"\n📝 Processing review: {review.text[:100]}...")
        
        processed_text = preprocessor.preprocess(review.text)
        print(f"🔧 Processed text: {processed_text[:100] if processed_text else 'empty'}...")

        if not processed_text:
            raise HTTPException(status_code=400, detail="Text contains no meaningful words after preprocessing")
        
        # Vectorize
        text_vectorized = vectorizer.transform([processed_text])
        print(f"📊 Vectorized shape: {text_vectorized.shape}")
        
        # Predict
        prediction = model.predict(text_vectorized)[0]
        print(f"🎯 Prediction (encoded): {prediction}")
        
        # Get probabilities
        try:
            probabilities = model.predict_proba(text_vectorized)[0]
            print(f"📈 Probabilities: {probabilities}")
            confidence = float(max(probabilities))
        except AttributeError:
            # Model doesn't have predict_proba (like SVM)
            print("⚠️ Model doesn't have predict_proba, using default confidence")
            probabilities = [0.0] * len(encoder.classes_)
            probabilities[prediction] = 1.0
            confidence = 0.95
        except Exception as proba_error:
            print(f"❌ Error in predict_proba: {proba_error}")
            confidence = 0.90
            probabilities = [0.0] * len(encoder.classes_)
            probabilities[prediction] = confidence
            remaining = (1.0 - confidence) / (len(encoder.classes_) - 1) if len(encoder.classes_) > 1 else 0
            for i in range(len(probabilities)):
                if i != prediction:
                    probabilities[i] = remaining

        # Sentiment Labels
        sentiment = encoder.inverse_transform([prediction])[0]
        print(f"✅ Sentiment: {sentiment} (confidence: {confidence:.2%})")

        # Create probabilities dict
        prob_dict = {
            label: float(prob) 
            for label, prob in zip(encoder.classes_, probabilities)
        }

        return SentimentResponse(
            review_id=review.review_id,
            text=review.text,
            sentiment=sentiment,
            confidence=confidence,
            probabilities=prob_dict
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing review: {str(e)}")
    

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)