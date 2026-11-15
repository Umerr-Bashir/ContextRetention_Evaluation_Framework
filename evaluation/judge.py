import json

from evaluation import judge_schemas
from llm import llm_request
from evaluation.judge_schemas import QualityEvaluation
from evaluation.metrics import (
    calculate_cost,
    validate_summary
)

def parse_json_response(response_text: str) -> dict:
    parsed = json.loads(response_text)

    # Handle JSON encoded inside another JSON string.
    if isinstance(parsed, str):
        parsed = json.loads(parsed)

    if not isinstance(parsed, dict):
        raise ValueError("Judge response must be a JSON object.")

    return parsed

def evaluate_summary(document_text: str, generated_summary: str, approach_name: str) -> dict:
    prompt = f"""
    You are an independent AI evaluation judge.

    Your task is to evaluate a generated document summary
    against the original source document.

    Do not evaluate writing style alone.
    Prioritize factual correctness and information preservation.

    EVALUATION RUBRIC:

    1. Faithfulness (1-5)
    Are the claims in the summary supported by the source?
    Penalize invented facts, unsupported claims and distortions.

    2. Completeness (1-5)
    Does the summary preserve the most important concepts,
    facts, figures, conclusions and topics?
    Do not penalize reasonable summarization of minor details.

    3. Entity accuracy (1-5)
    Are people, organizations, laws, dates, numbers and
    technical terms represented correctly?

    4. Relevance (1-5)
    Does the summary accurately represent the actual document?
    Penalize unrelated or misleading information.

    5. Conciseness (1-5)
    Does the summary communicate important information
    without unnecessary repetition or irrelevant detail?

    IMPORTANT RULES:

    - Use the original document as the source of truth.
    - Never assume a claim is correct just because it sounds plausible.
    - Do not reward a summary for including more information
      if that information is unsupported.
    - Do not penalize a summary for omitting minor details.
    - Identify important missing information.
    - Provide specific evidence for every finding.
    - Do not invent source quotations.
    - If you cannot find evidence, explicitly say so.
    - Be strict and consistent.
    - Return only the requested JSON structure.
    """
    text_attachments = f"""
    APPROACH:
    {approach_name}

    ORIGINAL DOCUMENT:
    {document_text}

    GENERATED SUMMARY:
    {generated_summary}
    """

    result = llm_request(text_attachments ,QualityEvaluation ,prompt)

    parsed = parse_json_response(result["summary"])

    evaluation = QualityEvaluation.model_validate(parsed)

    return {
        "approach": approach_name,
        "scores": evaluation.scores.model_dump(),
        "overall_assessment": evaluation.overall_assessment,
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "findings": [
            finding.model_dump()
            for finding in evaluation.findings
        ],
        "judge_latency": result["total_latency"],
        "judge_input_tokens": result["total_input_tokens"],
        "judge_output_tokens": result["total_output_tokens"],
        "estimated_cost_usd": round(calculate_cost(result["total_input_tokens"], result["total_output_tokens"]), 8),
    }