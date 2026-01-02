"""
Core normalization logic will live here.

Responsibilities (v1):
- encoding detection + normalization
- dialect detection
- row length enforcement
- header normalization
- ambiguity reporting
"""

from __future__ import annotations

import base64
import hashlib
import csv
import io
from typing import Any, Dict

from charset_normalizer import from_bytes


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_encoding_to_utf8_bom(raw: bytes) -> tuple[bytes, Dict[str, Any]]:
    """
    Normalize input bytes to UTF-8 with BOM (utf-8-sig).

    Rules:
    - Detect encoding best-effort via charset-normalizer.
    - If detection is uncertain, still attempt decode using best guess.
    - If decode fails, fall back to UTF-8 with replacement characters and report it.
    - Always output utf-8-sig bytes.
    """
    detected = None
    confidence = None

    match = from_bytes(raw).best()
    if match is not None:
        detected = match.encoding
        # charset-normalizer's match internals vary by version; avoid relying on fingerprint shape
        confidence = None

    # Decode using detected encoding if available; otherwise try utf-8 first.
    decode_used = detected or "utf-8"
    # If input is UTF-8 and begins with a BOM, decode with utf-8-sig so we don't double-BOM on output.
    if raw.startswith(b"\xef\xbb\xbf") and (decode_used.lower().replace("-", "_") in ("utf_8", "utf8")):
        decode_used = "utf-8-sig"   

    decode_fallback = False

    try:
        text = raw.decode(decode_used)
    except Exception:
        # Try utf-8 as a fallback
        try:
            text = raw.decode("utf-8")
            decode_used = "utf-8"
            decode_fallback = True
        except Exception:
            # Last resort: decode with replacement so pipeline can continue deterministically
            text = raw.decode(decode_used, errors="replace")
            decode_fallback = True

    normalized = text.encode("utf-8-sig")

    # --- Newline normalization: CRLF/CR -> LF ---
    nl_before = {
        "crlf": text.count("\r\n"),
        "cr": text.count("\r") - text.count("\r\n"),
        "lf": text.count("\n"),
    }

    # Normalize to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    nl_after = {
        "crlf": text.count("\r\n"),
        "cr": text.count("\r"),
        "lf": text.count("\n"),
    }

    # --- Delimiter detection + normalization to comma ---
    sample = text[:4096]
    detected_delim = ","
    sniffed = False

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        detected_delim = dialect.delimiter
        sniffed = True
    except Exception:
        detected_delim = ","  # default

    delim_changed = detected_delim != ","

    if delim_changed:
        # Re-serialize using comma delimiter
        inp = io.StringIO(text, newline="")
        outp = io.StringIO(newline="")

        reader = csv.reader(inp, delimiter=detected_delim)
        writer = csv.writer(outp, delimiter=",", lineterminator="\n")

        for row in reader:
            writer.writerow(row)

        text = outp.getvalue()


    report = {
        "encoding": {
            "detected": detected,
            "decode_used": decode_used,
            "decode_fallback": decode_fallback,
            "output": "utf-8-bom",
            "notes": "Output is UTF-8 with BOM (utf-8-sig) for deterministic downstream handling.",
        },
        "newlines": {
            "policy": "lf",
            "before": nl_before,
            "after": nl_after,
            "changed": (nl_before["crlf"] > 0) or (nl_before["cr"] > 0),
        },
        "delimiter": {
            "detected": detected_delim,
            "output": ",",
            "sniffed": sniffed,
            "changed": delim_changed,
            "notes": "Delimiter normalized to comma.",
        },
    }



    return normalized, report


def normalize_csv_bytes(raw: bytes) -> Dict[str, Any]:
    """
    v1: only encoding normalization + report.
    Returns a dict matching the API's response envelope.
    """
    normalized_bytes, enc_report = normalize_encoding_to_utf8_bom(raw)

    b64 = base64.b64encode(normalized_bytes).decode("ascii")
    return {
        "normalized_csv": {
            "sha256": _sha256_hex(normalized_bytes),
            "encoding": "utf-8-sig",
            "content_b64": b64,
        },
        "report": {
            "summary": {
                "rows": None,
                "columns": None,
                "warnings": 0,
                "errors": 0,
                "deterministic": True,
            },
            "normalizations": enc_report,
            "warnings": [],
            "errors": [],
        },
    }
