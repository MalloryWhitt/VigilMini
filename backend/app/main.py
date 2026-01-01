import os
import requests
from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI(title="Vigil Mini")

@app.get("/")
def root():
    return {
        "name": "Vigil Mini",
        "description": "Civic-tech tool for visualizing U.S. lobbying relationships",
        "status": "running"
    }

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/lda/ping")
def lda_ping():
    """
    Calls the Senate LDA API once and returns basic metadata.
    Requires environment variable LDA_API_KEY.
    """
    api_key = os.getenv("LDA_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing LDA_API_KEY environment variable")

    url = "https://lda.senate.gov/api/v1/filings/"
    headers = {"Authorization": f"Token {api_key}"}

    r = requests.get(url, headers=headers, params={"page_size": 1}, timeout=20)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    data = r.json()
    return {
        "status": "ok",
        "count": data.get("count"),
        "next": data.get("next"),
        "sample_keys": list((data.get("results") or [{}])[0].keys()),
    }
