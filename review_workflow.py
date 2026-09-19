import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKFLOW_FILE = Path("workflow_output.json")
REVIEW_FILE = Path("review_record.json")
ALLOWED_DECISIONS = {
    "1": "approved_for_configuration_draft",
    "2": "revision_required",
    "3": "rejected",
}


def load_workflow() -> tuple[dict[str, Any], bytes]:
    if not WORKFLOW_FILE.exists():
        print(f"BLOCKED: {WORKFLOW_FILE} was not found.")
        sys.exit(2)

    raw = WORKFLOW_FILE.read_bytes()
    try:
        workflow = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"BLOCKED: Workflow output is not valid JSON: {exc}")
        sys.exit(2)

    required = {"workflow_name", "steps", "source_gaps", "final_result_options"}
    if not required.issubset(workflow):
        print("BLOCKED: Workflow output is missing required sections.")
        sys.exit(2)

    if not workflow["steps"]:
        print("BLOCKED: Workflow has no steps to review.")
        sys.exit(2)

    return workflow, raw


def required_input(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field is required.")


def choose_decision() -> str:
    print("\nReview decision:")
    print("  1 - Approve as a configuration draft only")
    print("  2 - Revision required")
    print("  3 - Reject")

    while True:
        choice = input("Select 1, 2, or 3: ").strip()
        if choice in ALLOWED_DECISIONS:
            return ALLOWED_DECISIONS[choice]
        print("Invalid selection. Enter 1, 2, or 3.")


def main() -> None:
    workflow, raw = load_workflow()
    workflow_hash = hashlib.sha256(raw).hexdigest()

    print("AI Laboratory Workflow — Human Review Gate")
    print("=" * 45)
    print(f"Workflow: {workflow['workflow_name']}")
    print(f"Steps: {len(workflow['steps'])}")
    print(f"Source gaps requiring review: {len(workflow['source_gaps'])}")
    print("\nIMPORTANT:")
    print("- This is a fictional software-training workflow.")
    print("- Approval applies only to the configuration draft.")
    print("- It does not authorize laboratory testing or result reporting.")

    if workflow["source_gaps"]:
        print("\nOpen source gaps:")
        for index, gap in enumerate(workflow["source_gaps"], start=1):
            print(f"  {index}. {gap}")

    print("\nReviewer information")
    reviewer_name = required_input("Reviewer name: ")
    reviewer_role = required_input("Reviewer role: ")
    decision = choose_decision()
    comments = required_input("Review comments: ")

    confirmation = input(
        "\nType REVIEWED to confirm this decision and create the audit record: "
    ).strip()
    if confirmation != "REVIEWED":
        print("BLOCKED: Confirmation did not match. No review record was created.")
        sys.exit(1)

    record = {
        "workflow_file": WORKFLOW_FILE.name,
        "workflow_sha256": workflow_hash,
        "workflow_name": workflow["workflow_name"],
        "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        "reviewer_name": reviewer_name,
        "reviewer_role": reviewer_role,
        "decision": decision,
        "comments": comments,
        "source_gap_count": len(workflow["source_gaps"]),
        "authorization_scope": "software configuration draft only",
        "laboratory_use_authorized": False,
    }

    REVIEW_FILE.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"\nCreated {REVIEW_FILE.resolve()}")
    print(f"Decision: {decision}")
    print("Laboratory use authorized: False")


if __name__ == "__main__":
    main()
