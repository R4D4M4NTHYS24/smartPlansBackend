# backend/tests/conftest.py
import os, sys, pathlib, pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

# 1️⃣ pon una API-key dummy para que main.py no rompa
os.environ["OPENAI_API_KEY"] = "sk-test"

# 2️⃣ mete la carpeta padre (la que contiene backend/) en sys.path
ROOT = pathlib.Path(__file__).resolve().parents[1]  # va a …/backend
sys.path.insert(0, str(ROOT))

from backend.main import app, get_session

# 3️⃣ monta un SQLite en memoria y crea tablas
engine = create_engine("sqlite:///:memory:", echo=False)
SQLModel.metadata.create_all(engine)

@pytest.fixture(scope="session")
def client():
    # factory para que Depend(get_session) use este engine
    def _get_test_session():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = _get_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()
