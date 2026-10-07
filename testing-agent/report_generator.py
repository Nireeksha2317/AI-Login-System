from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

JSON_REPORT_PATH = REPORTS_DIR / "latest_report.json"
HTML_REPORT_PATH = REPORTS_DIR / "latest_report.html"


# =========================================================
# HELPERS
# =========================================================

def utc_timestamp() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def calculate_ai_execution_summary(
    ai_execution_results: list[dict[str, Any]],
) -> dict[str, int]:

    passed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "PASSED"
    )

    failed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "FAILED"
    )

    errors = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "ERROR"
    )

    not_executed = sum(
        1
        for result in ai_execution_results
        if result.get("status") == "NOT_EXECUTED"
    )

    total = len(ai_execution_results)

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "not_executed": not_executed,
    }


def determine_final_status(
    baseline_report: dict[str, Any],
    ai_execution_summary: dict[str, int],
    coverage_gaps: list[dict[str, Any]],
    unmapped_scenarios: list[dict[str, Any]],
) -> str:

    baseline_failed = baseline_report.get("failed", 0)

    ai_failed = ai_execution_summary.get("failed", 0)
    ai_errors = ai_execution_summary.get("errors", 0)

    if baseline_failed > 0 or ai_failed > 0 or ai_errors > 0:
        return "TESTING REQUIRES ATTENTION"

    if coverage_gaps or unmapped_scenarios:
        return "PASS WITH SECURITY/COVERAGE RECOMMENDATIONS"

    return "TESTING PASSED"


def build_recommendations(
    coverage_gaps: list[dict[str, Any]],
    unmapped_scenarios: list[dict[str, Any]],
) -> list[str]:

    recommendations: list[str] = []

    if coverage_gaps:
        recommendations.append(
            f"Review {len(coverage_gaps)} AI-identified "
            "coverage/security gap(s) requiring additional "
            "application functionality or testing support."
        )

    if unmapped_scenarios:
        recommendations.append(
            f"Create approved test templates for "
            f"{len(unmapped_scenarios)} currently unmapped "
            "AI-generated scenario(s)."
        )

    if not coverage_gaps and not unmapped_scenarios:
        recommendations.append(
            "Current API functionality is covered by the "
            "available automated testing scenarios."
        )

    recommendations.append(
        "Continue expanding edge-case, authentication, "
        "authorization, and security testing as the "
        "application evolves."
    )

    return recommendations


# =========================================================
# BUILD REPORT
# =========================================================

def build_report(
    baseline_scenarios: list[dict[str, Any]],
    baseline_report: dict[str, Any],
    ai_scenarios: list[dict[str, Any]],
    executable_scenarios: list[dict[str, Any]],
    coverage_gaps: list[dict[str, Any]],
    unmapped_scenarios: list[dict[str, Any]],
    ai_execution_results: list[dict[str, Any]],
    ai_analysis: str,
    provider: str,
    model: str,
) -> dict[str, Any]:

    ai_execution_summary = calculate_ai_execution_summary(
        ai_execution_results
    )

    final_status = determine_final_status(
        baseline_report=baseline_report,
        ai_execution_summary=ai_execution_summary,
        coverage_gaps=coverage_gaps,
        unmapped_scenarios=unmapped_scenarios,
    )

    recommendations = build_recommendations(
        coverage_gaps=coverage_gaps,
        unmapped_scenarios=unmapped_scenarios,
    )

    return {
        "report_metadata": {
            "project": "NEXA/AUTH",
            "report_type": "AI-Assisted Authentication Testing Report",
            "generated_at": utc_timestamp(),
            "ai_provider": provider,
            "ai_model": model,
        },

        "executive_summary": {
            "final_status": final_status,
            "summary": (
                "Automated baseline testing and AI-assisted "
                "security/coverage analysis were completed."
            ),
        },

        "test_summary": {
            "baseline_scenarios": len(baseline_scenarios),
            "baseline_total": baseline_report.get("total", 0),
            "baseline_passed": baseline_report.get("passed", 0),
            "baseline_failed": baseline_report.get("failed", 0),

            "ai_scenarios_generated": len(ai_scenarios),
            "ai_executable": len(executable_scenarios),
            "coverage_gaps": len(coverage_gaps),
            "unmapped_scenarios": len(unmapped_scenarios),

            "ai_total_executed": ai_execution_summary["total"],
            "ai_passed": ai_execution_summary["passed"],
            "ai_failed": ai_execution_summary["failed"],
            "ai_errors": ai_execution_summary["errors"],
            "ai_not_executed": ai_execution_summary["not_executed"],
        },

        "ai_analysis": {
            "provider": provider,
            "model": model,
            "analysis": ai_analysis,
        },

        "baseline_results": {
            "status": baseline_report.get("status"),
            "total": baseline_report.get("total", 0),
            "passed": baseline_report.get("passed", 0),
            "failed": baseline_report.get("failed", 0),
            "return_code": baseline_report.get("return_code"),
            "recommendation": baseline_report.get(
                "recommendation",
                "",
            ),
        },

        "ai_execution": {
            "summary": ai_execution_summary,
            "results": ai_execution_results,
        },

        "approved_ai_scenarios": executable_scenarios,

        "coverage_gaps": coverage_gaps,

        "unmapped_scenarios": unmapped_scenarios,

        "recommendations": recommendations,
    }


