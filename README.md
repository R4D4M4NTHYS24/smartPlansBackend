# SmartPlans API

This API exposes SmartPlans endpoints (FastAPI + SQLite + OpenAI).

## Getting Started

### Prerequisites
- Python >= 3.11 (recommended: 3.12)

### Clone the repository

git clone https://github.com/R4D4M4NTHYS24/smartPlansBackend.git
cd smartPlansBackend

## Create and activate a virtual environment

### Windows (Git Bash):
py -3.12 -m venv .venv
source .venv/Scripts/activate

## Windows (PowerShell):
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

## macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

## Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

## Environment variables
### Create a .env file at the repo root:
OPENAI_API_KEY=sk-...

## Run the API
### python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Verify
Health check: http://localhost:8000/ping
Swagger UI: http://localhost:8000/docs

| Method | Route                       | Description                      |
| ------ | --------------------------- | -------------------------------- |
| GET    | `/ping`                     | Check that the API is alive.     |
| GET    | `/planes`                   | List all plans.                  |
| POST   | `/planes`                   | Create a new plan.               |
| GET    | `/planes/{plan_id}`         | Get a plan by ID.                |
| PUT    | `/planes/{plan_id}`         | Update an existing plan.         |
| DELETE | `/planes/{plan_id}`         | Delete a plan.                   |
| POST   | `/planes/{plan_id}/analyze` | Generate AI feedback for a plan. |

## Run tests
pytest -q
