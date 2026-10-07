from pathlib import Path
from typing import Any


PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "auth_testing_prompt.txt"
)


def load_testing_prompt() -> str:
    """Load the testing-agent instructions."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_test_plan() -> list[dict[str, Any]]:
    """
    Generate the initial authentication test plan.

    This is the deterministic baseline used by the testing agent.
    The AI layer can later expand this plan with additional
    edge cases and security scenarios.
    """

    return [
        {
            "id": "TC-001",
            "name": "Successful user registration",
            "objective": "Verify a valid user can create an account.",
            "priority": "High",
            "category": "Functional",
        },
        {
            "id": "TC-002",
            "name": "Duplicate email registration",
            "objective": "Prevent registration with an existing email.",
            "priority": "High",
            "category": "Validation",
        },
        {
            "id": "TC-003",
            "name": "Duplicate username registration",
            "objective": "Prevent registration with an existing username.",
            "priority": "High",
            "category": "Validation",
        },
        {
            "id": "TC-004",
            "name": "Invalid email registration",
            "objective": "Reject incorrectly formatted email addresses.",
            "priority": "High",
            "category": "Validation",
        },
        {
            "id": "TC-005",
            "name": "Weak password rejection",
            "objective": "Reject passwords that do not satisfy the password policy.",
            "priority": "Critical",
            "category": "Security",
        },
        {
            "id": "TC-006",
            "name": "Password confirmation mismatch",
            "objective": "Reject registration when passwords do not match.",
            "priority": "High",
            "category": "Validation",
        },
        {
            "id": "TC-007",
            "name": "Successful login",
            "objective": "Verify valid credentials produce an access token.",
            "priority": "Critical",
            "category": "Functional",
        },
        {
            "id": "TC-008",
            "name": "Incorrect password",
            "objective": "Reject login with an incorrect password.",
            "priority": "Critical",
            "category": "Security",
        },
        {
            "id": "TC-009",
            "name": "Unknown email",
            "objective": "Reject login for an unregistered email address.",
            "priority": "High",
            "category": "Security",
        },
    ]


if __name__ == "__main__":
    prompt = load_testing_prompt()
    test_plan = generate_test_plan()

    print("=" * 60)
    print("NEXA/AUTH — AI TESTING AGENT")
    print("=" * 60)

    print("\nTesting prompt loaded:")
    print(f"{len(prompt)} characters")

    print(f"\nGenerated test cases: {len(test_plan)}")

    for test_case in test_plan:
        print(
            f"{test_case['id']} | "
            f"{test_case['priority']:<8} | "
            f"{test_case['name']}"
        )