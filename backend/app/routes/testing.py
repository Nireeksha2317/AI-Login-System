from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/testing",
    tags=["AI Testing"],
)


# ============================================================================
# PATHS
# ============================================================================

# backend/
BACKEND_ROOT = Path(__file__).resolve().parents[2]

# AI-Login-System/
PROJECT_ROOT = BACKEND_ROOT.parent

# AI-Login-System/testing-agent/
TESTING_AGENT_DIR = PROJECT_ROOT / "testing-agent"

# testing-agent/agent.py
AGENT_FILE = TESTING_AGENT_DIR / "agent.py"

# testing-agent/reports/latest_report.json
REPORT_FILE = (
    TESTING_AGENT_DIR
    / "reports"
    / "latest_report.json"
)


# ============================================================================
# TEST LOCK
# ============================================================================

# Prevent multiple AI testing runs from being started
# at the same time.
_test_lock = threading.Lock()


# ============================================================================
# READ LATEST JSON REPORT
# ============================================================================

def read_latest_report() -> dict[str, Any]:
    """
    Read and return the latest generated JSON testing report.
    """

    if not REPORT_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "No testing report exists yet. "
                "Run the AI testing agent first."
            ),
        )

    try:
        return json.loads(
            REPORT_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "The latest testing report "
                "contains invalid JSON."
            ),
        ) from exc


# ============================================================================
# VALIDATE TESTING AGENT
# ============================================================================

def validate_testing_agent() -> None:
    """
    Verify that the testing-agent directory and
    agent.py file exist before attempting execution.
    """

    if not TESTING_AGENT_DIR.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "Testing agent directory "
                "was not found."
            ),
        )

    if not AGENT_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "testing-agent/agent.py "
                "was not found."
            ),
        )


# ============================================================================
# GET LATEST JSON REPORT
# ============================================================================

@router.get("/report")
def get_latest_testing_report():
    """
    Return the latest structured JSON testing report.
    """

    return read_latest_report()


# ============================================================================
# GET LATEST HTML REPORT
# ============================================================================

@router.get("/report/html")
def get_latest_testing_report_html():
    """
    Return the latest professional HTML testing report.
    """

    if not REPORT_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No testing report exists yet.",
        )

    html_report_file = (
        TESTING_AGENT_DIR
        / "reports"
        / "latest_report.html"
    )

    if not html_report_file.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "HTML testing report "
                "does not exist yet."
            ),
        )

    return FileResponse(
        path=html_report_file,
        media_type="text/html",
        filename="latest_report.html",
    )


# ============================================================================
# RUN AI TESTING AGENT
# ============================================================================

@router.post("/run")
def run_ai_testing_agent():
    """
    Execute the AI testing agent and return
    the newly generated testing report.
    """

    # ------------------------------------------------------------------------
    # Validate agent files
    # ------------------------------------------------------------------------

    validate_testing_agent()

    # ------------------------------------------------------------------------
    # Prevent concurrent executions
    # ------------------------------------------------------------------------

    if not _test_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail=(
                "An AI testing run is already "
                "in progress."
            ),
        )

    try:

        # --------------------------------------------------------------------
        # Python executable
        # --------------------------------------------------------------------

        python_executable = sys.executable

        # --------------------------------------------------------------------
        # Agent command
        # --------------------------------------------------------------------

        command = [
            python_executable,
            str(AGENT_FILE),
        ]

        print()
        print(
            "[NEXA/AUTH] Starting AI testing agent..."
        )

        print(
            f"[NEXA/AUTH] Python: "
            f"{python_executable}"
        )

        print(
            f"[NEXA/AUTH] Agent: "
            f"{AGENT_FILE}"
        )

        print(
            f"[NEXA/AUTH] Working directory: "
            f"{TESTING_AGENT_DIR}"
        )

        print()

        # --------------------------------------------------------------------
        # Execute agent
        # --------------------------------------------------------------------

        try:

            process = subprocess.run(
                command,
                cwd=str(TESTING_AGENT_DIR),
                capture_output=True,
                text=True,
                timeout=900,
            )

        except subprocess.TimeoutExpired as exc:

            print(
                "[NEXA/AUTH] AI testing agent "
                "exceeded the 15-minute timeout."
            )

            raise HTTPException(
                status_code=504,
                detail=(
                    "The AI testing agent exceeded "
                    "the 15-minute execution limit."
                ),
            ) from exc

        # --------------------------------------------------------------------
        # Capture process output
        # --------------------------------------------------------------------

        stdout = process.stdout or ""
        stderr = process.stderr or ""

        print()
        print(
            "[NEXA/AUTH] AI testing process finished."
        )

        print(
            f"[NEXA/AUTH] Return code: "
            f"{process.returncode}"
        )

        # --------------------------------------------------------------------
        # Process failed
        # --------------------------------------------------------------------

        if process.returncode != 0:

            error_output = (
                stderr.strip()
                or stdout.strip()
                or "Unknown testing-agent error."
            )

            # Prevent an enormous error response.
            if len(error_output) > 6000:
                error_output = error_output[-6000:]

            print()
            print(
                "[NEXA/AUTH] Testing agent failed:"
            )

            print(error_output)

            raise HTTPException(
                status_code=500,
                detail=(
                    "AI testing agent failed "
                    "to complete.\n\n"
                    + error_output
                ),
            )

        # --------------------------------------------------------------------
        # Verify JSON report
        # --------------------------------------------------------------------

        if not REPORT_FILE.exists():

            raise HTTPException(
                status_code=500,
                detail=(
                    "The AI testing agent completed "
                    "successfully, but no testing "
                    "report was generated."
                ),
            )

        # --------------------------------------------------------------------
        # Read generated report
        # --------------------------------------------------------------------

        report = read_latest_report()

        print()
        print(
            "[NEXA/AUTH] Testing report loaded successfully."
        )

        # --------------------------------------------------------------------
        # Return report to frontend
        # --------------------------------------------------------------------

        return {
            "status": "completed",
            "message": (
                "AI testing completed successfully."
            ),
            "report": report,
        }

    finally:

        # Always release the lock, even when
        # an exception occurs.
        _test_lock.release()