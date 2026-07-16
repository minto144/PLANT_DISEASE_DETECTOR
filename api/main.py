"""
main.py — FastAPI server for plant disease detection.
Deployed on Render. Frontend on Vercel.
"""

import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .predict import predict, load_model
from .classes import CLASS_LABELS, DISEASE_INFO

app = FastAPI(
    title="Plant Disease Detection API",
    description="Upload a leaf image to identify plant diseases using deep learning.",
    version="1.0.0",
)

# Allow requests from local dev + Vercel deployment
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.vercel.app",   # your Vercel frontend
    "*",                       # open during development — restrict after launch
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    print("🌿 Plant Disease API starting...")
    try:
        load_model()
        print("✅ Model ready.")
    except FileNotFoundError as e:
        print(f"⚠️  {e}")


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Plant Disease Detection API is running.",
        "docs": "/docs",
    }


@app.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG.",
        )
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    try:
        result = predict(contents, top_k=3)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    return {"success": True, "filename": file.filename, **result}


@app.get("/classes")
def list_classes():
    classes = []
    for label in CLASS_LABELS:
        info = DISEASE_INFO.get(label, {})
        classes.append({
            "label": label,
            "name": info.get("name", label),
            "plant": info.get("plant", "Unknown"),
            "severity": info.get("severity", "unknown"),
        })
    return {"total": len(classes), "classes": classes}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
