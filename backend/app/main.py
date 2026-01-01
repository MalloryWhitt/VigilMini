import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.lda import router as lda_router

load_dotenv()

app = FastAPI(
    title="Vigil Mini",
    version="0.2.0",
    description="Civic-tech tool for visualizing U.S. lobbying relationships via the Senate LDA API",
)

cors_origins_raw = os.getenv("CORS_ORIGINS", "*").strip()

if cors_origins_raw == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "Vigil Mini",
        "description": "Influence graph explorer for the Senate LDA filings database",
        "status": "running",
        "docs": "/docs",
    }

@app.get("/api/health")
def health():
    return {"ok": True}

app.include_router(lda_router, prefix="/api/v1")
