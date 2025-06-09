import os, sys, pathlib, pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# --- 0. API-key dummy para que main.py no pete ---
os.environ.setdefault("OPENAI_API_KEY", "sk-test")

# --- 1. Añade la raíz del repo al sys.path ---
ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

import backend.main as backend_main      # ya existe todo (Plan, rutas…)

# --- 2. Motor SQLite en memoria PERO compartido ---
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,       # ⚠️ clave para compartir la BD
    echo=False,
)

SQLModel.metadata.create_all(test_engine)   # crea tabla plan & co.

# --- 3. Dependency override para usar nuestra BD ---
def _test_session():
    with Session(test_engine) as s:
        yield s

backend_main.get_session = _test_session   # cambia la función
backend_main.engine = test_engine          # (opcional, por coherencia)

@pytest.fixture(scope="session")
def client():
    return TestClient(backend_main.app)
