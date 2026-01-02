# csv-normalizer

A small, opinionated CSV normalization service for automation pipelines.

**Purpose:** take unreliable, real-world CSV input and produce a **deterministic, import-safe CSV** along with a **machine-readable report** describing exactly what was detected, normalized, padded, or rejected.

This project is intentionally narrow in scope. It focuses on correctness, repeatability, and transparency rather than convenience or heuristics.

---

## Why this exists

CSV is deceptively simple. In practice, it frequently breaks pipelines due to:

- inconsistent encodings (UTF-8, UTF-8 BOM, Latin-1, Windows codepages)
- mixed or platform-dependent newlines
- inconsistent delimiters (`;`, `\t`, `|`)
- ragged rows (missing or extra columns)
- quoting edge cases that break downstream parsers

Most tools either fail fast or silently guess.

**csv-normalizer takes a different approach:**

- Normalize structure deterministically
- Apply explicit, documented rules
- Never silently guess when data is ambiguous
- Surface every correction and every violation in a report

This makes it suitable for CI, ingestion pipelines, and automated import workflows where reproducibility matters.

---

## Design stance (important)

This service is **not** an ETL framework and **not** a schema inference tool.

It is designed to be a *first-stage sanitizer* that produces:

1. A CSV that downstream systems can safely parse
2. A report that downstream systems (or humans) can reason about

If something cannot be normalized safely, it is **left unchanged or flagged**, never guessed.

---

## What v1 does (current behavior)

Given an input CSV, the service:

### Encoding
- Detects encoding using `charset-normalizer`
- Decodes using the detected encoding (with safe fallbacks)
- Outputs **UTF-8 with BOM (`utf-8-sig`)** for deterministic downstream handling

### Newlines
- Normalizes all line endings to `LF`
- Reports before/after counts (`CRLF`, `CR`, `LF`)

### Delimiter
- Attempts delimiter detection (``, `;`, `\t`, `|`)
- Normalizes output to **comma-delimited**
- Reports whether detection was sniffed or defaulted

### Row width (rectangularization)
- Uses the header row to establish expected column count
- Short rows are **padded** (deterministically) and reported as warnings
- Long rows are **preserved but flagged as errors**
- No rows are dropped or reordered

### Output
- Returns the normalized CSV as Base64
- Includes a SHA-256 hash of the normalized output
- Returns a detailed normalization report

---

## Explicit non-goals (by design)

This project does **not**:

- infer column semantics or data types
- interpret locale-specific dates or numbers
- apply per-customer business rules
- validate against user-provided schemas
- “fix” ambiguous values silently
- guarantee Excel’s visual rendering behavior

Those concerns belong downstream, using the report this service produces.

---

## API

### `POST /normalize`

**Input**

- `multipart/form-data`
- Field: `file` (raw CSV bytes)

**Output**

```json
{
  "normalized_csv": {
    "sha256": "…",
    "encoding": "utf-8-sig",
    "content_b64": "…"
  },
  "report": {
    "summary": {
      "rows": null,
      "columns": null,
      "warnings": 8,
      "errors": 3,
      "deterministic": true
    },
    "normalizations": {
      "encoding": { ... },
      "newlines": { ... },
      "delimiter": { ... },
      "row_width": { ... }
    },
    "warnings": [ ... ],
    "errors": [ ... ]
  }
}
