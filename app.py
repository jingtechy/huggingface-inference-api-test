# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

# ===== 1. Load Models =====
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# ===== 2. Define FastAPI App =====
app = FastAPI(title="Multi-Model API", description="Single FastAPI service with Question Answering & Sentiment Analysis")

# ===== 3. Define the request =====
class QARequest(BaseModel):
    question: str
    context: str

class SentimentRequest(BaseModel):
    text: str

# ===== 4. Question Answering API =====
@app.post("/predict/qa")
def predict_qa(request: QARequest):
    result = qa_pipeline(question=request.question, context=request.context)
    return {"answer": result["answer"], "score": result["score"]}

# ===== 5. Sentiment Analysis API =====
@app.post("/predict/sentiment")
def predict_sentiment(request: SentimentRequest):
    result = sentiment_pipeline(request.text)
    # pipeline returns list，and extract the first result
    pred = result[0]
    return {"label": pred["label"], "score": pred["score"]}
