import uuid


def test_list_users_as_director(client, director_user, director_token):
    response = client.get(
        "/api/v1/usuarios",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_list_users_as_colaborador_forbidden(client, colaborador_user, colaborador_token):
    response = client.get(
        "/api/v1/usuarios",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_create_user(client, director_user, director_token):
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nombre": "New User",
            "email": "new@nia.com",
            "password": "Test1234!",
            "rol": "colaborador",
        },
        cookies={"access_token": director_token},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@nia.com"
    assert data["rol"] == "colaborador"
    assert data["activo"] is True
    assert "password_hash" not in data


def test_create_user_duplicate_email(client, director_user, director_token):
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nombre": "Dup User",
            "email": "director@nia.com",
            "password": "Test1234!",
            "rol": "colaborador",
        },
        cookies={"access_token": director_token},
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONFLICT_STATE"


def test_create_user_invalid_role(client, director_user, director_token):
    response = client.post(
        "/api/v1/usuarios",
        json={
            "nombre": "Bad Role",
            "email": "bad@nia.com",
            "password": "Test1234!",
            "rol": "admin",
        },
        cookies={"access_token": director_token},
    )
    assert response.status_code == 422


def test_update_user(client, director_user, director_token, colaborador_user):
    response = client.put(
        f"/api/v1/usuarios/{colaborador_user.id}",
        json={"nombre": "Updated Name"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Updated Name"


def test_update_user_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.put(
        f"/api/v1/usuarios/{fake_id}",
        json={"nombre": "Test"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_reset_password(client, director_user, director_token, colaborador_user):
    response = client.post(
        f"/api/v1/usuarios/{colaborador_user.id}/reset-password",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset email sent"


def test_list_users_filter_by_role(client, director_user, director_token, colaborador_user):
    response = client.get(
        "/api/v1/usuarios?rol=colaborador",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["rol"] == "colaborador" for item in data["items"])
