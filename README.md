# SmartPlans API

![CI](https://github.com/R4D4M4NTHYS24/smartPlansBackend/actions/workflows/ci.yml/badge.svg)

Esta API expone los endpoints de SmartPlans (FastAPI + SQLite + OpenAI).

---

## Getting Started

### Prerrequisitos

- Python ≥ 3.11
- Clona este repo y copia tu `.env`:
  ```bash
  git clone https://github.com/R4D4M4NTHYS24/smartPlansBackend.git
  cd smartPlansBackend/backend
  cp .env.example .env
  # Edita .env y pon tu OPENAI_API_KEY
  ```

## Instalación

python -m pip install --upgrade pip
pip install -r requirements.txt

## Ejecutar la API

uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Endpoints principales

Método Ruta Descripción
GET /ping Comprueba que la API está viva.
GET /planes Lista todos los planes.
POST /planes Crea un nuevo plan.
GET /planes/{plan_id} Obtiene un plan por su ID.
PUT /planes/{plan_id} Actualiza un plan existente.
DELETE /planes/{plan_id} Borra un plan.
POST /planes/{plan_id}/analyze Genera feedback IA para un plan.

## Ejecutar tests

cd backend
pytest -q
