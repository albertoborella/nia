import uuid


def _create_auspiciante(client, token, nombre="Auspiciante Test"):
    return client.post(
        "/api/v1/auspiciantes",
        json={
            "nombre": nombre,
            "logo_url": "https://example.com/logo.png",
            "enlace": "https://example.com",
            "descripcion": "Test description",
        },
        cookies={"access_token": token},
    )


def _create_boletin(client, token):
    return client.post(
        "/api/v1/boletines",
        json={
            "nombre": "Boletin Test",
            "periodo_inicio": "2026-01-01",
            "periodo_fin": "2026-01-31",
        },
        cookies={"access_token": token},
    )


def test_create_auspiciante(client, director_user, director_token):
    response = _create_auspiciante(client, director_token)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Auspiciante Test"
    assert data["activo"] is True
    assert data["logo_url"] == "https://example.com/logo.png"


def test_create_auspiciante_as_colaborador_forbidden(client, colaborador_token):
    response = _create_auspiciante(client, colaborador_token)
    assert response.status_code == 403


def test_list_auspiciantes(client, director_user, director_token):
    _create_auspiciante(client, director_token, "Ausp 1")
    _create_auspiciante(client, director_token, "Ausp 2")
    response = client.get(
        "/api/v1/auspiciantes",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


def test_list_auspiciantes_filter_activo(client, director_user, director_token):
    _create_auspiciante(client, director_token, "Active One")
    resp = _create_auspiciante(client, director_token, "To Disable")
    ausp_id = resp.json()["id"]
    client.put(
        f"/api/v1/auspiciantes/{ausp_id}",
        json={"activo": False},
        cookies={"access_token": director_token},
    )
    response = client.get(
        "/api/v1/auspiciantes?activo=true",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    names = [a["nombre"] for a in response.json()["items"]]
    assert "Active One" in names
    assert "To Disable" not in names


def test_get_auspiciante_detail(client, director_user, director_token):
    create_resp = _create_auspiciante(client, director_token)
    ausp_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/auspiciantes/{ausp_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["id"] == ausp_id


def test_get_auspiciante_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/auspiciantes/{fake_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_update_auspiciante(client, director_user, director_token):
    create_resp = _create_auspiciante(client, director_token)
    ausp_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/auspiciantes/{ausp_id}",
        json={"nombre": "Updated Name"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Updated Name"


def test_update_auspiciante_as_colaborador_forbidden(client, director_user, director_token, colaborador_token):
    create_resp = _create_auspiciante(client, director_token)
    ausp_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/auspiciantes/{ausp_id}",
        json={"nombre": "Should Fail"},
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_soft_delete_auspiciante(client, director_user, director_token):
    create_resp = _create_auspiciante(client, director_token)
    ausp_id = create_resp.json()["id"]
    response = client.delete(
        f"/api/v1/auspiciantes/{ausp_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 204
    detail = client.get(
        f"/api/v1/auspiciantes/{ausp_id}",
        cookies={"access_token": director_token},
    )
    assert detail.json()["activo"] is False


def test_soft_delete_as_colaborador_forbidden(client, director_user, director_token, colaborador_token):
    create_resp = _create_auspiciante(client, director_token)
    ausp_id = create_resp.json()["id"]
    response = client.delete(
        f"/api/v1/auspiciantes/{ausp_id}",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_assign_auspiciantes_to_boletin(client, director_user, director_token):
    a1 = _create_auspiciante(client, director_token, "Sponsor A")
    a2 = _create_auspiciante(client, director_token, "Sponsor B")
    b = _create_boletin(client, director_token)
    boletin_id = b.json()["id"]
    response = client.put(
        f"/api/v1/boletines/{boletin_id}/auspiciantes",
        json={"auspiciantes_ids": [a1.json()["id"], a2.json()["id"]]},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_boletin_auspiciantes(client, director_user, director_token):
    a1 = _create_auspiciante(client, director_token, "Sponsor X")
    b = _create_boletin(client, director_token)
    boletin_id = b.json()["id"]
    client.put(
        f"/api/v1/boletines/{boletin_id}/auspiciantes",
        json={"auspiciantes_ids": [a1.json()["id"]]},
        cookies={"access_token": director_token},
    )
    response = client.get(
        f"/api/v1/boletines/{boletin_id}/auspiciantes",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nombre"] == "Sponsor X"


def test_update_boletin_auspiciantes_replaces(client, director_user, director_token):
    a1 = _create_auspiciante(client, director_token, "Old Sponsor")
    a2 = _create_auspiciante(client, director_token, "New Sponsor")
    b = _create_boletin(client, director_token)
    boletin_id = b.json()["id"]
    client.put(
        f"/api/v1/boletines/{boletin_id}/auspiciantes",
        json={"auspiciantes_ids": [a1.json()["id"]]},
        cookies={"access_token": director_token},
    )
    response = client.put(
        f"/api/v1/boletines/{boletin_id}/auspiciantes",
        json={"auspiciantes_ids": [a2.json()["id"]]},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nombre"] == "New Sponsor"


def test_unauthenticated_cannot_access_auspiciantes(client):
    response = client.get("/api/v1/auspiciantes")
    assert response.status_code == 401
