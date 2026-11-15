import csv
import json
from datetime import datetime, timezone

from evaluation.judge import evaluate_summary


def run_quality_evaluation(
    document_text: str,
    benchmark_results: list
):

    evaluations = []

    for result in benchmark_results:

        print(
            f"Evaluating {result['approach']}..."
        )

        evaluation = evaluate_summary(
            document_text=document_text,
            generated_summary=result["summary"],
            approach_name=result["approach"]
        )

        evaluations.append(evaluation)

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d_%H%M%S")

    output_path = (
        f"evaluation/results/quality_{timestamp}.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluations,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Save comparable metrics in CSV.
    csv_path = f"evaluation/results/quality_{timestamp}.csv"

    fields = [
        "approach",

        # Quality scores
        "faithfulness",
        "completeness",
        "entity_accuracy",
        "relevance",
        "conciseness",

        # Overall evaluation
        "overall_assessment",
        "strengths",
        "weaknesses",

        # Finding details
        "finding_count",
        "finding_issue_types",
        "finding_severities",
        "finding_summary_excerpts",
        "finding_source_evidence",
        "finding_explanations",

        # Judge performance metrics
        "judge_latency",
        "judge_input_tokens",
        "judge_output_tokens",
        "estimated_cost_usd"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        for result in evaluations:
            findings = result["findings"]

            writer.writerow({
                "approach": result["approach"],

                # Quality scores
                **result["scores"],

                # Overall evaluation
                "overall_assessment": result["overall_assessment"],
                "strengths": json.dumps(result["strengths"], ensure_ascii=False),
                "weaknesses": json.dumps(result["weaknesses"], ensure_ascii=False),

                # Finding details
                "finding_count": len(findings),

                "finding_issue_types": json.dumps(
                    [f["issue_type"] for f in findings],
                    ensure_ascii=False
                ),

                "finding_severities": json.dumps(
                    [f["severity"] for f in findings],
                    ensure_ascii=False
                ),

                "finding_summary_excerpts": json.dumps(
                    [f["summary_excerpt"] for f in findings],
                    ensure_ascii=False
                ),

                "finding_source_evidence": json.dumps(
                    [f["source_evidence"] for f in findings],
                    ensure_ascii=False
                ),

                "finding_explanations": json.dumps(
                    [f["explanation"] for f in findings],
                    ensure_ascii=False
                ),

                # Judge performance metrics
                "judge_latency": result["judge_latency"],
                "judge_input_tokens": result["judge_input_tokens"],
                "judge_output_tokens": result["judge_output_tokens"],
                "estimated_cost_usd": result["estimated_cost_usd"]
            })

    print("\nQuality Benchmark completed.")

    print(f"Quality evaluation saved (JSON): {output_path}")
    print(f"Quality evaluation saved (CSV): {csv_path}")

    return evaluations
