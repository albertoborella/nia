import uuid
from io import BytesIO

from app.services.nota_service import UPLOAD_DIR


def _create_nota(client, token, titulo="Test Note", autor="Test Author", filename="test.pdf", content=b"fake pdf content"):
    return client.post(
        "/api/v1/notas",
        data={
            "titulo": titulo,
            "autor": autor,
        },
        files={"archivo": (filename, BytesIO(content), "application/pdf")},
        cookies={"access_token": token},
    )


def test_create_nota_pdf(client, director_user, director_token):
    response = _create_nota(client, director_token)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "Test Note"
    assert data["autor"] == "Test Author"
    assert data["estado"] == "pendiente"
    assert data["archivo_tipo"] == "pdf"
    assert data["colaborador_id"] == str(director_user.id)
    assert data["fecha_recepcion"] is not None


def test_create_nota_docx(client, director_user, director_token):
    response = client.post(
        "/api/v1/notas",
        data={
            "titulo": "DOCX Note",
            "autor": "Author",
        },
        files={"archivo": ("note.docx", BytesIO(b"fake docx content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 201
    assert response.json()["archivo_tipo"] == "docx"


def test_create_nota_invalid_file_type(client, director_user, director_token):
    response = client.post(
        "/api/v1/notas",
        data={
            "titulo": "Bad File",
            "autor": "Author",
        },
        files={"archivo": ("malware.exe", BytesIO(b"bad content"), "application/octet-stream")},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 422


def test_create_nota_txt_rejected(client, director_user, director_token):
    response = client.post(
        "/api/v1/notas",
        data={
            "titulo": "Text File",
            "autor": "Author",
        },
        files={"archivo": ("notes.txt", BytesIO(b"text"), "text/plain")},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 422


def test_list_notas(client, director_user, director_token):
    _create_nota(client, director_token)
    response = client.get(
        "/api/v1/notas",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_list_notas_filter_estado(client, director_user, director_token):
    _create_nota(client, director_token)
    response = client.get(
        "/api/v1/notas?estado=pendiente",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_list_notas_filter_autor(client, director_user, director_token):
    _create_nota(client, director_token, autor="Juan Perez")
    _create_nota(client, director_token, autor="Maria Lopez")
    response = client.get(
        "/api/v1/notas?autor=Juan",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["autor"] == "Juan Perez"


def test_list_notas_filter_tema(client, director_user, director_token):
    _create_nota(client, director_token)
    client.post(
        "/api/v1/notas",
        data={
            "titulo": "Bacteria Note",
            "autor": "Author",
            "tema": "bacterias",
        },
        files={"archivo": ("bacteria.pdf", BytesIO(b"bacteria"), "application/pdf")},
        cookies={"access_token": director_token},
    )
    response = client.get(
        "/api/v1/notas?tema=bacterias",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_nota_detail(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/notas/{nota_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["id"] == nota_id
    assert response.json()["titulo"] == "Test Note"


def test_get_nota_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/notas/{fake_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_update_nota_metadata(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/notas/{nota_id}",
        json={"titulo": "Updated Title", "autor": "Updated Author"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Updated Title"
    assert data["autor"] == "Updated Author"


def test_delete_nota_director(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    file_url = create_resp.json()["archivo_url"]
    response = client.delete(
        f"/api/v1/notas/{nota_id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted"

    from pathlib import Path
    assert not Path(file_url).exists()

    get_resp = client.get(
        f"/api/v1/notas/{nota_id}",
        cookies={"access_token": director_token},
    )
    assert get_resp.status_code == 404


def test_delete_nota_colaborador_forbidden(client, colaborador_user, colaborador_token):
    create_resp = _create_nota(client, colaborador_token)
    nota_id = create_resp.json()["id"]
    response = client.delete(
        f"/api/v1/notas/{nota_id}",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_change_estado_pendiente_to_aprobada(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "aprobada"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "aprobada"
    assert data["fecha_revision"] is not None
    assert data["revisado_por"] == str(director_user.id)


def test_change_estado_aprobada_to_archivada(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]

    client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "aprobada"},
        cookies={"access_token": director_token},
    )

    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "archivada", "observaciones": "Archiving note"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "archivada"
    assert data["observaciones"] == "Archiving note"


def test_change_estado_pendiente_to_archivada(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "archivada"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "archivada"


def test_invalid_state_transition(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]

    client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "aprobada"},
        cookies={"access_token": director_token},
    )

    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "pendiente"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 409


def test_invalid_state_value(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "invalid_state"},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 422


def test_download_nota_file(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    response = client.get(
        f"/api/v1/notas/{nota_id}/descarga",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_download_nota_not_found(client, director_user, director_token):
    fake_id = str(uuid.uuid4())
    response = client.get(
        f"/api/v1/notas/{fake_id}/descarga",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 404


def test_unauthenticated_cannot_access_notas(client):
    response = client.get("/api/v1/notas")
    assert response.status_code == 401


def test_unauthenticated_cannot_create_nota(client):
    response = client.post(
        "/api/v1/notas",
        data={"titulo": "Test", "autor": "Author"},
        files={"archivo": ("test.pdf", BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 401


def test_change_estado_with_boletin_asignado(client, director_user, director_token):
    create_resp = _create_nota(client, director_token)
    nota_id = create_resp.json()["id"]
    fake_boletin_id = str(uuid.uuid4())
    response = client.put(
        f"/api/v1/notas/{nota_id}/estado",
        json={"estado": "aprobada", "boletin_asignado": fake_boletin_id},
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    assert response.json()["boletin_asignado"] == fake_boletin_id
