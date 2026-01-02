# csv-normalizer

A small, opinionated CSV normalization service for automation pipelines.

**Goal:** turn “messy CSV that breaks imports/parsers” into a deterministic, import-safe CSV **plus** a machine-readable report of what changed and what was ambiguous.

This is intentionally **not** an ETL platform, not a schema mapper, and not a business-rule validator.

---

## Why this exists

Real-world CSVs are often inconsistent (dialect, quoting, encoding, row length, headers, dates). Most tools either fail, require complex configuration, or silently guess.

**csv-normalizer** takes a different stance:

- Normalize the structure deterministically
- **Never guess** when data is ambiguous
- Report every correction and every ambiguity

This makes it safe to use in CI/ETL/import pipelines where reproducibility matters.

---

## Contract (v1)

Given an input CSV, the service produces:

- A **deterministic normalized CSV**
  - consistent delimiter + quoting rules
  - consistent column count (row length)
  - normalized headers
  - normalized encoding (UTF-8 with BOM)
- A **machine-readable normalization report**
  - what was detected
  - what was changed
  - what was ambiguous (and therefore left unchanged)

**Non-negotiable rule:** if a value cannot be normalized safely, it is **not guessed**. It is left as-is and flagged in the report.

---

## Non-goals (intentional)

This project does **not** attempt to:

- infer business semantics (“this column is currency”)
- do per-customer configuration / rules DSL
- validate against user-provided schemas
- silently fix ambiguous dates/locales
- guarantee how Excel visually renders values

If you need those, build them downstream using the report output from this service.

---

## API

### `POST /normalize`

**Input:** `multipart/form-data` with `file` field containing CSV bytes.

**Output:** JSON with:
- `normalized_csv` (artifact reference)
- `report` (normalization details)

Example response shape:

```json
{
  "normalized_csv": {
    "sha256": "…",
    "download_url": "…"
  },
  "report": {
    "summary": { "rows": 10432, "columns": 18, "warnings": 7, "errors": 0 },
    "normalizations": {
      "encoding": { "from": "latin-1", "to": "utf-8-bom" },
      "delimiter": { "detected": ";", "normalized_to": "," },
      "headers": { "Order Date ": "order_date", "Customer-ID": "customer_id" }
    },
    "warnings": [
      {
        "row": 341,
        "column": "invoice_date",
        "issue": "ambiguous_date_format",
        "value": "03/04/2024",
        "action": "left_unchanged"
      }
    ],
    "errors": []
  }
}
