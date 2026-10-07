import re
from typing import Any


def analyze_test_results(test_result: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze pytest output and convert it into structured
    testing information.
    """

    stdout = test_result.get("stdout", "")
    stderr = test_result.get("stderr", "")
    return_code = test_result.get("return_code", 1)

    # Find the number of passed tests.
    passed_match = re.search(
        r"(\d+)\s+passed",
        stdout,
        re.IGNORECASE,
    )

    # Find the number of failed tests.
    failed_match = re.search(
        r"(\d+)\s+failed",
        stdout,
        re.IGNORECASE,
    )

    passed_count = (
        int(passed_match.group(1))
        if passed_match
        else 0
    )

    failed_count = (
        int(failed_match.group(1))
        if failed_match
        else 0
    )

    total_count = passed_count + failed_count

    if return_code == 0:
        status = "PASSED"
        recommendation = (
            "All automated tests passed. "
            "Continue with additional edge-case and security testing."
        )
    else:
        status = "FAILED"
        recommendation = (
            "One or more automated tests failed. "
            "Review the failing tests before deployment."
        )

    return {
        "status": status,
        "passed": passed_count,
        "failed": failed_count,
        "total": total_count,
        "return_code": return_code,
        "recommendation": recommendation,
        "stderr": stderr.strip(),
    }


def print_report(report: dict[str, Any]) -> None:
    """Display a human-readable testing report."""

    print("=" * 60)
    print("NEXA/AUTH — AUTOMATED TEST ANALYSIS")
    print("=" * 60)

    print(f"\nStatus       : {report['status']}")
    print(f"Total tests  : {report['total']}")
    print(f"Passed       : {report['passed']}")
    print(f"Failed       : {report['failed']}")
    print(f"Return code  : {report['return_code']}")

    print("\nRecommendation:")
    print(report["recommendation"])

    if report["stderr"]:
        print("\nWarnings / Errors:")
        print(report["stderr"])

    print("\n" + "=" * 60)


if __name__ == "__main__":
    sample_result = {
        "return_code": 0,
        "stdout": "......... [100%]\n9 passed in 0.56s",
        "stderr": "",
    }

    report = analyze_test_results(sample_result)
    print_report(report)