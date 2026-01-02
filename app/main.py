from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(
    title="csv-normalizer",
    description="Deterministic CSV normalization for automation pipelines",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/normalize")
async def normalize_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=422, detail="Only CSV files are supported")

    # Placeholder: real implementation comes later
    return {
        "normalized_csv": None,
        "report": {
            "summary": {
                "rows": None,
                "columns": None,
                "warnings": 0,
                "errors": 0,
                "deterministic": True,
            },
            "normalizations": {},
            "warnings": [],
            "errors": [],
        },
        "status": "not_implemented_yet",
    }