# =========================================================
# SAVE JSON REPORT
# =========================================================

def save_json_report(
    report: dict[str, Any],
) -> Path:

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return JSON_REPORT_PATH


# =========================================================
# HTML HELPERS
# =========================================================

def escape_html(value: Any) -> str:
    return html.escape(str(value))


def status_class(status: str) -> str:

    normalized = status.upper().replace(" ", "-")

    if normalized in {
        "PASSED",
        "TESTING-PASSED",
    }:
        return "status-passed"

    if normalized in {
        "FAILED",
        "ERROR",
        "TESTING-REQUIRES-ATTENTION",
    }:
        return "status-failed"

    return "status-warning"


def render_execution_rows(
    results: list[dict[str, Any]],
) -> str:

    if not results:
        return """
        <tr>
            <td colspan="5" class="empty">
                No AI execution results available.
            </td>
        </tr>
        """

    rows = []

    for index, result in enumerate(results, start=1):

        status = result.get(
            "status",
            "UNKNOWN",
        )

        rows.append(
            f"""
            <tr>
                <td>{index}</td>
                <td>{escape_html(result.get("name", "Unknown"))}</td>
                <td>
                    <span class="badge {status_class(status)}">
                        {escape_html(status)}
                    </span>
                </td>
                <td>
                    {escape_html(
                        result.get("actual_status", "-")
                    )}
                </td>
                <td>
                    {escape_html(
                        result.get("reason", "-")
                    )}
                </td>
            </tr>
            """
        )

    return "\n".join(rows)


def render_coverage_rows(
    scenarios: list[dict[str, Any]],
) -> str:

    if not scenarios:
        return """
        <tr>
            <td colspan="4" class="empty">
                No coverage gaps identified.
            </td>
        </tr>
        """

    rows = []

    for index, scenario in enumerate(
        scenarios,
        start=1,
    ):

        rows.append(
            f"""
            <tr>
                <td>{index}</td>
                <td>{escape_html(
                    scenario.get("name", "Unknown")
                )}</td>
                <td>{escape_html(
                    scenario.get("priority", "-")
                )}</td>
                <td>{escape_html(
                    scenario.get(
                        "reason",
                        "Required functionality is unavailable.",
                    )
                )}</td>
            </tr>
            """
        )

    return "\n".join(rows)


def render_unmapped_rows(
    scenarios: list[dict[str, Any]],
) -> str:

    if not scenarios:
        return """
        <tr>
            <td colspan="3" class="empty">
                No unmapped scenarios.
            </td>
        </tr>
        """

    rows = []

    for index, scenario in enumerate(
        scenarios,
        start=1,
    ):

        rows.append(
            f"""
            <tr>
                <td>{index}</td>
                <td>{escape_html(
                    scenario.get("name", "Unknown")
                )}</td>
                <td>{escape_html(
                    scenario.get("objective", "-")
                )}</td>
            </tr>
            """
        )

    return "\n".join(rows)


def render_recommendations(
    recommendations: list[str],
) -> str:

    if not recommendations:
        return "<li>No additional recommendations.</li>"

    return "\n".join(
        f"<li>{escape_html(item)}</li>"
        for item in recommendations
    )


# =========================================================
# SAVE HTML REPORT
# =========================================================

