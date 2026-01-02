# CSV Normalizer

Deterministic CSV normalization service for automation pipelines and data ingestion workflows.

This project focuses on **making CSV inputs predictable**, even when source files are messy, inconsistent, or produced by uncontrolled upstream systems.

It is designed to answer one question reliably:

> **“Can I safely feed this CSV into downstream systems without surprises?”**

---

## What this does (intentionally and explicitly)

Given an uploaded CSV file, the service:

- **Normalizes encoding**
  - Detects input encoding
  - Outputs **UTF-8 with BOM (`utf-8-sig`)** consistently
- **Normalizes newlines**
  - Converts CRLF / CR → LF
- **Normalizes delimiter**
  - Detects common delimiters (`;`, `,`, `\t`, `|`)
  - Outputs comma-delimited CSV
- **Enforces rectangular shape**
  - Determines expected column count from the header
  - **Short rows are padded**
  - **Long rows are preserved but reported as errors**
- **Preserves data determinism**
  - The same input always produces the same output bytes
- **Produces a structured report**
  - What was detected
  - What was changed
  - What rows were padded
  - What rows exceeded expected width

This service does **not** attempt to guess business meaning, clean values, or “fix” bad data silently.  
All ambiguity is surfaced explicitly in the report.

---

## Design principles

- Deterministic over clever
- Report, don’t hide
- Normalize format, not semantics
- Automation-first behavior
- Errors are data issues, not transport failures

A file with data problems still returns HTTP `200`.  
Those problems are surfaced in the response body, not through HTTP status codes.

This makes the service suitable for CI pipelines, batch jobs, and ingestion systems that must continue running while capturing data quality issues.

---

## API overview

### `POST /normalize`

Accepts a CSV file as `multipart/form-data` and returns:

- Base64-encoded normalized CSV bytes
- SHA-256 hash of the normalized output
- Detailed normalization report
- Structured warnings and errors

The output CSV is always:

- UTF-8 with BOM
- LF newlines
- Comma-delimited
- Rectangular

### `GET /health`

Simple liveness endpoint.

---

## Example response (shape only)

```json
{
  "normalized_csv": {
    "sha256": "…",
    "encoding": "utf-8-sig",
    "content_b64": "…"
  },
  "report": {
    "summary": {
      "warnings": 8,
      "errors": 3,
      "deterministic": true
    },
    "normalizations": {
      "encoding": {},
      "newlines": {},
      "delimiter": {},
      "row_width": {}
    },
    "warnings": [],
    "errors": []
  }
}
