import uuid

from sqlmodel import select

from app.models.log_auditoria import LogAuditoria
from app.services.auditoria_service import log_event


def test_log_event(db_session, director_user):
    log_event(
        db_session,
        usuario_id=director_user.id,
        accion="create",
        entidad_tipo="boletin",
        entidad_id=uuid.uuid4(),
        detalles={"nombre": "Test Boletin"},
        ip="127.0.0.1",
    )
    logs = db_session.exec(select(LogAuditoria)).all()
    assert len(logs) == 1
    assert logs[0].accion == "create"
    assert logs[0].entidad_tipo == "boletin"
    assert logs[0].ip == "127.0.0.1"


def test_list_logs_endpoint(client, director_user, director_token, db_session):
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="boletin")
    response = client.get(
        "/api/v1/auditoria",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_list_logs_as_colaborador_forbidden(client, colaborador_token):
    response = client.get(
        "/api/v1/auditoria",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_list_logs_filter_by_usuario(client, director_user, director_token, colaborador_user, db_session):
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="boletin")
    log_event(db_session, usuario_id=colaborador_user.id, accion="update", entidad_tipo="nota")
    response = client.get(
        f"/api/v1/auditoria?usuario_id={colaborador_user.id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["usuario_id"] == str(colaborador_user.id)


def test_list_logs_filter_by_entidad_tipo(client, director_user, director_token, db_session):
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="boletin")
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="incidente")
    response = client.get(
        "/api/v1/auditoria?entidad_tipo=boletin",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["entidad_tipo"] == "boletin"


def test_get_logs_by_usuario_endpoint(client, director_user, director_token, colaborador_user, db_session):
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="boletin")
    log_event(db_session, usuario_id=colaborador_user.id, accion="update", entidad_tipo="nota")
    response = client.get(
        f"/api/v1/auditoria/usuario/{colaborador_user.id}",
        cookies={"access_token": director_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["usuario_id"] == str(colaborador_user.id)


def test_get_logs_by_usuario_as_colaborador_forbidden(client, colaborador_token, director_user, db_session):
    log_event(db_session, usuario_id=director_user.id, accion="create", entidad_tipo="nota")
    response = client.get(
        f"/api/v1/auditoria/usuario/{director_user.id}",
        cookies={"access_token": colaborador_token},
    )
    assert response.status_code == 403


def test_unauthenticated_cannot_access_auditoria(client):
    response = client.get("/api/v1/auditoria")
    assert response.status_code == 401
