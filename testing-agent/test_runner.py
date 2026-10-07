import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
TEST_DIR = BACKEND_DIR / "tests"


def run_tests() -> dict:
    """Run the backend pytest suite and capture its results."""

    command = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_DIR),
        "-q",
    ]

    result = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )

    return {
        "command": " ".join(command),
        "return_code": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("NEXA/AUTH — TEST RUNNER")
    print("=" * 60)

    result = run_tests()

    print("\nPytest output:")
    print(result["stdout"])

    if result["stderr"]:
        print("\nWarnings / errors:")
        print(result["stderr"])

    print("-" * 60)

    if result["passed"]:
        print("TEST STATUS: PASSED")
    else:
        print("TEST STATUS: FAILED")

    print(f"Exit code: {result['return_code']}")