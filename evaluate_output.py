import json
import sys
from pathlib import Path
from typing import Any, Callable


OUTPUT_FILE = Path("workflow_output.json")


def normalized_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).lower()


def has_required_top_level_keys(data: dict[str, Any]) -> bool:
    required = {
        "workflow_name",
        "assay_name",
        "sample_types",
        "steps",
        "final_result_options",
        "assumptions",
        "source_gaps",
    }
    return required.issubset(data)


def has_sequential_steps(data: dict[str, Any]) -> bool:
    steps = data.get("steps", [])
    sequences = [step.get("sequence") for step in steps]
    return bool(steps) and sequences == list(range(1, len(steps) + 1))


def every_step_has_fields_and_criteria(data: dict[str, Any]) -> bool:
    return all(
        step.get("name")
        and step.get("performer_role")
        and isinstance(step.get("fields"), list)
        and isinstance(step.get("acceptance_criteria"), list)
        and step.get("acceptance_criteria")
        for step in data.get("steps", [])
    )


def captures_sample_identity(data: dict[str, Any]) -> bool:
    return "sample id" in normalized_text(data.get("steps", []))


def captures_control_review(data: dict[str, Any]) -> bool:
    text = normalized_text(data.get("steps", []))
    return "positive control" in text and "negative control" in text


def captures_expected_results(data: dict[str, Any]) -> bool:
    results = {str(item).lower() for item in data.get("final_result_options", [])}
    return {"detected", "not detected", "inconclusive"}.issubset(results)


def requires_human_review(data: dict[str, Any]) -> bool:
    return any(step.get("requires_human_review") is True for step in data.get("steps", []))


def documents_source_gaps(data: dict[str, Any]) -> bool:
    gaps = data.get("source_gaps", [])
    return isinstance(gaps, list) and len(gaps) >= 5


def main() -> None:
    if not OUTPUT_FILE.exists():
        print(f"ERROR: {OUTPUT_FILE} was not found.")
        sys.exit(2)

    try:
        data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Output is not valid JSON: {exc}")
        sys.exit(2)

    checks: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
        ("Required top-level sections", has_required_top_level_keys),
        ("Sequential workflow steps", has_sequential_steps),
        ("Step fields and acceptance criteria", every_step_has_fields_and_criteria),
        ("Sample identity captured", captures_sample_identity),
        ("Positive and negative controls captured", captures_control_review),
        ("Expected final-result choices", captures_expected_results),
        ("Human review required", requires_human_review),
        ("At least five source gaps documented", documents_source_gaps),
    ]

    passed = 0
    print("AI Laboratory Workflow Evaluation")
    print("=" * 38)

    for label, check in checks:
        try:
            result = check(data)
        except (AttributeError, TypeError):
            result = False

        print(f"{'PASS' if result else 'FAIL'}  {label}")
        passed += int(result)

    total = len(checks)
    score = passed / total
    print("-" * 38)
    print(f"Score: {passed}/{total} ({score:.0%})")

    if passed != total:
        print("Evaluation failed. Review the FAIL items before human approval.")
        sys.exit(1)

    print("Evaluation passed. Human review is still required before use.")


if __name__ == "__main__":
    main()
