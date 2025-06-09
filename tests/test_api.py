 # ■ tests/test_api.py
from uuid import uuid4
import json

def test_create_and_list_plan(client, mocker):
     """CRUD mínimo + mock de IA (sin tocar la API real)."""
     fake_fb = {
         "riesgos": ["riesgo X"],
         "sugerencias": ["sug Y"],
         "impacto_estimado": {"Obj": 88},
     }
     # Mock OpenAI
     mocker.patch(
        "main.openai.ChatCompletion.create",
         return_value=mocker.Mock(
             choices=[mocker.Mock(message=mocker.Mock(content=json.dumps(fake_fb)))]
         ),
     )