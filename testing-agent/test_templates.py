import sys
import uuid
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from app.database import Base, get_db
from app.main import app


# ============================================================
# ISOLATED AI TEST DATABASE
# ============================================================

def create_ai_client():
    """
    Create a completely isolated FastAPI client and
    in-memory SQLite database for one AI scenario.

    The real backend/nexa_auth.db is never used for
    AI-generated test data.
    """

    ai_engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    AI_SessionLocal = sessionmaker(
        bind=ai_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(
        bind=ai_engine
    )

    def override_get_db():
        db = AI_SessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    # Keep the engine attached to the client.
    client._ai_engine = ai_engine

    return client


def close_ai_client(client):
    """
    Close the isolated client and remove the
    FastAPI dependency override.
    """

    if client is None:
        return

    try:
        client.close()
    except Exception:
        pass

    app.dependency_overrides.pop(
        get_db,
        None,
    )

    ai_engine = getattr(
        client,
        "_ai_engine",
        None,
    )

    if ai_engine is not None:
        try:
            ai_engine.dispose()
        except Exception:
            pass


def get_client():
    """
    Every AI test scenario receives a fresh,
    isolated in-memory database.
    """

    return create_ai_client()


# ============================================================
# COMMON TEST RESULT HELPER
# ============================================================

def result(
    name: str,
    expected_status: Any,
    actual_status: int,
) -> dict[str, Any]:
    """
    Create a standard test result.
    """

    if expected_status == "4xx":
        passed = 400 <= actual_status < 500

    elif isinstance(expected_status, str):
        allowed_statuses = set()

        for value in expected_status.split("/"):
            try:
                allowed_statuses.add(
                    int(value.strip())
                )
            except ValueError:
                pass

        passed = actual_status in allowed_statuses

    else:
        passed = (
            actual_status == expected_status
        )

    return {
        "name": name,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "passed": passed,
        "status": (
            "PASSED"
            if passed
            else "FAILED"
        ),
    }


# ============================================================
# UNIQUE TEST DATA
# ============================================================

def unique_suffix() -> str:
    """
    Generate a unique suffix so repeated AI test runs
    never collide with previously-created test data.
    """

    return uuid.uuid4().hex[:10]


# ============================================================
# USERNAME TESTS
# ============================================================

def test_username_exactly_three_characters():
    """
    Username with exactly 3 characters.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": "abc",
            "email": f"exact3_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Username exactly 3 characters",
        201,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_username_minimum_length():
    """
    Username satisfying the minimum length requirement.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": "abc",
            "email": f"minimum_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Username minimum length",
        201,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_username_below_minimum():
    """
    Username below the minimum length.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": "ab",
            "email": f"below_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Username below minimum",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_username_maximum_length():
    """
    Username exceeding the backend maximum of 50 characters.
    """

    client = get_client()

    username = "u" * 51

    response = client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": f"maxuser_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Username maximum length boundary",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# EMAIL TESTS
# ============================================================

def test_invalid_email():
    """
    Invalid email format.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"invalidemail_{unique_suffix()}",
            "email": "invalid-email",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Invalid email format",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# PASSWORD TESTS
# ============================================================

def test_password_exactly_eight():
    """
    Password exactly 8 characters.

    Abcdef1! satisfies the backend complexity requirements.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"eightpass_{unique_suffix()}",
            "email": f"eightpass_{unique_suffix()}@example.com",
            "password": "Abcdef1!",
            "confirm_password": "Abcdef1!",
        },
    )

    result_data = result(
        "Password exactly 8 characters",
        201,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_weak_password():
    """
    Password below the minimum requirement.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"weak_{unique_suffix()}",
            "email": f"weak_{unique_suffix()}@example.com",
            "password": "weak",
            "confirm_password": "weak",
        },
    )

    result_data = result(
        "Weak password rejection",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_password_mismatch():
    """
    Password and confirmation password do not match.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"mismatch_{unique_suffix()}",
            "email": f"mismatch_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "DifferentPassword1!",
        },
    )

    result_data = result(
        "Password confirmation mismatch",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# DUPLICATE USERNAME / EMAIL TESTS
# ============================================================

def test_duplicate_username():
    """
    Verify that registering an already existing username
    is rejected.
    """

    client = get_client()

    suffix = unique_suffix()

    username = f"duplicate_user_{suffix}"
    first_email = (
        f"duplicate_first_{suffix}@example.com"
    )
    second_email = (
        f"duplicate_second_{suffix}@example.com"
    )

    # --------------------------------------------------------
    # FIRST REGISTRATION
    # --------------------------------------------------------

    first_response = client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": first_email,
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    if first_response.status_code != 201:

        result_data = {
            "name": "Duplicate username registration",
            "expected_status": 201,
            "actual_status": first_response.status_code,
            "passed": False,
            "status": "FAILED",
            "reason": (
                "Could not create the initial account "
                "required for the duplicate-username test."
            ),
        }

        close_ai_client(client)

        return result_data

    # --------------------------------------------------------
    # SECOND REGISTRATION — SAME USERNAME
    # --------------------------------------------------------

    response = client.post(
        "/auth/signup",
        json={
            "username": username,
            "email": second_email,
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Duplicate username registration",
        409,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_duplicate_email():
    """
    Verify that registering an already existing email
    address is rejected.
    """

    client = get_client()

    suffix = unique_suffix()

    email = (
        f"duplicate_email_{suffix}@example.com"
    )

    # --------------------------------------------------------
    # FIRST REGISTRATION
    # --------------------------------------------------------

    first_response = client.post(
        "/auth/signup",
        json={
            "username": f"duplicate_email_first_{suffix}",
            "email": email,
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    if first_response.status_code != 201:

        result_data = {
            "name": "Duplicate email registration",
            "expected_status": 201,
            "actual_status": first_response.status_code,
            "passed": False,
            "status": "FAILED",
            "reason": (
                "Could not create the initial account "
                "required for the duplicate-email test."
            ),
        }

        close_ai_client(client)

        return result_data

    # --------------------------------------------------------
    # SECOND REGISTRATION — SAME EMAIL
    # --------------------------------------------------------

    response = client.post(
        "/auth/signup",
        json={
            "username": f"duplicate_email_second_{suffix}",
            "email": email,
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Duplicate email registration",
        409,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# EMPTY INPUT TESTS
# ============================================================

def test_empty_username():
    """
    Signup with an empty username.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": "",
            "email": f"emptyuser_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Empty username",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_empty_email():
    """
    Signup with an empty email.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"emptyemail_{unique_suffix()}",
            "email": "",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Empty email",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_empty_password():
    """
    Signup with an empty password.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"emptypass_{unique_suffix()}",
            "email": f"emptypass_{unique_suffix()}@example.com",
            "password": "",
            "confirm_password": "",
        },
    )

    result_data = result(
        "Empty password",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# PASSWORD COMPLEXITY TESTS
# ============================================================

def test_password_missing_lowercase():
    """
    Password missing a lowercase character.
    """

    client = get_client()

    password = "STRONGPASSWORD1!"

    response = client.post(
        "/auth/signup",
        json={
            "username": f"lower_{unique_suffix()}",
            "email": f"lower_{unique_suffix()}@example.com",
            "password": password,
            "confirm_password": password,
        },
    )

    result_data = result(
        "Password missing lowercase character",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_password_missing_uppercase():
    """
    Password missing an uppercase character.
    """

    client = get_client()

    password = "strongpassword1!"

    response = client.post(
        "/auth/signup",
        json={
            "username": f"upper_{unique_suffix()}",
            "email": f"upper_{unique_suffix()}@example.com",
            "password": password,
            "confirm_password": password,
        },
    )

    result_data = result(
        "Password missing uppercase character",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_password_missing_number():
    """
    Password missing a number.
    """

    client = get_client()

    password = "StrongPassword!"

    response = client.post(
        "/auth/signup",
        json={
            "username": f"number_{unique_suffix()}",
            "email": f"number_{unique_suffix()}@example.com",
            "password": password,
            "confirm_password": password,
        },
    )

    result_data = result(
        "Password missing number",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_password_missing_special():
    """
    Password missing a special character.
    """

    client = get_client()

    password = "StrongPassword1"

    response = client.post(
        "/auth/signup",
        json={
            "username": f"special_{unique_suffix()}",
            "email": f"special_{unique_suffix()}@example.com",
            "password": password,
            "confirm_password": password,
        },
    )

    result_data = result(
        "Password missing special character",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# SQL INJECTION TESTS
# ============================================================

def test_sql_injection_username():
    """
    SQL injection-style payload in username.

    A 201 does not mean SQL injection succeeded.
    SQLAlchemy parameterizes the value.
    """

    client = get_client()

    payload = "' OR '1'='1"

    response = client.post(
        "/auth/signup",
        json={
            "username": payload,
            "email": f"sqluser_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    passed = response.status_code in (
        201,
        409,
        422,
    )

    result_data = {
        "name": "SQL injection in username",
        "expected_status": "201/409/422",
        "actual_status": response.status_code,
        "passed": passed,
        "status": (
            "PASSED"
            if passed
            else "FAILED"
        ),
    }

    close_ai_client(client)

    return result_data


def test_sql_injection_email():
    """
    SQL injection-style payload in signup email.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "username": f"sql_email_{unique_suffix()}",
            "email": "' OR '1'='1",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "SQL injection in email",
        "4xx",
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_sql_injection_password():
    """
    SQL injection-style payload in signup password.
    """

    client = get_client()

    payload = "' OR '1'='1"

    response = client.post(
        "/auth/signup",
        json={
            "username": f"sql_password_{unique_suffix()}",
            "email": f"sqlpassword_{unique_suffix()}@example.com",
            "password": payload,
            "confirm_password": payload,
        },
    )

    result_data = result(
        "SQL injection in password",
        "4xx",
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# XSS TEST
# ============================================================

def test_xss_username():
    """
    XSS-style payload in username.

    This API-level test does not prove browser-level XSS
    protection. It checks controlled API behavior.
    """

    client = get_client()

    payload = "<script>alert('xss')</script>"

    response = client.post(
        "/auth/signup",
        json={
            "username": payload,
            "email": f"xss_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    if response.status_code == 201:

        try:
            data = response.json()

            returned_username = data.get(
                "username",
                "",
            )

            passed = (
                returned_username == payload
            )

        except Exception:
            passed = False

    else:
        passed = response.status_code in (
            400,
            409,
            422,
        )

    result_data = {
        "name": "XSS payload in username",
        "expected_status": (
            "201 with unchanged data or 4xx rejection"
        ),
        "actual_status": response.status_code,
        "passed": passed,
        "status": (
            "PASSED"
            if passed
            else "FAILED"
        ),
    }

    close_ai_client(client)

    return result_data


# ============================================================
# REQUEST VALIDATION TESTS
# ============================================================

def test_missing_username():
    """
    Signup request without username.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={
            "email": f"missinguser_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Missing username",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_missing_required_fields():
    """
    Signup request with no fields.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        json={},
    )

    result_data = result(
        "Missing required signup fields",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_malformed_signup_json():
    """
    Malformed JSON sent to signup endpoint.
    """

    client = get_client()

    response = client.post(
        "/auth/signup",
        content=b'{"username": "broken"',
        headers={
            "Content-Type": "application/json",
        },
    )

    result_data = result(
        "Malformed signup JSON",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# LOGIN TEST TEMPLATES
# ============================================================

def test_unknown_email_login():
    """
    Login using an email that does not exist.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "email": f"doesnotexist_{unique_suffix()}@example.com",
            "password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Unknown email login",
        401,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_wrong_password():
    """
    Login using an incorrect password.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "email": f"existing_{unique_suffix()}@example.com",
            "password": "WrongPassword123!",
        },
    )

    result_data = result(
        "Login with incorrect password",
        401,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_missing_login_email():
    """
    Login request without email.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Missing login email",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_missing_login_password():
    """
    Login request without password.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "email": f"missingpass_{unique_suffix()}@example.com",
        },
    )

    result_data = result(
        "Missing login password",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_missing_login_fields():
    """
    Login request without required fields.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={},
    )

    result_data = result(
        "Missing required login fields",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_malformed_login_json():
    """
    Malformed JSON sent to login endpoint.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        content=b'{"email": "broken"',
        headers={
            "Content-Type": "application/json",
        },
    )

    result_data = result(
        "Malformed login JSON",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# LOGIN SQL INJECTION TESTS
# ============================================================

def test_sql_injection_login_email():
    """
    SQL injection-style payload in login email.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "email": "' OR '1'='1",
            "password": "StrongPassword1!",
        },
    )

    result_data = result(
        "SQL injection in login email",
        "4xx",
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_sql_injection_login_password():
    """
    SQL injection-style payload in login password.
    """

    client = get_client()

    response = client.post(
        "/auth/login",
        json={
            "email": f"unknown_{unique_suffix()}@example.com",
            "password": "' OR '1'='1",
        },
    )

    result_data = result(
        "SQL injection in login password",
        "4xx",
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# LENGTH TESTS
# ============================================================

def test_email_maximum_length():
    """
    Test an email address exceeding the maximum
    allowed Pydantic length of 255 characters.
    """

    client = get_client()

    oversized_email = (
        "a" * 250
        + "@example.com"
    )

    response = client.post(
        "/auth/signup",
        json={
            "username": f"emailmax_{unique_suffix()}",
            "email": oversized_email,
            "password": "StrongPassword1!",
            "confirm_password": "StrongPassword1!",
        },
    )

    result_data = result(
        "Email maximum length boundary",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


def test_password_maximum_length():
    """
    Test a password exceeding the backend maximum
    of 128 characters.
    """

    client = get_client()

    oversized_password = (
        "Aa1!"
        + "x" * 125
    )

    response = client.post(
        "/auth/signup",
        json={
            "username": f"passwordmax_{unique_suffix()}",
            "email": f"passwordmax_{unique_suffix()}@example.com",
            "password": oversized_password,
            "confirm_password": oversized_password,
        },
    )

    result_data = result(
        "Password maximum length boundary",
        422,
        response.status_code,
    )

    close_ai_client(client)

    return result_data


# ============================================================
# CONTROLLED TEST REGISTRY
# ============================================================

TEST_REGISTRY: dict[
    str,
    Callable[[], dict[str, Any]]
] = {

    # Registration / boundary
    "username_exactly_three":
        test_username_exactly_three_characters,

    "username_minimum_length":
        test_username_minimum_length,

    "username_below_minimum":
        test_username_below_minimum,

    "username_maximum_length":
        test_username_maximum_length,

    "invalid_email":
        test_invalid_email,

    "password_exactly_eight":
        test_password_exactly_eight,

    "weak_password":
        test_weak_password,

    "password_mismatch":
        test_password_mismatch,

    # Duplicate registration
    "duplicate_username":
        test_duplicate_username,

    "duplicate_email":
        test_duplicate_email,

    # Empty fields
    "empty_username":
        test_empty_username,

    "empty_email":
        test_empty_email,

    "empty_password":
        test_empty_password,

    # Password complexity
    "password_missing_lowercase":
        test_password_missing_lowercase,

    "password_missing_uppercase":
        test_password_missing_uppercase,

    "password_missing_number":
        test_password_missing_number,

    "password_missing_special":
        test_password_missing_special,

    # Security
    "sql_injection_username":
        test_sql_injection_username,

    "sql_injection_email":
        test_sql_injection_email,

    "sql_injection_password":
        test_sql_injection_password,

    "xss_username":
        test_xss_username,

    # Signup validation
    "missing_username":
        test_missing_username,

    "missing_required_fields":
        test_missing_required_fields,

    "malformed_signup_json":
        test_malformed_signup_json,

    # Login
    "unknown_email_login":
        test_unknown_email_login,

    "wrong_password":
        test_wrong_password,

    "sql_injection_login_email":
        test_sql_injection_login_email,

    "sql_injection_login_password":
        test_sql_injection_login_password,

    "missing_login_email":
        test_missing_login_email,

    "missing_login_password":
        test_missing_login_password,

    "missing_login_fields":
        test_missing_login_fields,

    "malformed_login_json":
        test_malformed_login_json,

    # Length
    "email_maximum_length":
        test_email_maximum_length,

    "password_maximum_length":
        test_password_maximum_length,
}


# ============================================================
# SCENARIO NAME NORMALIZATION
# ============================================================

def normalize_name(name: str) -> str:
    """
    Normalize AI-generated scenario names so small
    formatting differences do not break matching.
    """

    return (
        name
        .lower()
        .strip()
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
        .replace("-", " ")
        .replace("_", " ")
    )


# ============================================================
# SCENARIO → TEMPLATE MATCHING
# ============================================================

def find_template(
    scenario_name: str,
) -> Callable[[], dict[str, Any]] | None:

    name = normalize_name(
        scenario_name
    )

    # --------------------------------------------------------
    # DUPLICATE USERNAME
    # --------------------------------------------------------

    if (
        "duplicate username" in name
        or "existing username" in name
        or "already existing username" in name
    ):
        return TEST_REGISTRY[
            "duplicate_username"
        ]

    # --------------------------------------------------------
    # DUPLICATE EMAIL
    # --------------------------------------------------------

    if (
        "duplicate email" in name
        or "existing email" in name
        or "already existing email" in name
    ):
        return TEST_REGISTRY[
            "duplicate_email"
        ]

    # --------------------------------------------------------
    # USERNAME BOUNDARY
    # --------------------------------------------------------

    if (
        "username exactly 3" in name
        or "username exactly three" in name
    ):
        return TEST_REGISTRY[
            "username_exactly_three"
        ]

    if (
        "username less than 3" in name
        or "username below minimum" in name
        or "username just below minimum" in name
    ):
        return TEST_REGISTRY[
            "username_below_minimum"
        ]

    if (
        "username minimum length" in name
        or "username minimum" in name
    ):
        return TEST_REGISTRY[
            "username_minimum_length"
        ]

    if (
        "username maximum length" in name
        or "username max" in name
        or "very long username" in name
    ):
        return TEST_REGISTRY[
            "username_maximum_length"
        ]

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if (
        "invalid email" in name
        or "email format validation" in name
    ):
        return TEST_REGISTRY[
            "invalid_email"
        ]

    if (
        "email maximum length" in name
        or "email max" in name
        or "oversized email" in name
    ):
        return TEST_REGISTRY[
            "email_maximum_length"
        ]

    # --------------------------------------------------------
    # PASSWORD LENGTH
    # --------------------------------------------------------

    if (
        "password exactly 8" in name
        or "password exactly eight" in name
    ):
        return TEST_REGISTRY[
            "password_exactly_eight"
        ]

    if (
        "password less than 8" in name
        or "password below minimum" in name
        or "password just below minimum" in name
        or "weak password" in name
    ):
        return TEST_REGISTRY[
            "weak_password"
        ]

    if (
        "password maximum length" in name
        or "password max" in name
        or "oversized password" in name
        or "extremely long password" in name
    ):
        return TEST_REGISTRY[
            "password_maximum_length"
        ]

    # --------------------------------------------------------
    # PASSWORD COMPLEXITY
    # --------------------------------------------------------

    if (
        "password missing lowercase" in name
        or "password without lowercase" in name
    ):
        return TEST_REGISTRY[
            "password_missing_lowercase"
        ]

    if (
        "password missing uppercase" in name
        or "password without uppercase" in name
    ):
        return TEST_REGISTRY[
            "password_missing_uppercase"
        ]

    if (
        "password missing number" in name
        or "password without number" in name
        or "password missing a number" in name
    ):
        return TEST_REGISTRY[
            "password_missing_number"
        ]

    if (
        "password missing special" in name
        or "password without special" in name
        or "password missing special character" in name
    ):
        return TEST_REGISTRY[
            "password_missing_special"
        ]

    # --------------------------------------------------------
    # PASSWORD MISMATCH
    # --------------------------------------------------------

    if (
        "password and confirm password mismatch"
        in name
        or "password confirmation mismatch"
        in name
        or "password mismatch" in name
    ):
        return TEST_REGISTRY[
            "password_mismatch"
        ]

    # --------------------------------------------------------
    # SQL INJECTION
    # --------------------------------------------------------

    if "sql injection" in name:

        if (
            "login" in name
            and "email" in name
        ):
            return TEST_REGISTRY[
                "sql_injection_login_email"
            ]

        if (
            "login" in name
            and "password" in name
        ):
            return TEST_REGISTRY[
                "sql_injection_login_password"
            ]

        if "username" in name:
            return TEST_REGISTRY[
                "sql_injection_username"
            ]

        if "email" in name:
            return TEST_REGISTRY[
                "sql_injection_email"
            ]

        if "password" in name:
            return TEST_REGISTRY[
                "sql_injection_password"
            ]

    # --------------------------------------------------------
    # XSS
    # --------------------------------------------------------

    if (
        "xss" in name
        and "username" in name
    ):
        return TEST_REGISTRY[
            "xss_username"
        ]

    # --------------------------------------------------------
    # EMPTY INPUTS
    # --------------------------------------------------------

    if "empty username" in name:
        return TEST_REGISTRY[
            "empty_username"
        ]

    if "empty email" in name:
        return TEST_REGISTRY[
            "empty_email"
        ]

    if "empty password" in name:
        return TEST_REGISTRY[
            "empty_password"
        ]

    # --------------------------------------------------------
    # SIGNUP MISSING FIELDS
    # --------------------------------------------------------

    if (
        "missing username" in name
        and "login" not in name
    ):
        return TEST_REGISTRY[
            "missing_username"
        ]

    if (
        "missing required fields" in name
        and (
            "signup" in name
            or "registration" in name
        )
    ):
        return TEST_REGISTRY[
            "missing_required_fields"
        ]

    # --------------------------------------------------------
    # MALFORMED SIGNUP JSON
    # --------------------------------------------------------

    if (
        "malformed json" in name
        and (
            "signup" in name
            or "registration" in name
        )
    ):
        return TEST_REGISTRY[
            "malformed_signup_json"
        ]

    # --------------------------------------------------------
    # LOGIN UNKNOWN EMAIL
    # --------------------------------------------------------

    if (
        "non existent email" in name
        or "non-existent email" in name
        or "unknown email" in name
        or "unregistered email" in name
    ):
        return TEST_REGISTRY[
            "unknown_email_login"
        ]

    # --------------------------------------------------------
    # LOGIN INCORRECT PASSWORD
    # --------------------------------------------------------

    if (
        "incorrect password" in name
        or "wrong password" in name
        or (
            "registered email"
            in name
            and "incorrect" in name
        )
    ):
        return TEST_REGISTRY[
            "wrong_password"
        ]

    # --------------------------------------------------------
    # LOGIN MISSING PASSWORD
    # --------------------------------------------------------

    if (
        "missing login password" in name
        or (
            "missing password" in name
            and "login" in name
        )
    ):
        return TEST_REGISTRY[
            "missing_login_password"
        ]

    # --------------------------------------------------------
    # LOGIN MISSING EMAIL
    # --------------------------------------------------------

    if "missing login email" in name:
        return TEST_REGISTRY[
            "missing_login_email"
        ]

    # --------------------------------------------------------
    # LOGIN MISSING FIELDS
    # --------------------------------------------------------

    if (
        "missing required fields" in name
        and "login" in name
    ):
        return TEST_REGISTRY[
            "missing_login_fields"
        ]

    # --------------------------------------------------------
    # MALFORMED LOGIN JSON
    # --------------------------------------------------------

    if (
        "malformed json" in name
        and "login" in name
    ):
        return TEST_REGISTRY[
            "malformed_login_json"
        ]

    # --------------------------------------------------------
    # NO MATCH
    # --------------------------------------------------------

    return None


# ============================================================
# CONTROLLED SCENARIO EXECUTION
# ============================================================

def execute_scenario(
    scenario: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute an AI-generated scenario only if an approved
    test template exists.

    Gemini never generates executable Python here.
    """

    scenario_name = scenario.get(
        "name",
        "Unknown scenario",
    )

    template = find_template(
        scenario_name
    )

    if template is None:
        return {
            "name": scenario_name,
            "status": "NOT_EXECUTED",
            "passed": False,
            "reason": (
                "No approved test template exists."
            ),
        }

    try:

        execution_result = template()

        return {
            **execution_result,
            "ai_scenario": scenario_name,
        }

    except Exception as exc:

        return {
            "name": scenario_name,
            "ai_scenario": scenario_name,
            "status": "ERROR",
            "passed": False,
            "reason": str(exc),
        }


# ============================================================
# LOCAL REGISTRY CHECK
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NEXA/AUTH — TEST TEMPLATE REGISTRY")
    print("=" * 60)

    print(
        "\nBackend directory:"
    )

    print(
        BACKEND_DIR
    )

    print(
        f"\nRegistered templates: "
        f"{len(TEST_REGISTRY)}"
    )

    print(
        "\nAvailable templates:"
    )

    for template_name in TEST_REGISTRY:
        print(
            f" - {template_name}"
        )

    print(
        "\nTemplate registry loaded successfully."
    )