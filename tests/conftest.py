 # ■ tests/conftest.py
import os, sys, pathlib, pytest, json
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from main import app, get_session
 
os.environ.setdefault("OPENAI_API_KEY", "sk-test")

 
ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session")
def test_db():
     engine = create_engine("sqlite:///:memory:", echo=False)
     SQLModel.metadata.create_all(engine)
     yield engine
     engine.dispose()

@pytest.fixture(scope="session")
def client(test_db):
     def _get_test_session():
         with Session(test_db) as s:
             yield s

     app.dependency_overrides[get_session] = _get_test_session
     yield TestClient(app)
     app.dependency_overrides.clear()