def save_html_report(
    report: dict[str, Any],
) -> Path:

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata = report["report_metadata"]
    summary = report["test_summary"]
    executive = report["executive_summary"]
    ai_execution = report["ai_execution"]
    recommendations = report["recommendations"]

    final_status = executive["final_status"]

    html_content = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
    NEXA/AUTH — AI Testing Report
</title>

<style>

:root {{
    --ivory: #f4f1ea;
    --black: #171717;
    --orange: #d4512c;
    --muted: #706d66;
    --border: #d8d3c8;
    --white: #fffdf8;
    --green: #287a4d;
    --red: #a33a2b;
    --yellow: #9a6a00;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: var(--ivory);
    color: var(--black);
    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}}

.container {{
    width: min(1180px, 92%);
    margin: 0 auto;
    padding: 48px 0 80px;
}}

.header {{
    border-bottom: 2px solid var(--black);
    padding-bottom: 28px;
    margin-bottom: 36px;
}}

.eyebrow {{
    color: var(--orange);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}}

h1 {{
    font-size: clamp(36px, 6vw, 68px);
    line-height: 0.95;
    margin: 12px 0;
    letter-spacing: -0.05em;
}}

.subtitle {{
    color: var(--muted);
    font-size: 16px;
}}

.meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px 28px;
    margin-top: 20px;
    color: var(--muted);
    font-size: 13px;
}}

.status-card {{
    background: var(--black);
    color: var(--white);
    padding: 28px;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}}

