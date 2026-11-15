from prompts import full_doc_prompt, reduce_prompt, chunk_prompt
from schemas import DocumentAnalysis
from pydantic import ValidationError
from typing_extensions import Any
from json import JSONDecodeError
from chunking import chunk_text
from llm import llm_request
import pymupdf
import json

# Text Extraction
def extract_text(pdf_bytes: bytes) -> str:
    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    ) as document:
        pages = [
            page.get_text()
            for page in document
        ]
        text = "\n".join(pages).strip()

        if not text:
            raise ValueError(
                "No extractable text found. "
                "This PDF may require OCR."
                "Or File may be Corrupted."
            )
        return text

# Parser
def parse_response(response: str, schema):
    if not response or not response.strip():
        raise ValueError("LLM returned an empty response")
    try:
        response = json.loads(response)
        return schema.model_validate(response)
    except JSONDecodeError as e:
        print(f"JSON Parsing Error: {e.msg}")
    except ValidationError as e:
        print(f"Schema Validation Error: {e}")
        raise


# Map-Reduce Summarization
def map_reduce_summarization(text: str) -> dict[str, Any]:
    chunks = chunk_text(text)

    map_results = []
    total_map_latency = 0
    total_input_tokens = 0
    total_output_tokens = 0

    # MAP PHASE
    for index, chunk in enumerate(chunks["chunks"]):

        result = llm_request(chunk, DocumentAnalysis, chunk_prompt)
        map_results.append(result["summary"])
        total_map_latency += result["total_latency"]

        if result["total_input_tokens"] is not None:
            total_input_tokens += result["total_input_tokens"]

        if result["total_output_tokens"] is not None:
            total_output_tokens += result["total_output_tokens"]

        print(f"Processed chunk {index + 1}/{len(chunks["chunks"])}")

    # REDUCE PHASE
    combined_summaries = "\n\n".join(map_results)

    reduce_result = llm_request(combined_summaries,DocumentAnalysis,reduce_prompt)

    return {
        "summary": reduce_result["summary"],
        "chunks_processed": len(chunks["chunks"]),
        "map_latency": total_map_latency,
        "reduce_latency": reduce_result["total_latency"],
        "request_count": len(chunks["chunks"]) + 1,
        "total_latency": (
                total_map_latency + reduce_result["total_latency"]
        ),
        "total_input_tokens": (
                total_input_tokens
                + (reduce_result["total_input_tokens"] or 0)
        ),
        "total_output_tokens": (
                total_output_tokens
                + (reduce_result["total_output_tokens"] or 0)
        ),
    }

# Full Document Request
def full_document_summarization(text: str) -> dict[str, Any] | None:
    return llm_request(text, DocumentAnalysis, full_doc_prompt)
