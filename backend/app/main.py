from fastapi import FastAPI

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