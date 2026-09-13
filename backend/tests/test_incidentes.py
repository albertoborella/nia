import uuid
import os
import json
from datetime import date

from app.services.prompt_service import DATA_DIR


def _create_incidente(client, token, overrides=None):
    data = {
        "incidente": "Brote de Salmonella en leche",
        "producto": "Leche entera",
        "patogeno": "Salmonella enteritidis",
        "organismo": "FDA",
        "pais": "Estados Unidos",
        "riesgo": "alto",
        "fecha_inicio": "2026-01-15",
        "fecha_consulta": "2026-01-20",
        "severidad": "alto",
    }
    if overrides:
        data.update(overrides)
    return client.post(
        "/api/v1/incidentes",
        json=data,
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


def test_create_incidente(client, director_user, director_token):
    response = _create_incidente(client, director_token)
    assert response.status_code == 201
    data = response.json()
    assert data["incidente"] == "Brote de Salmonella en leche"
    assert data["riesgo"] == "alto"
    assert data["severidad"] == "alto"
    assert data["creado_por"] == str(director_user.id)
    assert data["estado_verificacion"] == "confirmado"
    assert data["estado_editorial"] == "generado"
    assert "id" in data


def test_create_incidente_as_colaborador_forbidden(client, colaborador_user, colaborador_token):
    response = _create_incidente(client, colaborador_token)
    assert response.status_code == 403


def test_create_incidente_invalid_riesgo(client, director_user, director_token):
    response = _create_incidente(client, director_token, overrides={"riesgo": "invalido"})
    assert response.status_code == 422


def test_create_incidente_invalid_severidad(client, director_user, director_token):
    response = _create_incidente(client, director_token, overrides={"severidad": "invalida"})
    assert response.status_code == 422


def test_list_incidentes(client, director_user, director_token):
    _create_incidente(client, director_token)
    response = client.get(
        "/api/v1/incidentes",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_list_incidentes_filter_pais(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"pais": "Argentina"})
    _create_incidente(client, director_token, overrides={"pais": "Brasil"})
    response = client.get(
        "/api/v1/incidentes?pais=Argentina",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["pais"] == "Argentina" for item in data["items"])


def test_list_incidentes_filter_riesgo(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"riesgo": "alto"})
    _create_incidente(client, director_token, overrides={"riesgo": "bajo"})
    response = client.get(
        "/api/v1/incidentes?riesgo=alto",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["riesgo"] == "alto" for item in data["items"])


