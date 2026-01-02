from fastapi import FastAPI, UploadFile, File, HTTPException
from .models import NormalizeResponse, HealthResponse
from .normalize import normalize_csv_bytes

app = FastAPI(
    title="csv-normalizer",
    description="Deterministic CSV normalization for automation pipelines",
    version="0.1.0",
)

@app.get("/health", response_model=HealthResponse)
def health():
    return {"ok": True}

@app.post("/normalize", response_model=NormalizeResponse)
async def normalize_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="Only CSV files are supported")

    raw = await file.read()
    return normalize_csv_bytes(raw)