.status-label {{
    color: #aaa59b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}}

.status {{
    margin-top: 8px;
    font-size: clamp(22px, 4vw, 38px);
    font-weight: 800;
    letter-spacing: -0.03em;
}}

.status-accent {{
    width: 70px;
    height: 70px;
    border: 2px solid var(--orange);
    display: grid;
    place-items: center;
    color: var(--orange);
    font-weight: 900;
    font-size: 24px;
}}

.metrics {{
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    margin-bottom: 42px;
}}

.metric {{
    background: var(--white);
    padding: 24px;
}}

.metric-label {{
    color: var(--muted);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}

.metric-value {{
    font-size: 34px;
    font-weight: 800;
    margin-top: 8px;
}}

section {{
    margin-top: 48px;
}}

h2 {{
    font-size: 25px;
    letter-spacing: -0.03em;
    margin-bottom: 18px;
}}

.panel {{
    background: var(--white);
    border: 1px solid var(--border);
    padding: 24px;
}}

.insight {{
    font-size: 15px;
    line-height: 1.75;
    white-space: pre-wrap;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th {{
    background: var(--black);
    color: var(--white);
    text-align: left;
    padding: 12px;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

td {{
    border-bottom: 1px solid var(--border);
    padding: 13px 12px;
    vertical-align: top;
    line-height: 1.5;
}}

tr:last-child td {{
    border-bottom: none;
}}

.badge {{
    display: inline-block;
    padding: 5px 9px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.06em;
}}

.status-passed {{
    color: var(--green);
    border: 1px solid var(--green);
}}

.status-failed {{
    color: var(--red);
    border: 1px solid var(--red);
}}

.status-warning {{
    color: var(--yellow);
    border: 1px solid var(--yellow);
}}

.empty {{
    color: var(--muted);
    text-align: center;
    padding: 28px;
}}

ul {{
    margin: 0;
    padding-left: 20px;
}}

li {{
    margin-bottom: 10px;
    line-height: 1.6;
}}

.footer {{
    border-top: 1px solid var(--border);
    margin-top: 60px;
    padding-top: 20px;
    color: var(--muted);
    font-size: 12px;
}}

@media (max-width: 800px) {{

    .metrics {{
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }}

    .panel {{
        overflow-x: auto;
    }}

}}

@media (max-width: 520px) {{

    .metrics {{
        grid-template-columns: 1fr;
    }}

}}

</style>

</head>

<body>

<div class="container">

    <header class="header">

        <div class="eyebrow">
            AI-Assisted Security Testing
        </div>

        <h1>NEXA/AUTH</h1>

        <div class="subtitle">
            Professional Authentication Testing Report
        </div>

        <div class="meta">

            <span>
                Generated:
                {escape_html(metadata["generated_at"])}
            </span>

            <span>
                Provider:
                {escape_html(metadata["ai_provider"])}
            </span>

            <span>
                Model:
                {escape_html(metadata["ai_model"])}
            </span>

        </div>

    </header>


    <div class="status-card">

        <div>

            <div class="status-label">
                Final Testing Status
            </div>

            <div class="status">
                {escape_html(final_status)}
            </div>

        </div>

        <div class="status-accent">
            AI
        </div>

    </div>


    <div class="metrics">

        <div class="metric">

            <div class="metric-label">
                Baseline
            </div>

            <div class="metric-value">
                {summary["baseline_passed"]}/
                {summary["baseline_total"]}
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                AI Tests
            </div>

            <div class="metric-value">
                {summary["ai_passed"]}/
                {summary["ai_total_executed"]}
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Coverage Gaps
            </div>

            <div class="metric-value">
                {summary["coverage_gaps"]}
            </div>

        </div>


        <div class="metric">

            <div class="metric-label">
                Unmapped
            </div>

            <div class="metric-value">
                {summary["unmapped_scenarios"]}
            </div>

        </div>

    </div>


    <section>

        <h2>Executive Summary</h2>

        <div class="panel">

            <p class="insight">
                {escape_html(
                    executive["summary"]
                )}
            </p>

        </div>

    </section>


    <section>

        <h2>AI Testing Analysis</h2>

        <div class="panel">

            <div class="insight">
                {escape_html(
                    report["ai_analysis"]["analysis"]
                )}
            </div>

        </div>

    </section>


    <section>

        <h2>AI Test Execution</h2>

        <div class="panel">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>Scenario</th>
                        <th>Status</th>
                        <th>HTTP</th>
                        <th>Reason</th>
                    </tr>

                </thead>

                <tbody>

                    {render_execution_rows(
                        ai_execution["results"]
                    )}

                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Coverage Gaps</h2>

        <div class="panel">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>Scenario</th>
                        <th>Priority</th>
                        <th>Reason</th>
                    </tr>

                </thead>

                <tbody>

                    {render_coverage_rows(
                        report["coverage_gaps"]
                    )}

                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Unmapped AI Scenarios</h2>

        <div class="panel">

            <table>

                <thead>

                    <tr>
                        <th>#</th>
                        <th>Scenario</th>
                        <th>Objective</th>
                    </tr>

                </thead>

                <tbody>

                    {render_unmapped_rows(
                        report["unmapped_scenarios"]
                    )}

                </tbody>

            </table>

        </div>

    </section>


    <section>

        <h2>Recommendations</h2>

        <div class="panel">

            <ul>

                {render_recommendations(
                    recommendations
                )}

            </ul>

        </div>

    </section>


    <footer class="footer">

        NEXA/AUTH — AI-Assisted Authentication Testing<br>
        Generated automatically by the NEXA/AUTH testing agent.

    </footer>

</div>

</body>

</html>
"""

    HTML_REPORT_PATH.write_text(
        html_content,
        encoding="utf-8",
    )

    return HTML_REPORT_PATH


# =========================================================
# MAIN REPORT GENERATOR
# =========================================================

def generate_report(
    baseline_scenarios: list[dict[str, Any]],
    baseline_report: dict[str, Any],
    ai_scenarios: list[dict[str, Any]],
    executable_scenarios: list[dict[str, Any]],
    coverage_gaps: list[dict[str, Any]],
    unmapped_scenarios: list[dict[str, Any]],
    ai_execution_results: list[dict[str, Any]],
    ai_analysis: str,
    provider: str = "Google Gemini",
    model: str = "Unknown",
) -> dict[str, str]:

    print("\nBuilding structured testing report...")

    report = build_report(
        baseline_scenarios=baseline_scenarios,
        baseline_report=baseline_report,
        ai_scenarios=ai_scenarios,
        executable_scenarios=executable_scenarios,
        coverage_gaps=coverage_gaps,
        unmapped_scenarios=unmapped_scenarios,
        ai_execution_results=ai_execution_results,
        ai_analysis=ai_analysis,
        provider=provider,
        model=model,
    )

    json_path = save_json_report(
        report
    )

    html_path = save_html_report(
        report
    )

    return {
        "json": str(json_path),
        "html": str(html_path),
    }


# =========================================================
# DIRECT EXECUTION CHECK
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("NEXA/AUTH — PROFESSIONAL REPORT GENERATOR")
    print("=" * 70)

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"\nReports directory:\n{REPORTS_DIR}"
    )

    print(
        "\nThe report generator is ready to receive "
        "AI testing results."
    )