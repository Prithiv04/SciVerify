from __future__ import annotations

from app.schemas.evidence import EvidenceItem
from app.schemas.verification import ProsecutorAnalysis
from app.services.agents.defender import _build_agent_prompt as _shared_prompt  # noqa: F401
from app.services.evidence_validation import (
    format_evidence_for_prompt,
    sanitize_prosecutor_analysis,
)
from app.services.llm.provider import LLMProvider, LLMResponseError

PROSECUTOR_SYSTEM_PROMPT = """You are the Prosecutor agent in a scientific claim verification system.
Your job is to challenge the claim using ONLY the supplied evidence chunks.
Do not invent papers, quotes, numbers, citations, or experimental results.
Reference evidence only by chunk_id from the supplied list.
Return JSON matching the requested schema exactly."""


def run_prosecutor(
    claim: str,
    evidence: list[EvidenceItem],
    llm: LLMProvider,
) -> ProsecutorAnalysis:
    prompt = _build_agent_prompt(
        role="Prosecutor",
        claim=claim,
        evidence=evidence,
        instructions=(
            "Attempt to disprove, weaken, or challenge the claim. Focus on contradictions, "
            "numeric mismatches, overstated conclusions, missing conditions, scope limitations, "
            "and methodological limitations."
        ),
    )
    result = llm.generate(
        prompt,
        system=PROSECUTOR_SYSTEM_PROMPT,
        response_model=ProsecutorAnalysis,
    )
    if not isinstance(result, ProsecutorAnalysis):
        raise LLMResponseError("Prosecutor returned unexpected response type.")

    valid_ids = {item.chunk_id for item in evidence}
    return sanitize_prosecutor_analysis(result, valid_ids)


def _build_agent_prompt(
    *,
    role: str,
    claim: str,
    evidence: list[EvidenceItem],
    instructions: str,
) -> str:
    return f"""
Role: {role}

Claim:
{claim}

Instructions:
{instructions}

Evidence chunks (use only these chunk_id values):
{format_evidence_for_prompt(evidence)}

Return JSON with fields:
- agent
- analysis
- stance
- key_points
- supporting_evidence (array of chunk_id strings)
- contradicting_evidence (array of chunk_id strings)
- confidence (number between 0 and 1)
""".strip()
