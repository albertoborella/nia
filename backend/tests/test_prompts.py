import os
import json
import shutil

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def cleanup_responses():
    yield
    responses_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "responses")
    if os.path.exists(responses_dir):
        shutil.rmtree(responses_dir)


class TestPromptCRUD:
    def test_create_prompt(self, client: TestClient, director_token: str):
        response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta Incidentes",
                "descripcion": "Prompt para buscar incidentes de inocuidad",
                "template": "Busca incidentes de {{producto}} en {{pais}} durante {{periodo}}",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Consulta Incidentes"
        assert data["tipo"] == "consulta_incidentes"
        assert data["activo"] is True

    def test_create_prompt_colaborador_forbidden(self, client: TestClient, colaborador_token: str):
        response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Test",
                "template": "Test template",
                "tipo": "otro"
            },
            cookies={"access_token": colaborador_token}
        )
        assert response.status_code == 403

    def test_list_prompts(self, client: TestClient, director_token: str):
        client.post(
            "/api/v1/prompts",
            json={"nombre": "Prompt 1", "template": "Template 1", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        client.post(
            "/api/v1/prompts",
            json={"nombre": "Prompt 2", "template": "Template 2", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        
        response = client.get(
            "/api/v1/prompts",
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_prompts_filter_tipo(self, client: TestClient, director_token: str):
        client.post(
            "/api/v1/prompts",
            json={"nombre": "Prompt 1", "template": "Template 1", "tipo": "consulta_incidentes"},
            cookies={"access_token": director_token}
        )
        client.post(
            "/api/v1/prompts",
            json={"nombre": "Prompt 2", "template": "Template 2", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        
        response = client.get(
            "/api/v1/prompts?tipo=consulta_incidentes",
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["tipo"] == "consulta_incidentes"

    def test_get_prompt(self, client: TestClient, director_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={"nombre": "Test Prompt", "template": "Template", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.get(
            f"/api/v1/prompts/{prompt_id}",
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Test Prompt"

    def test_get_prompt_not_found(self, client: TestClient, director_token: str):
        response = client.get(
            "/api/v1/prompts/00000000-0000-0000-0000-000000000000",
            cookies={"access_token": director_token}
        )
        assert response.status_code == 404

    def test_update_prompt(self, client: TestClient, director_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={"nombre": "Old Name", "template": "Template", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/v1/prompts/{prompt_id}",
            json={"nombre": "New Name"},
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "New Name"

    def test_delete_prompt(self, client: TestClient, director_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={"nombre": "To Delete", "template": "Template", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/v1/prompts/{prompt_id}",
            cookies={"access_token": director_token}
        )
        assert response.status_code == 204
        
        get_response = client.get(
            f"/api/v1/prompts/{prompt_id}",
            cookies={"access_token": director_token}
        )
        assert get_response.status_code == 404


class TestPromptRender:
    def test_render_prompt(self, client: TestClient, director_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta",
                "template": "Busca incidentes de {{producto}} en {{pais}}",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/v1/prompts/{prompt_id}/render",
            json={"variables": {"producto": "leche", "pais": "Argentina"}},
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["rendered_text"] == "Busca incidentes de leche en Argentina"
        assert data["variables"]["producto"] == "leche"

    def test_render_prompt_missing_variables(self, client: TestClient, director_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta",
                "template": "Busca {{producto}} en {{pais}}",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/v1/prompts/{prompt_id}/render",
            json={"variables": {"producto": "leche"}},
            cookies={"access_token": director_token}
        )
        assert response.status_code == 422
        assert "Missing required variables" in response.json()["detail"]["message"]


class TestUploadResponse:
    def test_upload_valid_response(self, client: TestClient, director_token: str):
        prompt_response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta Incidentes",
                "template": "Busca incidentes de {{producto}}",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        prompt_id = prompt_response.json()["id"]
        
        boletin_response = client.post(
            "/api/v1/boletines",
            json={
                "nombre": "Boletin Test",
                "periodo_inicio": "2026-03-01",
                "periodo_fin": "2026-03-31"
            },
            cookies={"access_token": director_token}
        )
        boletin_id = boletin_response.json()["id"]
        
        response = client.post(
            f"/api/v1/prompts/{prompt_id}/upload-response?boletin_id={boletin_id}",
            json={
                "incidentes": [
                    {
                        "incidente": "Brote de Salmonella",
                        "producto": "Leche",
                        "patogeno": "Salmonella",
                        "riesgo": "alto"
                    }
                ],
                "prompt_rendered": "Busca incidentes de leche"
            },
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_received"] == 1
        assert data["total_stored"] == 1
        assert len(data["errors"]) == 0

    def test_upload_with_invalid_data(self, client: TestClient, director_token: str):
        prompt_response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta",
                "template": "Template",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        prompt_id = prompt_response.json()["id"]
        
        boletin_response = client.post(
            "/api/v1/boletines",
            json={
                "nombre": "Boletin Test",
                "periodo_inicio": "2026-03-01",
                "periodo_fin": "2026-03-31"
            },
            cookies={"access_token": director_token}
        )
        boletin_id = boletin_response.json()["id"]
        
        response = client.post(
            f"/api/v1/prompts/{prompt_id}/upload-response?boletin_id={boletin_id}",
            json={
                "incidentes": [
                    {"incidente": "Valid Incident"},
                    {},
                    {"incidente": "", "riesgo": "invalido"}
                ]
            },
            cookies={"access_token": director_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_received"] == 3
        assert data["total_stored"] == 1
        assert len(data["errors"]) == 2

    def test_upload_creates_files(self, client: TestClient, director_token: str):
        prompt_response = client.post(
            "/api/v1/prompts",
            json={
                "nombre": "Consulta",
                "template": "Template {{var}}",
                "tipo": "consulta_incidentes"
            },
            cookies={"access_token": director_token}
        )
        prompt_id = prompt_response.json()["id"]
        
        boletin_response = client.post(
            "/api/v1/boletines",
            json={
                "nombre": "Boletin Test",
                "periodo_inicio": "2026-03-01",
                "periodo_fin": "2026-03-31"
            },
            cookies={"access_token": director_token}
        )
        boletin_id = boletin_response.json()["id"]
        
        client.post(
            f"/api/v1/prompts/{prompt_id}/upload-response?boletin_id={boletin_id}",
            json={"incidentes": [{"incidente": "Test"}], "prompt_rendered": "Template test value"},
            cookies={"access_token": director_token}
        )
        
        responses_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "responses")
        prompt_dir = os.path.join(responses_dir, prompt_id)
        assert os.path.exists(prompt_dir)
        
        boletin_dir = os.path.join(prompt_dir, boletin_id)
        assert os.path.exists(boletin_dir)
        
        timestamp_dirs = os.listdir(boletin_dir)
        assert len(timestamp_dirs) == 1
        
        response_dir = os.path.join(boletin_dir, timestamp_dirs[0])
        assert os.path.exists(os.path.join(response_dir, "prompt_rendered.txt"))
        assert os.path.exists(os.path.join(response_dir, "response.json"))


class TestPromptAuth:
    def test_unauthorized_access(self, client: TestClient):
        response = client.get("/api/v1/prompts")
        assert response.status_code == 401

    def test_colaborador_can_list(self, client: TestClient, colaborador_token: str):
        response = client.get(
            "/api/v1/prompts",
            cookies={"access_token": colaborador_token}
        )
        assert response.status_code == 200

    def test_colaborador_can_render(self, client: TestClient, director_token: str, colaborador_token: str):
        create_response = client.post(
            "/api/v1/prompts",
            json={"nombre": "Test", "template": "Template", "tipo": "otro"},
            cookies={"access_token": director_token}
        )
        prompt_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/v1/prompts/{prompt_id}/render",
            json={"variables": {}},
            cookies={"access_token": colaborador_token}
        )
        assert response.status_code == 200
