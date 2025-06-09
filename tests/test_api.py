# tests/test_api.py
import json
from backend.main import Plan            # sólo para tipado
from uuid import uuid4                   # se usa en el payload

def test_create_and_list_plan(client, mocker):
    """CRUD mínimo + mock de IA (sin tocar la API real)."""
    fake_fb = {
        "riesgos": ["riesgo X"],
        "sugerencias": ["sug Y"],
        "impacto_estimado": {"Obj": 88},
    }
    # Mock OpenAI
    mocker.patch(
        "backend.main.openai.chat.completions.create",
        return_value=mocker.Mock(
            choices=[mocker.Mock(message=mocker.Mock(content=json.dumps(fake_fb)))]
        ),
    )

    # Crear
    payload = {
        "nombre": "Plan test",
        "responsable": "QA",
        "cargo": "Ingeniero",
        "objetivo": "Obj",
        "fecha": "2025-12-31",
        "prioridad": "Media",
        "descripcion": "Test",
    }
    r = client.post("/planes", json=payload)
    assert r.status_code == 201
    plan_id = r.json()["id"]

    # Analizar (IA)
    r2 = client.post(f"/planes/{plan_id}/analyze")
    assert r2.status_code == 200
    assert r2.json()["impacto_estimado"]["Obj"] == 88

    # Listar: el feedback quedó persistido
    planes = client.get("/planes").json()
    primera = next(p for p in planes if p["id"] == plan_id)
    assert primera["feedback"]["riesgos"] == ["riesgo X"]
