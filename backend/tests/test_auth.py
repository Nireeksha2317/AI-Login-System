# =========================================================
# SIGNUP TESTS
# =========================================================


def test_signup_success(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True

    # Sensitive information must never be returned.
    assert "password" not in data
    assert "password_hash" not in data


def test_signup_duplicate_email(client):
    user_data = {
        "username": "firstuser",
        "email": "duplicate@example.com",
        "password": "SecurePass@123",
        "confirm_password": "SecurePass@123",
    }

    first_response = client.post(
        "/auth/signup",
        json=user_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json={
            **user_data,
            "username": "seconduser",
        },
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "Email is already registered."
    )


def test_signup_duplicate_username(client):
    first_response = client.post(
        "/auth/signup",
        json={
            "username": "sameusername",
            "email": "first@example.com",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json={
            "username": "sameusername",
            "email": "second@example.com",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        },
    )

    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "Username is already registered."
    )


def test_signup_password_mismatch(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "mismatchuser",
            "email": "mismatch@example.com",
            "password": "SecurePass@123",
            "confirm_password": "DifferentPass@123",
        },
    )

    assert response.status_code == 422


def test_signup_invalid_email(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "emailuser",
            "email": "invalid-email",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        },
    )

    assert response.status_code == 422


def test_signup_weak_password(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak",
            "confirm_password": "weak",
        },
    )

    assert response.status_code == 422


# =========================================================
# LOGIN TESTS
# =========================================================


def create_test_user(client):
    response = client.post(
        "/auth/signup",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "SecurePass@123",
            "confirm_password": "SecurePass@123",
        },
    )

    assert response.status_code == 201


def test_login_success(client):
    create_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "SecurePass@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    assert data["user"]["username"] == "loginuser"
    assert data["user"]["email"] == "login@example.com"

    # Password must never be returned.
    assert "password" not in data
    assert "password_hash" not in data


def test_login_wrong_password(client):
    create_test_user(client)

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "WrongPassword@123",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password."
    )


def test_login_unknown_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "SecurePass@123",
        },
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Invalid email or password."
    )