def test_list_incidentes_filter_estado_verificacion(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"estado_verificacion": "confirmado"})
    response = client.get(
        "/api/v1/incidentes?estado_verificacion=confirmado",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(item["estado_verificacion"] == "confirmado" for item in data["items"])


def test_get_incidente_detail(client, director_user, director_token):
    create_resp = _create_incidente(client, director_token)
    incidente_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/incidentes/{incidente_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == incidente_id


def test_get_incidente_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/incidentes/{fake_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_update_incidente(client, director_user, director_token):
    create_resp = _create_incidente(client, director_token)
    incidente_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/incidentes/{incidente_id}",
        json={"incidente": "Brote actualizado de Salmonella"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incidente"] == "Brote actualizado de Salmonella"


def test_update_incidente_as_colaborador_forbidden(client, director_user, director_token, colaborador_user, colaborador_token):
    create_resp = _create_incidente(client, director_token)
    incidente_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/incidentes/{incidente_id}",
        json={"incidente": "Should fail"},
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_delete_incidente(client, director_user, director_token):
    create_resp = _create_incidente(client, director_token)
    incidente_id = create_resp.json()["id"]
    response = client.delete(
        f"/api/v1/incidentes/{incidente_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 204
    get_response = client.get(
        f"/api/v1/incidentes/{incidente_id}",
        cookies={"access_token": director_token},
    )
    assert get_response.status_code == 404


def test_delete_incidente_as_colaborador_forbidden(client, director_user, director_token, colaborador_user, colaborador_token):
    create_resp = _create_incidente(client, director_token)
    incidente_id = create_resp.json()["id"]
    response = client.delete(
        f"/api/v1/incidentes/{incidente_id}",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_import_from_stored_response(client, director_user, director_token, db_session):
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]

    prompt_id = str(uuid.uuid4())
    timestamp_dir = "2026-01-01_120000"
    response_dir = os.path.join(DATA_DIR, prompt_id, boletin_id, timestamp_dir)
    os.makedirs(response_dir, exist_ok=True)

    mock_response = [
        {
            "incidente": "Incidente importado",
            "producto": "Producto test",
            "patogeno": "Patogeno test",
            "pais": "Argentina",
            "riesgo": "medio",
            "severidad": "medio",
            "fecha_inicio": "2026-01-10",
            "fecha_consulta": "2026-01-15",
        }
    ]
    with open(os.path.join(response_dir, "response.json"), "w") as f:
        json.dump(mock_response, f)

    response = client.post(
        f"/api/v1/incidentes/importar?prompt_id={prompt_id}&boletin_id={boletin_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_imported"] == 1
    assert len(data["errors"]) == 0

    list_response = client.get(
        f"/api/v1/incidentes?boletin_asignado={boletin_id}",
        cookies={"access_token": director_token},
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    import shutil
    shutil.rmtree(os.path.join(DATA_DIR, prompt_id), ignore_errors=True)


def test_import_from_stored_response_not_found(client, director_user, director_token):
    fake_prompt_id = str(uuid.uuid4())
    fake_boletin_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/incidentes/importar?prompt_id={fake_prompt_id}&boletin_id={fake_boletin_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_import_from_stored_response_as_colaborador_forbidden(client, colaborador_user, colaborador_token):
    response = client.post(
        f"/api/v1/incidentes/importar?prompt_id={uuid.uuid4()}&boletin_id={uuid.uuid4()}",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_generar_articulo(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"boletin_asignado": None})
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]

    for i in range(3):
        _create_incidente(client, director_token, overrides={
            "boletin_asignado": boletin_id,
            "incidente": f"Incidente {i+1}",
        })

    response = client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incidentes_incluidos"] == 3
    assert data["version"] == 1
    assert "# Incidentes de Inocuidad Alimentaria" in data["articulo_markdown"]

    import shutil
    articulos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "articulos", boletin_id)
    shutil.rmtree(articulos_dir, ignore_errors=True)


def test_generar_articulo_no_incidents(client, director_user, director_token):
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]
    response = client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 422


def test_generar_articulo_as_colaborador_forbidden(client, director_user, director_token, colaborador_user, colaborador_token):
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]
    response = client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_get_articulo(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"boletin_asignado": None})
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]

    _create_incidente(client, director_token, overrides={"boletin_asignado": boletin_id})

    client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": director_token},
    )

    response = client.get(
        f"/api/v1/incidentes/{boletin_id}/articulo",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "articulo_markdown" in data
    assert data["incidentes_incluidos"] == 1

    import shutil
    articulos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "articulos", boletin_id)
    shutil.rmtree(articulos_dir, ignore_errors=True)


def test_get_articulo_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/incidentes/{fake_id}/articulo",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_update_articulo(client, director_user, director_token):
    _create_incidente(client, director_token, overrides={"boletin_asignado": None})
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]

    _create_incidente(client, director_token, overrides={"boletin_asignado": boletin_id})

    client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": director_token},
    )

    response = client.put(
        f"/api/v1/incidentes/{boletin_id}/articulo",
        json={
            "articulo_markdown": "# Articulo editado\n\nContenido editado.",
            "version": 2,
        },
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 2
    assert data["articulo_markdown"] == "# Articulo editado\n\nContenido editado."

    import shutil
    articulos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "articulos", boletin_id)
    shutil.rmtree(articulos_dir, ignore_errors=True)


def test_update_articulo_as_colaborador_forbidden(client, director_user, director_token, colaborador_user, colaborador_token):
    _create_incidente(client, director_token, overrides={"boletin_asignado": None})
    boletin_resp = _create_boletin(client, director_token)
    boletin_id = boletin_resp.json()["id"]

    _create_incidente(client, director_token, overrides={"boletin_asignado": boletin_id})

    client.post(
        f"/api/v1/incidentes/{boletin_id}/generar-articulo",
        cookies={"access_token": director_token},
    )

    response = client.put(
        f"/api/v1/incidentes/{boletin_id}/articulo",
        json={
            "articulo_markdown": "# Should fail",
            "version": 2,
        },
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403

    import shutil
    articulos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "articulos", boletin_id)
    shutil.rmtree(articulos_dir, ignore_errors=True)


def test_unauthenticated_cannot_access(client):
    response = client.get("/api/v1/incidentes")
    assert response.status_code == 401


def test_list_incidentes_with_pagination(client, director_user, director_token):
    for i in range(5):
        _create_incidente(client, director_token, overrides={"incidente": f"Incidente {i+1}"})
    response = client.get(
        "/api/v1/incidentes?page=1&limit=2",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2
