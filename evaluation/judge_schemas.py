from pydantic import BaseModel, Field
from typing import Literal

class QualityScores(BaseModel):
    faithfulness: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    entity_accuracy: int = Field(ge=1, le=5)
    relevance: int = Field(ge=1, le=5)
    conciseness: int = Field(ge=1, le=5)


class Finding(BaseModel):
    issue_type: Literal[
        "unsupported_claim",
        "missing_information",
        "entity_error",
        "irrelevant_information",
        "repetition"
    ]

    severity: Literal["low", "medium", "high"]

    summary_excerpt: str
    source_evidence: str
    explanation: str


class QualityEvaluation(BaseModel):
    scores: QualityScores

    overall_assessment: str

    strengths: list[str]

    weaknesses: list[str]

    findings: list[Finding]