from tests.conftest import auth_headers, register_user, unique_email


def test_register_returns_access_token_and_sets_refresh_cookie(client):
    response = client.post(
        "/api/auth/register",
        json={"email": unique_email(), "full_name": "Jane Doe", "password": "Str0ngPassw0rd!"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"] is None  # browser clients get it via cookie, not the body
    assert body["user"]["full_name"] == "Jane Doe"
    assert "artifactx_refresh" in response.cookies


def test_register_rejects_weak_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": unique_email(), "full_name": "Jane", "password": "alllowercase"},
    )
    assert response.status_code == 422


def test_register_duplicate_email_fails_generically(client):
    email = unique_email()
    register_user(client, email=email)

    response = client.post(
        "/api/auth/register",
        json={"email": email, "full_name": "Second User", "password": "AnotherStr0ng!"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "registration_failed"


def test_login_success_and_wrong_password(client):
    email = unique_email()
    register_user(client, email=email, password="CorrectHorse1!")

    ok = client.post("/api/auth/login", json={"email": email, "password": "CorrectHorse1!"})
    assert ok.status_code == 200

    wrong = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword1!"})
    assert wrong.status_code == 401
    assert wrong.json()["error"]["code"] == "unauthorized"


def test_login_unknown_email_returns_generic_401(client):
    response = client.post(
        "/api/auth/login", json={"email": unique_email(), "password": "WhateverPass1!"}
    )
    assert response.status_code == 401


def test_me_requires_bearer_token(client):
    unauthenticated = client.get("/api/auth/me")
    assert unauthenticated.status_code == 401

    registration = register_user(client)
    authenticated = client.get("/api/auth/me", headers=auth_headers(registration["access_token"]))
    assert authenticated.status_code == 200
    assert authenticated.json()["email"] == registration["user"]["email"]


def test_refresh_rotates_cookie_and_old_token_then_fails(client):
    register_user(client)

    first_refresh = client.post("/api/auth/refresh")
    assert first_refresh.status_code == 200
    old_cookie_value = client.cookies.get("artifactx_refresh")

    second_refresh = client.post("/api/auth/refresh")
    assert second_refresh.status_code == 200
    assert client.cookies.get("artifactx_refresh") != old_cookie_value

    # Replay the now-rotated-away first cookie: this is reuse of a revoked token.
    client.cookies.set("artifactx_refresh", old_cookie_value)
    reused = client.post("/api/auth/refresh")
    assert reused.status_code == 401


def test_logout_revokes_refresh_token(client):
    register_user(client)

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204

    after_logout = client.post("/api/auth/refresh")
    assert after_logout.status_code == 401


def test_native_client_receives_refresh_token_in_body_not_cookie(client):
    response = client.post(
        "/api/auth/register",
        json={"email": unique_email(), "full_name": "CLI User", "password": "Str0ngPassw0rd!"},
        headers={"X-ArtifactX-Client": "native"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["refresh_token"]
    assert "artifactx_refresh" not in response.cookies

    refreshed = client.post(
        "/api/auth/refresh",
        json={"refresh_token": body["refresh_token"]},
        headers={"X-ArtifactX-Client": "native"},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"]


def test_password_reset_request_is_silent_for_unknown_email(client):
    response = client.post("/api/auth/password-reset/request", json={"email": unique_email()})
    assert response.status_code == 202
    assert "sent" in response.json()["message"].lower()


def test_password_reset_confirm_rejects_invalid_token(client):
    response = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "x" * 40, "new_password": "NewStr0ngPass1!"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_token"


def test_login_rate_limit_blocks_after_threshold(client):
    email = unique_email()
    register_user(client, email=email, password="CorrectHorse1!")

    last_status = None
    for _ in range(15):
        last_status = client.post(
            "/api/auth/login", json={"email": email, "password": "WrongPassword1!"}
        ).status_code

    assert last_status == 429
