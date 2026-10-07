import json
import os
from typing import Any

from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


# ---------------------------------------------------------
# AI Testing Engine
# ---------------------------------------------------------

class AIEngine:
    """
    Gemini-powered AI reasoning layer for the NEXA/AUTH
    automated testing agent.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Add it to testing-agent/.env."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        # The model can be changed through .env
        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

    # -----------------------------------------------------
    # Analyze requirements + API specification
    # -----------------------------------------------------

    def analyze_requirements(
        self,
        requirements: str,
        api_spec: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ask Gemini to analyze the software requirements
        together with the current API capabilities.

        Gemini identifies:
        - Additional executable test scenarios
        - Security scenarios
        - Edge cases
        - Coverage gaps
        """

        api_spec_json = json.dumps(
            api_spec,
            indent=2,
        )

        prompt = f"""
You are an expert software testing engineer and
application security tester.

Your task is to analyze an authentication system and
identify additional test scenarios that should be
considered.

========================================================
AUTHENTICATION REQUIREMENTS
========================================================

{requirements}

========================================================
CURRENT API SPECIFICATION
========================================================

{api_spec_json}

========================================================
IMPORTANT TESTING RULES
========================================================

A scenario can be marked EXECUTABLE only when the
current API specification contains the functionality
required to perform that test.

If the required functionality does NOT exist:

- Do NOT pretend that the test can be executed.
- Mark it as COVERAGE_GAP.
- Explain which functionality is missing.

Do not invent API endpoints.

For example:

If logout is not implemented:

    Logout token invalidation
    → COVERAGE_GAP

If there is no protected endpoint:

    JWT tampering against protected resource
    → COVERAGE_GAP

If signup exists:

    Duplicate email registration
    → EXECUTABLE

If login exists:

    Incorrect password
    → EXECUTABLE

========================================================
TESTING AREAS
========================================================

Analyze the system for:

1. Functional edge cases
2. Boundary conditions
3. Input validation
4. Authentication security
5. Authorization
6. Malicious input
7. Error handling
8. Session management
9. JWT security
10. Account security
11. API robustness
12. Missing security controls

Pay particular attention to:

- SQL injection
- XSS
- credential attacks
- account enumeration
- password policy weaknesses
- JWT manipulation
- expired tokens
- authorization failures
- rate limiting
- account lockout
- concurrent requests
- boundary values
- malformed input

========================================================
OUTPUT FORMAT
========================================================

Return ONLY valid JSON.

Do not return Markdown.

Do not use code fences.

Use exactly this structure:

{{
    "analysis": "short summary of the overall testing assessment",

    "additional_scenarios": [
        {{
            "name": "test scenario name",
            "objective": "what this test verifies",
            "priority": "Critical|High|Medium|Low",
            "category": "Security|Validation|Functional|Edge Case",
            "execution_status": "EXECUTABLE|COVERAGE_GAP",
            "reason": "why the scenario is executable or why it is a coverage gap"
        }}
    ]
}}

========================================================
QUALITY REQUIREMENTS
========================================================

Generate meaningful scenarios rather than duplicate tests.

Prioritize security-critical scenarios.

Do not claim that a test passed.

You are generating test scenarios only.

Do not invent functionality that is not present in the
provided API specification.
"""

        # -------------------------------------------------
        # Call Gemini
        # -------------------------------------------------

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        response_text = response.text.strip()

        # -------------------------------------------------
        # Parse JSON returned by Gemini
        # -------------------------------------------------

        try:
            result = json.loads(response_text)

        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini returned an invalid JSON response.\n"
                f"Response received:\n{response_text}"
            ) from exc

        # -------------------------------------------------
        # Validate basic response structure
        # -------------------------------------------------

        additional_scenarios = result.get(
            "additional_scenarios",
            [],
        )

        if not isinstance(
            additional_scenarios,
            list,
        ):
            raise RuntimeError(
                "Gemini returned an invalid "
                "'additional_scenarios' structure."
            )

        return {
            "provider": "Google Gemini",
            "model": self.model,
            "status": "success",
            "analysis": result.get(
                "analysis",
                "",
            ),
            "additional_scenarios": additional_scenarios,
        }


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":

    # Import the actual API specification
    # used by the testing agent.
    from api_spec import API_SPEC

    engine = AIEngine()

    requirements = """
    The authentication system must allow users to create
    accounts using a unique username and email address.

    Registration requires:

    - Username with at least 3 characters
    - Valid email address
    - Password with at least 8 characters
    - Password must contain a lowercase letter
    - Password must contain an uppercase letter
    - Password must contain a number
    - Password must contain a special character
    - Password and confirm password must match

    Users must be able to log in using their registered
    email and password.

    Invalid credentials must be rejected.

    Duplicate usernames and emails must be rejected.

    Inactive accounts must not be allowed to log in.

    The system uses JWT authentication and secure
    password hashing.
    """

    print("=" * 70)
    print("NEXA/AUTH — GEMINI AI TESTING ENGINE")
    print("=" * 70)

    print("\nAnalyzing authentication requirements...")
    print("Analyzing current API capabilities...")

    try:
        result = engine.analyze_requirements(
            requirements,
            API_SPEC,
        )

        print(
            f"\nProvider : {result['provider']}"
        )

        print(
            f"Model    : {result['model']}"
        )

        print(
            f"Status   : {result['status']}"
        )

        # -------------------------------------------------
        # AI Analysis
        # -------------------------------------------------

        print("\nAI Testing Analysis:")
        print("-" * 70)

        print(
            result["analysis"]
        )

        # -------------------------------------------------
        # Additional scenarios
        # -------------------------------------------------

        scenarios = result[
            "additional_scenarios"
        ]

        print(
            f"\nAI identified "
            f"{len(scenarios)} additional scenarios."
        )

        print(
            "\nAdditional Test Scenarios:"
        )

        print("-" * 70)

        for index, scenario in enumerate(
            scenarios,
            start=1,
        ):

            print(
                f"\n{index}. "
                f"{scenario.get('name', 'Unnamed scenario')}"
            )

            print(
                f"   Objective : "
                f"{scenario.get('objective', 'N/A')}"
            )

            print(
                f"   Priority  : "
                f"{scenario.get('priority', 'N/A')}"
            )

            print(
                f"   Category  : "
                f"{scenario.get('category', 'N/A')}"
            )

            print(
                f"   Status    : "
                f"{scenario.get('execution_status', 'N/A')}"
            )

            print(
                f"   Reason    : "
                f"{scenario.get('reason', 'N/A')}"
            )

        print("\n" + "=" * 70)
        print("AI ANALYSIS COMPLETED")
        print("=" * 70)

    except Exception as exc:
        print("\nAI ENGINE ERROR")
        print("-" * 70)
        print(str(exc))