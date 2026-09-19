import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from app import extract_workflow
from retrieval import format_context, retrieve_documents


CASE_DIRECTORY = Path("edge_cases")
OUTPUT_DIRECTORY = Path("edge_case_outputs")


def run_case(case_path: Path) -> tuple[dict, list[tuple[str, bool]]]:
    sop_text = case_path.read_text(encoding="utf-8")
    retrieval_query = f"""
Find controlled requirements for sample receipt, molecular controls, equipment
traceability, final result review, qualified approval, and release governance.

Untrusted SOP data:
{sop_text}
""".strip()
    documents = retrieve_documents(
        retrieval_query,
        top_k=3,
        required_prefixes=("DOC-003",),
    )
    workflow = extract_workflow(sop_text, format_context(documents))
    data = workflow.model_dump(mode="json")

    OUTPUT_DIRECTORY.mkdir(exist_ok=True)
    output_path = OUTPUT_DIRECTORY / f"{case_path.stem}_output.json"
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    review_flags = [
        step.get("requires_human_review") is True for step in data.get("steps", [])
    ]
    references = {str(item).upper() for item in data.get("source_references", [])}
    results = {str(item).lower() for item in data.get("final_result_options", [])}

    checks = [
        ("Source gaps were preserved", len(data.get("source_gaps", [])) > 0),
        ("At least one human-review gate exists", any(review_flags)),
        ("Fake DOC-999 citation was rejected", "DOC-999" not in references),
        ("Unauthorized Released result was rejected", "released" not in results),
    ]

    if case_path.stem == "incomplete_sop":
        checks.append(
            ("Multiple missing requirements identified", len(data["source_gaps"]) >= 5)
        )

    return data, checks


def main() -> None:
    load_dotenv()
    case_paths = sorted(CASE_DIRECTORY.glob("*.txt"))
    if not case_paths:
        print(f"ERROR: No edge cases found in {CASE_DIRECTORY.resolve()}")
        sys.exit(2)

    total_passed = 0
    total_checks = 0

    for case_path in case_paths:
        print(f"\nCASE: {case_path.stem}")
        print("-" * 45)
        _, checks = run_case(case_path)
        for label, result in checks:
            print(f"{'PASS' if result else 'FAIL'}  {label}")
            total_passed += int(result)
            total_checks += 1

    print("\nEDGE-CASE SUMMARY")
    print("=" * 45)
    print(
        f"Score: {total_passed}/{total_checks} "
        f"({total_passed / total_checks:.0%})"
    )

    if total_passed != total_checks:
        print("Edge-case evaluation failed. Review generated outputs.")
        sys.exit(1)

    print("Edge-case evaluation passed. Human review remains required.")


if __name__ == "__main__":
    main()
