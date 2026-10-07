from ai_engine import AIEngine
from api_spec import API_SPEC
from test_generator import generate_test_plan
from test_runner import run_tests
from result_analyzer import analyze_test_results, print_report
from test_selector import select_tests
from test_templates import execute_scenario
from report_generator import generate_report


# =========================================================
# AUTHENTICATION REQUIREMENTS
# =========================================================

AUTH_REQUIREMENTS = """
The authentication system must allow users to create accounts
using a unique username and email address.

Registration requires:

- Username with at least 3 characters
- Valid email address
- Password with at least 8 characters
- Password must contain a lowercase letter
- Password must contain an uppercase letter
- Password must contain a number
- Password must contain a special character
- Password and confirm password must match

Users must be able to log in using their registered email
and password.

Invalid credentials must be rejected.

Duplicate usernames and emails must be rejected.

Inactive accounts must not be allowed to log in.

The system uses JWT authentication and secure password hashing.
"""


# =========================================================
# MAIN TESTING AGENT
# =========================================================

def run_testing_agent():

    print("=" * 70)
    print("NEXA/AUTH — AI-ASSISTED TESTING AGENT")
    print("=" * 70)

    # =========================================================
    # STEP 1 — GENERATE BASELINE TEST PLAN
    # =========================================================

    print("\n[1/6] Generating baseline test plan...")

    baseline_tests = generate_test_plan()

    print(
        f"Baseline scenarios: {len(baseline_tests)}"
    )

    # =========================================================
    # STEP 2 — AI REQUIREMENTS ANALYSIS
    # =========================================================

    print("\n[2/6] Running AI requirements analysis...")

    ai_engine = AIEngine()

    ai_result = ai_engine.analyze_requirements(
        AUTH_REQUIREMENTS,
        API_SPEC,
    )

    ai_scenarios = ai_result["additional_scenarios"]

    print(
        f"AI-generated scenarios: {len(ai_scenarios)}"
    )

    print("\nAI Testing Insights:")
    print("-" * 70)
    print(ai_result["analysis"])

    # =========================================================
    # STEP 3 — SELECT SAFE AI TEST SCENARIOS
    # =========================================================

    print("\n[3/6] Selecting executable AI scenarios...")

    selection_result = select_tests(
        ai_scenarios,
        baseline_tests,
    )

    executable_tests = selection_result["executable"]

    coverage_gaps = selection_result["coverage_gaps"]

    unmapped_tests = selection_result["unmapped"]

    print(
        f"Executable AI tests : {len(executable_tests)}"
    )

    print(
        f"Coverage gaps       : {len(coverage_gaps)}"
    )

    print(
        f"Unmapped scenarios  : {len(unmapped_tests)}"
    )

    # =========================================================
    # DISPLAY APPROVED EXECUTABLE SCENARIOS
    # =========================================================

    if executable_tests:

        print("\nApproved executable scenarios:")
        print("-" * 70)

        for index, test_case in enumerate(
            executable_tests,
            start=1,
        ):

            print(
                f"{index}. "
                f"{test_case['name']} "
                f"[{test_case.get('category', 'Unknown')}]"
            )

    # =========================================================
    # DISPLAY COVERAGE GAPS
    # =========================================================

    if coverage_gaps:

        print("\nCoverage gaps identified by AI:")
        print("-" * 70)

        for index, scenario in enumerate(
            coverage_gaps,
            start=1,
        ):

            print(
                f"{index}. {scenario['name']}"
            )

            print(
                "   Reason: "
                f"{scenario.get('reason', 'Required functionality is unavailable.')}"
            )

    # =========================================================
    # DISPLAY UNMAPPED SCENARIOS
    # =========================================================

    if unmapped_tests:

        print("\nUnmapped AI scenarios:")
        print("-" * 70)

        for index, scenario in enumerate(
            unmapped_tests,
            start=1,
        ):

            print(
                f"{index}. {scenario['name']}"
            )

    # =========================================================
    # STEP 4 — EXECUTE AI-SELECTED TESTS
    # =========================================================

    print(
        "\n[4/6] Executing approved AI test scenarios..."
    )

    print("-" * 70)

    ai_execution_results = []

    for index, scenario in enumerate(
        executable_tests,
        start=1,
    ):

        scenario_name = scenario.get(
            "name",
            "Unknown scenario",
        )

        print(
            f"\n[{index}/{len(executable_tests)}] "
            f"{scenario_name}"
        )

        result = execute_scenario(
            scenario
        )

        ai_execution_results.append(
            result
        )

        print(
            f"Status: "
            f"{result.get('status', 'UNKNOWN')}"
        )

        if result.get("actual_status") is not None:

            print(
                f"HTTP Status: "
                f"{result['actual_status']}"
            )

        if result.get("expected_status") is not None:

            print(
                f"Expected: "
                f"{result['expected_status']}"
            )

        if result.get("reason"):

            print(
                f"Reason: "
                f"{result['reason']}"
            )

    print(
        "\nAI scenario execution completed."
    )

    # =========================================================
    # AI EXECUTION SUMMARY
    # =========================================================

    ai_passed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "PASSED"
    )

    ai_failed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "FAILED"
    )

    ai_errors = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "ERROR"
    )

    ai_not_executed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "NOT_EXECUTED"
    )

    # =========================================================
    # STEP 5 — RUN BASELINE PYTEST SUITE
    # =========================================================

    print(
        "\n[5/6] Executing baseline pytest suite..."
    )

    test_result = run_tests()

    print(
        "\nAnalyzing baseline test results..."
    )

    report = analyze_test_results(
        test_result
    )

    print_report(
        report
    )

    # =========================================================
    # STEP 6 — FINAL TESTING SUMMARY
    # =========================================================

    print(
        "\n[6/6] Generating final AI testing summary..."
    )

    print("=" * 70)
    print("FINAL TESTING SUMMARY")
    print("=" * 70)

    # ---------------------------------------------------------
    # AI ANALYSIS
    # ---------------------------------------------------------

    print(
        f"\nBaseline scenarios    : "
        f"{len(baseline_tests)}"
    )

    print(
        f"AI scenarios          : "
        f"{len(ai_scenarios)}"
    )

    print(
        f"Executable AI         : "
        f"{len(executable_tests)}"
    )

    print(
        f"Coverage gaps         : "
        f"{len(coverage_gaps)}"
    )

    print(
        f"Unmapped scenarios    : "
        f"{len(unmapped_tests)}"
    )

    # ---------------------------------------------------------
    # AI EXECUTION RESULTS
    # ---------------------------------------------------------

    print(
        "\nAI EXECUTION RESULTS"
    )

    print("-" * 70)

    print(
        f"AI tests executed     : "
        f"{len(ai_execution_results)}"
    )

    print(
        f"AI tests passed       : "
        f"{ai_passed}"
    )

    print(
        f"AI tests failed       : "
        f"{ai_failed}"
    )

    print(
        f"AI execution errors   : "
        f"{ai_errors}"
    )

    print(
        f"AI not executed       : "
        f"{ai_not_executed}"
    )

    # ---------------------------------------------------------
    # BASELINE PYTEST RESULTS
    # ---------------------------------------------------------

    print(
        "\nBASELINE PYTEST RESULTS"
    )

    print("-" * 70)

    print(
        f"Tests executed        : "
        f"{report['total']}"
    )

    print(
        f"Tests passed          : "
        f"{report['passed']}"
    )

    print(
        f"Tests failed          : "
        f"{report['failed']}"
    )

    print(
        f"Overall status        : "
        f"{report['status']}"
    )

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    print(
        "\nAI RECOMMENDATION"
    )

    print("-" * 70)

    print(
        report["recommendation"]
    )

    # ---------------------------------------------------------
    # SECURITY / COVERAGE SUMMARY
    # ---------------------------------------------------------

    print(
        "\nSECURITY & COVERAGE SUMMARY"
    )

    print("-" * 70)

    if coverage_gaps:

        print(
            f"AI identified {len(coverage_gaps)} "
            "coverage/security gaps that require "
            "additional application functionality."
        )

    else:

        print(
            "No API coverage gaps were identified."
        )

    if unmapped_tests:

        print(
            f"{len(unmapped_tests)} AI scenarios "
            "remain unmapped to approved test templates."
        )

    else:

        print(
            "All AI scenarios are mapped to approved templates."
        )

    # =========================================================
    # FINAL STATUS
    # =========================================================

    print(
        "\nFINAL STATUS"
    )

    print("-" * 70)

    if (
        report["status"] == "PASSED"
        and ai_failed == 0
        and ai_errors == 0
    ):

        if coverage_gaps or unmapped_tests:

            print(
                "PASS WITH SECURITY/COVERAGE RECOMMENDATIONS"
            )

        else:

            print(
                "ALL TESTING PASSED"
            )

    else:

        print(
            "TESTING REQUIRES ATTENTION"
        )

    print(
        "\n" + "=" * 70
    )

    # =========================================================
    # STAGE 9 — GENERATE PROFESSIONAL TESTING REPORT
    # =========================================================

    print(
        "\nGenerating professional testing report..."
    )

    report_paths = generate_report(
        baseline_scenarios=baseline_tests,
        baseline_report=report,
        ai_scenarios=ai_scenarios,
        executable_scenarios=executable_tests,
        coverage_gaps=coverage_gaps,
        unmapped_scenarios=unmapped_tests,
        ai_execution_results=ai_execution_results,
        ai_analysis=ai_result.get("analysis", ""),
        provider=ai_result.get(
            "provider",
            "Google Gemini",
        ),
        model=ai_result.get(
            "model",
            "Unknown",
        ),
    )

    print(
        "\nProfessional testing report generated:"
    )

    print(
        f"JSON report : {report_paths['json']}"
    )

    print(
        f"HTML report : {report_paths['html']}"
    )

    # =========================================================
    # RETURN COMPLETE AGENT RESULT
    # =========================================================

    return {
        "report_paths": report_paths,

        "baseline_tests": baseline_tests,

        "ai_scenarios": ai_scenarios,

        "executable_tests": executable_tests,

        "coverage_gaps": coverage_gaps,

        "unmapped_tests": unmapped_tests,

        "ai_execution_results": ai_execution_results,

        "ai_passed": ai_passed,

        "ai_failed": ai_failed,

        "ai_errors": ai_errors,

        "ai_not_executed": ai_not_executed,

        "test_result": test_result,

        "report": report,
    }


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    run_testing_agent()