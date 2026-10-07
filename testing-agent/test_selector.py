from typing import Any

from test_templates import find_template


def normalize_name(name: str) -> str:
    """Normalize a scenario name for comparison."""
    return (
        name.lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
    )


def is_duplicate_scenario(
    scenario: dict[str, Any],
    baseline_tests: list[dict[str, Any]],
) -> bool:
    """
    Prevent the AI from executing a scenario that is already
    covered by the baseline test suite.
    """
    scenario_name = normalize_name(
        scenario.get("name", "")
    )

    for baseline in baseline_tests:
        baseline_name = normalize_name(
            baseline.get("name", "")
        )

        if scenario_name == baseline_name:
            return True

    return False


def select_tests(
    ai_scenarios: list[dict[str, Any]],
    baseline_tests: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:

    executable = []
    coverage_gaps = []
    unmapped = []

    for scenario in ai_scenarios:

        # ------------------------------------------------------
        # 1. Skip scenarios already covered by baseline tests
        # ------------------------------------------------------

        if is_duplicate_scenario(
            scenario,
            baseline_tests,
        ):
            continue

        # ------------------------------------------------------
        # 2. Respect Gemini's coverage-gap classification
        # ------------------------------------------------------

        execution_status = (
            scenario.get(
                "execution_status",
                "",
            )
            .upper()
        )

        if execution_status == "COVERAGE_GAP":
            coverage_gaps.append(scenario)
            continue

        # ------------------------------------------------------
        # 3. Ask the actual template registry
        # ------------------------------------------------------

        scenario_name = scenario.get(
            "name",
            "",
        )

        template = find_template(
            scenario_name
        )

        # ------------------------------------------------------
        # 4. Only a real template means EXECUTABLE
        # ------------------------------------------------------

        if template is not None:
            executable.append(scenario)
        else:
            unmapped.append(scenario)

    return {
        "executable": executable,
        "coverage_gaps": coverage_gaps,
        "unmapped": unmapped,
    }