import json
import sys
from pathlib import Path
from typing import Any


RESULTS_FILE = Path("retrieval_results.json")
REQUIRED_DOCUMENT_PREFIXES = {
    "DOC-001": "Sample receipt requirements",
    "DOC-002": "Molecular control requirements",
    "DOC-003": "Result review and approval requirements",
}


def matches_prefix(document_id: str, prefix: str) -> bool:
    return document_id.upper().startswith(prefix)


def main() -> None:
    if not RESULTS_FILE.exists():
        print(f"ERROR: {RESULTS_FILE} was not found. Run python app.py first.")
        sys.exit(2)

    try:
        results: list[dict[str, Any]] = json.loads(
            RESULTS_FILE.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        print(f"ERROR: Retrieval audit is not valid JSON: {exc}")
        sys.exit(2)

    selected_ids = [str(item.get("document_id", "")) for item in results]
    similarities = [item.get("similarity") for item in results]
    checks: list[tuple[str, bool]] = [
        ("Three or four documents retrieved", 3 <= len(results) <= 4),
        (
            "Ranks are sequential",
            [item.get("rank") for item in results]
            == list(range(1, len(results) + 1)),
        ),
        (
            "Similarity scores are descending",
            all(isinstance(score, (int, float)) for score in similarities)
            and similarities[:3] == sorted(similarities[:3], reverse=True),
        ),
    ]

    for prefix, label in REQUIRED_DOCUMENT_PREFIXES.items():
        found = any(matches_prefix(document_id, prefix) for document_id in selected_ids)
        checks.append((f"{label} ({prefix})", found))

    print("Retrieval Evaluation")
    print("=" * 38)
    passed = 0
    for label, result in checks:
        print(f"{'PASS' if result else 'FAIL'}  {label}")
        passed += int(result)

    total = len(checks)
    print("-" * 38)
    print(f"Score: {passed}/{total} ({passed / total:.0%})")
    print(f"Selected: {', '.join(selected_ids)}")

    if passed != total:
        print("Retrieval evaluation failed. Do not treat the evidence set as complete.")
        sys.exit(1)

    print("Retrieval evaluation passed.")


if __name__ == "__main__":
    main()
