from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NormalizedCsv(BaseModel):
    sha256: str
    encoding: str = Field(default="utf-8-sig")
    content_b64: str


class ReportSummary(BaseModel):
    rows: Optional[int] = Field(default=None, examples=[None])
    columns: Optional[int] = Field(default=None, examples=[None])
    warnings: int = 0
    errors: int = 0
    deterministic: bool = True


class ReportItem(BaseModel):
    row: Optional[int] = None
    column: Optional[str] = None
    issue: str
    value: Optional[str] = None
    action: str


class NormalizationReport(BaseModel):
    summary: ReportSummary
    normalizations: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[ReportItem] = Field(default_factory=list)
    errors: List[ReportItem] = Field(default_factory=list)


class NormalizeResponse(BaseModel):
    normalized_csv: NormalizedCsv
    report: NormalizationReport

class HealthResponse(BaseModel):
    ok: bool = True
