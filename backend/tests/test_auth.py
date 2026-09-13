def test_login_valid_credentials(client, director_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "director@nia.com", "password": "Director123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "director@nia.com"
    assert data["user"]["rol"] == "director"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_login_invalid_password(client, director_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "director@nia.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@nia.com", "password": "test"},
    )
    assert response.status_code == 401


def test_me_authenticated(client, director_user, director_token):
    response = client.get(
        "/api/v1/auth/me",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "director@nia.com"


def test_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh_token(client, director_user):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "director@nia.com", "password": "Director123!"},
    )
    refresh_cookie = login_resp.cookies.get("refresh_token")
    assert refresh_cookie is not None

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        cookies={"refresh_token": refresh_cookie},
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.cookies


def test_refresh_no_token(client):
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


def test_logout(client, director_user):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "director@nia.com", "password": "Director123!"},
    )
    assert login_resp.status_code == 200

    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Logged out"


def test_change_password(client, director_user, director_token):
    response = client.put(
        "/api/v1/auth/change-password",
        json={"current_password": "Director123!", "new_password": "NewPass123!"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated"

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "director@nia.com", "password": "NewPass123!"},
    )
    assert login_resp.status_code == 200


def test_change_password_wrong_current(client, director_user, director_token):
    response = client.put(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong", "new_password": "NewPass123!"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 401
