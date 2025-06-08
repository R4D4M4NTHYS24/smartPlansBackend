# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import Column, JSON
from typing import List, Optional, Dict
from typing_extensions import Annotated
from uuid import uuid4
from pydantic import constr

# 1. MODELOS (con JSON en SQLite)

DateStr = Annotated[
    str,
    constr(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        strip_whitespace=True,
        min_length=10,
        max_length=10,
    ),
]

class PlanBase(SQLModel):
    nombre: Annotated[str, Field(min_length=1)]
    responsable: Annotated[str, Field(min_length=1)]
    objetivo: Annotated[str, Field(min_length=1)]
    fecha: DateStr        # ISO date "YYYY-MM-DD"
    prioridad: Annotated[str, Field(min_length=1)]
    descripcion: Annotated[str, Field(min_length=1)]

class Plan(PlanBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    acciones: List[Dict] = Field(sa_column=Column(JSON), default_factory=list)
    feedback: Optional[Dict] = Field(sa_column=Column(JSON), default=None)

# ------------------------------
# 2. BASE DE DATOS (SQLite)
# ------------------------------
DATABASE_URL = "sqlite:///./smartplans.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# ------------------------------
# 3. API
# ------------------------------
app = FastAPI(title="SmartPlans EAFIT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/planes", response_model=List[Plan])
def listar_planes():
    with Session(engine) as session:
        return session.exec(select(Plan)).all()

@app.post("/planes", response_model=Plan, status_code=201)
def crear_plan(plan: PlanBase):
    # Pydantic validará todos los campos y el formato de 'fecha'
    nueva = Plan(**plan.dict())
    with Session(engine) as session:
        session.add(nueva)
        session.commit()
        session.refresh(nueva)
        return nueva

@app.get("/planes/{plan_id}", response_model=Plan)
def obtener_plan(plan_id: str):
    with Session(engine) as session:
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        return plan

@app.put("/planes/{plan_id}", response_model=Plan)
def actualizar_plan(plan_id: str, datos: PlanBase):
    with Session(engine) as session:
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        for campo, val in datos.dict().items():
            setattr(plan, campo, val)
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return plan

@app.delete("/planes/{plan_id}", status_code=204)
def borrar_plan(plan_id: str):
    with Session(engine) as session:
        plan = session.get(Plan, plan_id)
        if plan:
            session.delete(plan)
            session.commit()
    return

@app.post("/planes/{plan_id}/analyze", response_model=Dict)
def analizar_plan(plan_id: str):
    with Session(engine) as session:
        plan = session.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        # → Aquí integras tu llamada real a OpenAI; por ahora, feedback de ejemplo:
        feedback = {
            "riesgos": ["Plazo muy ajustado en alguna acción"],
            "sugerencias": ["Considera asignar otro responsable a la acción X"],
            "impacto_estimado": {plan.objetivo: len(plan.acciones)}
        }
        plan.feedback = feedback
        session.add(plan)
        session.commit()
        return feedback

# Para arrancar:
# cd backend
# uvicorn main:app --reload --port 8000
