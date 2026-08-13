from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.evidence import EvidenceItem, EvidencePaperSummary


class Verdict(str, Enum):
    SUPPORTS = "SUPPORTS"
    OVERSTATED = "OVERSTATED"
    CONTRADICTS = "CONTRADICTS"
    INSUFFICIENT = "INSUFFICIENT"
    FABRICATED = "FABRICATED"


class VerificationStatus(str, Enum):
    SUCCESS = "success"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LLM_UNAVAILABLE = "llm_unavailable"
    VERIFICATION_FAILED = "verification_failed"
    NOT_FOUND = "not_found"
    PROVIDER_ERROR = "provider_error"


class VerificationAnalyzeRequest(BaseModel):
    claim: str
    doi: str


class AgentEvidenceReference(BaseModel):
    chunk_id: str
    rationale: str | None = None


class ProsecutorAnalysis(BaseModel):
    agent: Literal["prosecutor"] = "prosecutor"
    analysis: str
    stance: str
    key_points: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    confidence: float

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class DefenderAnalysis(BaseModel):
    agent: Literal["defender"] = "defender"
    analysis: str
    stance: str
    key_points: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    confidence: float

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class AdjudicatorAnalysis(BaseModel):
    agent: Literal["adjudicator"] = "adjudicator"
    analysis: str
    verdict: Verdict
    confidence: float
    reasoning: str
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    suggested_correction: str | None = None

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class ClaimSegmentStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


class ClaimSegmentTrace(BaseModel):
    id: str
    text: str
    status: ClaimSegmentStatus
    coverage_score: float
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("coverage_score")
    @classmethod
    def clamp_coverage(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class ClaimTraceability(BaseModel):
    segments: list[ClaimSegmentTrace] = Field(default_factory=list)
    overall_coverage: float = 0.0
    warnings: list[str] = Field(default_factory=list)

    @field_validator("overall_coverage")
    @classmethod
    def clamp_overall_coverage(cls, value: float) -> float:
        return max(0.0, min(1.0, value))


class VerificationResponse(BaseModel):
    status: VerificationStatus
    claim: str
    verdict: Verdict | None = None
    confidence: float | None = None
    summary: str | None = None
    reasoning: str | None = None
    paper: EvidencePaperSummary
    evidence: list[EvidenceItem] = Field(default_factory=list)
    prosecutor: ProsecutorAnalysis | None = None
    defender: DefenderAnalysis | None = None
    adjudicator: AdjudicatorAnalysis | None = None
    suggested_correction: str | None = None
    agent_agreement: bool | None = None
    validation_warnings: list[str] | None = None
    claim_traceability: ClaimTraceability | None = None
    detail: str | None = None
