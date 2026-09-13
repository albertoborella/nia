import uuid
from datetime import date


def _create_boletin(client, token):
    return client.post(
        "/api/v1/boletines",
        json={
            "nombre": "Boletin Test",
            "periodo_inicio": "2026-01-01",
            "periodo_fin": "2026-01-31",
            "fecha_publicacion_estimada": "2026-02-05",
        },
        cookies={"access_token": token},
    )


def _complete_all_sections(client, boletin_id, token, db_session):
    tipos = [
        "editorial", "incidentes", "notas_colaboradores",
        "tabla_incidentes", "auspiciantes", "indice",
    ]
    for tipo in tipos:
        client.post(
            f"/api/v1/boletines/{boletin_id}/completar-seccion",
            json={"tipo": tipo},
            cookies={"access_token": token},
        )


def test_create_boletin_with_sections(client, director_user, director_token):
    response = _create_boletin(client, director_token)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Boletin Test"
    assert data["estado"] == "borrador"
    assert len(data["secciones"]) == 6
    tipos = [s["tipo"] for s in data["secciones"]]
    assert tipos == [
        "editorial", "incidentes", "notas_colaboradores",
        "tabla_incidentes", "auspiciantes", "indice",
    ]
    assert all(s["estado"] == "pendiente" for s in data["secciones"])
    assert data["creado_por"] == str(director_user.id)


def test_create_boletin_as_colaborador_forbidden(client, colaborador_user, colaborador_token):
    response = _create_boletin(client, colaborador_token)
    assert response.status_code == 403


def test_list_boletines(client, director_user, director_token):
    _create_boletin(client, director_token)
    response = client.get(
        "/api/v1/boletines",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_list_boletines_filter_estado(client, director_user, director_token):
    _create_boletin(client, director_token)
    response = client.get(
        "/api/v1/boletines?estado=borrador",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_get_boletin_detail(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/boletines/{boletin_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == boletin_id
    assert len(data["secciones"]) == 6


def test_get_boletin_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/boletines/{fake_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_update_boletin_borrador(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/boletines/{boletin_id}",
        json={"nombre": "Boletin Actualizado"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Boletin Actualizado"


def test_update_boletin_not_borrador_conflict(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    _complete_all_sections(client, boletin_id, director_token, None)
    client.post(
        f"/api/v1/boletines/{boletin_id}/cerrar",
        cookies={"access_token": director_token},
    )
    response = client.put(
        f"/api/v1/boletines/{boletin_id}",
        json={"nombre": "Should Fail"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 409


def test_complete_section(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/completar-seccion",
        json={"tipo": "editorial"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tipo"] == "editorial"
    assert data["estado"] == "completada"
    assert data["completado_por"] == str(director_user.id)
    assert data["fecha_completado"] is not None


def test_complete_section_not_found(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/completar-seccion",
        json={"tipo": "nonexistent"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_complete_section_out_of_order(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/completar-seccion",
        json={"tipo": "indice"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["tipo"] == "indice"


def test_close_boletin_all_complete(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    _complete_all_sections(client, boletin_id, director_token, None)
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/cerrar",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "cerrado"
    assert data["fecha_cierre"] is not None


def test_close_boletin_incomplete_sections(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    client.post(
        f"/api/v1/boletines/{boletin_id}/completar-seccion",
        json={"tipo": "editorial"},
        cookies={"access_token": director_token},
    )
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/cerrar",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 409


def test_list_secciones(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/boletines/{boletin_id}/secciones",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6


def test_get_seccion_by_tipo(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/boletines/{boletin_id}/secciones/editorial",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["tipo"] == "editorial"


def test_update_seccion_content(client, director_user, director_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/boletines/{boletin_id}/secciones/editorial",
        json={"contenido": {"texto": "Editorial content here"}},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["contenido"] == {"texto": "Editorial content here"}


def test_colaborador_can_complete_sections(client, director_user, director_token, colaborador_user, colaborador_token):
    create_resp = _create_boletin(client, director_token)
    boletin_id = create_resp.json()["id"]
    response = client.post(
        f"/api/v1/boletines/{boletin_id}/completar-seccion",
        json={"tipo": "editorial"},
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 200
    assert response.json()["completado_por"] == str(colaborador_user.id)


def test_unauthenticated_cannot_access(client):
    response = client.get("/api/v1/boletines")
    assert response.status_code == 401
