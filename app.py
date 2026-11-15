from pathlib import Path

from analyzer import extract_text
from evaluation.benchmark import run_benchmark
from evaluation.run_quality_evaluation import run_quality_evaluation


def main() -> None:
    file_bytes = Path("documents/Business Finance.pdf").read_bytes()
    text = extract_text(file_bytes)

    benchmark_results = run_benchmark(text)
    run_quality_evaluation(text, benchmark_results)


if __name__ == "__main__":
    main()
