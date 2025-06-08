# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import Column, JSON
from typing import List, Dict, Annotated
from uuid import uuid4
from pydantic import constr
import os, json, openai
from dotenv import load_dotenv

# --- entorno ------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY no definida en .env")

# --- modelos ------------------------------------------------------------
DateStr = Annotated[
    str,
    constr(pattern=r"^\d{4}-\d{2}-\d{2}$", strip_whitespace=True, min_length=10, max_length=10),
]

class PlanBase(SQLModel):
    nombre: str
    responsable: str
    cargo: str
    objetivo: str
    fecha: DateStr
    prioridad: str
    descripcion: str

class Plan(PlanBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    acciones: List[Dict] = Field(sa_column=Column(JSON), default_factory=list)
    feedback: Dict | None = Field(sa_column=Column(JSON), default=None)

# --- base de datos ------------------------------------------------------
DATABASE_URL = "sqlite:///./smartplans.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

# --- app ----------------------------------------------------------------
app = FastAPI(title="SmartPlans EAFIT API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/ping")
def ping() -> Dict[str, str]:
    return {"ping": "pong"}

# --- CRUD ---------------------------------------------------------------
@app.get("/planes", response_model=List[Plan])
def listar_planes():
    with Session(engine) as s:
        return s.exec(select(Plan)).all()

@app.post("/planes", response_model=Plan, status_code=201)
def crear_plan(plan: PlanBase):
    nuevo = Plan(**plan.dict())
    with Session(engine) as s:
        s.add(nuevo)
        s.commit()
        s.refresh(nuevo)
        return nuevo

@app.get("/planes/{plan_id}", response_model=Plan)
def obtener_plan(plan_id: str):
    with Session(engine) as s:
        plan = s.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        return plan

@app.put("/planes/{plan_id}", response_model=Plan)
def actualizar_plan(plan_id: str, datos: PlanBase):
    with Session(engine) as s:
        plan = s.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        for k, v in datos.dict().items():
            setattr(plan, k, v)
        s.commit()
        s.refresh(plan)
        return plan

@app.delete("/planes/{plan_id}", status_code=204)
def borrar_plan(plan_id: str):
    with Session(engine) as s:
        plan = s.get(Plan, plan_id)
        if plan:
            s.delete(plan)
            s.commit()
    return

# --- IA -----------------------------------------------------------------
PROMPT_SYSTEM = "Responde solo en JSON válido"

def generar_feedback(plan: Plan) -> Dict:
    """Llama a GPT-4o y devuelve dict con riesgos, sugerencias e impacto (%)"""
    prompt_user = f"""
Eres un consultor senior de estrategia. Analiza el siguiente plan y responde
**en JSON estricto** con las claves EXACTAS:

"riesgos": lista de 1-3 frases breves.
"sugerencias": lista de 1-3 frases breves.
"impacto_estimado": objeto con una sola clave (exactamente el objetivo que
ves abajo) y su valor EN PORCENTAJE (0-100).

PLAN:
Nombre: {plan.nombre}
Responsable: {plan.responsable}  |  Cargo: {plan.cargo}
Objetivo: {plan.objetivo}
Fecha meta: {plan.fecha}
Prioridad: {plan.prioridad}
Descripción: {plan.descripcion}
Acciones: {plan.acciones}
"""
    chat = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMPT_SYSTEM},
            {"role": "user",   "content": prompt_user},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return json.loads(chat.choices[0].message.content)

@app.post("/planes/{plan_id}/analyze", response_model=Dict)
def analizar_plan(plan_id: str):
    with Session(engine) as s:
        plan = s.get(Plan, plan_id)
        if not plan:
            raise HTTPException(404, "Plan no encontrado")
        if plan.feedback:
            return plan.feedback

        try:
            feedback = generar_feedback(plan)
        except Exception as e:
            raise HTTPException(502, f"Error externo IA: {e}")

        plan.feedback = feedback
        s.commit()
        return feedback
