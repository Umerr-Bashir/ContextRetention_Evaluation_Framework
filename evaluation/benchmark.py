from datetime import datetime, timezone
from schemas import DocumentAnalysis
from analyzer import (
    full_document_summarization,
    map_reduce_summarization
)
from evaluation.metrics import (
    calculate_cost,
    validate_summary
)
from time import perf_counter
import json
import csv
import os


def evaluate_approach(name, analysis_function, document_text):

    start = perf_counter()
    result = analysis_function(document_text)

    # Actual elapsed time for the complete operation.
    wall_latency = perf_counter() - start
    summary = json.dumps(result["summary"])
    validation = validate_summary(summary, DocumentAnalysis)

    input_tokens = result["total_input_tokens"]
    output_tokens = result["total_output_tokens"]

    return {
        "approach": name,
        "wall_latency_seconds": round(wall_latency, 3),
        "reported_request_latency_seconds": result.get(
            "total_latency", 0
        ),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": round(
            calculate_cost(input_tokens, output_tokens), 8
        ),
        "request_count": result.get("request_count", 1),
        "chunks_processed": result.get("chunks_processed", 1),
        "json_valid": validation["json_valid"],
        "schema_valid": validation["schema_valid"],
        "validation_error": validation["error"],
        "summary_characters": len(summary),
        "summary": summary
    }


def run_benchmark(document_text: str):

    print("Starting full-document benchmark...")
    full_result = evaluate_approach(
        "Full Document",
        full_document_summarization,
        document_text
    )

    print("Starting Map-Reduce benchmark...")
    map_reduce_result = evaluate_approach(
        "Map-Reduce",
        map_reduce_summarization,
        document_text
    )

    results = [full_result, map_reduce_result]

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    os.makedirs("evaluation/results", exist_ok=True)

    # Save complete results, including generated summaries.
    json_path = f"evaluation/results/benchmark_{timestamp}.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    # Save comparable metrics in CSV.
    csv_path = f"evaluation/results/benchmark_{timestamp}.csv"

    fields = [
        "approach",
        "wall_latency_seconds",
        "reported_request_latency_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost_usd",
        "request_count",
        "chunks_processed",
        "json_valid",
        "schema_valid",
        "summary_characters"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        for result in results:
            writer.writerow({
                key: result[key] for key in fields
            })

    print("\nBenchmark completed.")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")

    return results