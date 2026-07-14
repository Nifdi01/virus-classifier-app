# Virus Classifier App

A full-stack application for classifying viral nucleotide sequences (focused on influenza labels) using multiple ML backends:

- **HyenaDNA** deep-learning model
- **Scikit-learn baselines** (Logistic Regression, Random Forest, XGBoost)

The system includes:

- A **FastAPI** inference API
- A **Celery + Redis** background queue for batch jobs
- A **React + Vite** frontend for submitting sequences and viewing job status

---

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development](#local-development)
- [API Reference](#api-reference)
- [Input Validation Rules](#input-validation-rules)
- [Available Models](#available-models)

---

## Architecture

```text
Frontend (React/Vite)
        |
        v
FastAPI API (app/main.py)
   |                 |
   | sync predict    | async batch
   v                 v
Model Registry    Celery Worker (worker.py / app/tasks.py)
   |                 |
   +--------> Redis broker/result backend
```

---

## Project Structure

```text
.
├── app/                  # FastAPI app, routes, schemas, inference, model registry
├── frontend/             # React + TypeScript UI
├── ml/
│   ├── models/           # Trained model artifacts (hyenadna + baselines)
│   ├── src/              # Model wrapper/loading code
│   └── data/             # Example/training data assets
├── worker.py             # Celery app configuration
├── docker-compose.yml    # Multi-service local stack
├── Dockerfile            # API/worker Python image
└── requirements.txt      # Python dependencies
```

---

## Requirements

### For Docker workflow

- Docker
- Docker Compose

### For local (non-Docker) workflow

- Python 3.14 (project Docker image uses `python:3.14-slim`)
- Node.js + npm (for frontend)
- Redis (local broker/backend for Celery)

---

## Quick Start (Docker)

From `/home/runner/work/virus-classifier-app/virus-classifier-app`:

```bash
docker compose up --build
```

Services:

- API: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Redis: `localhost:6379`
- Celery worker runs in the `worker` service

To stop:

```bash
docker compose down
```

---

## Local Development

### 1) Backend API + worker setup

```bash
cd /home/runner/work/virus-classifier-app/virus-classifier-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start Redis (example):

```bash
redis-server
```

Run API:

```bash
fastapi run app/main.py --host 0.0.0.0 --port 8000
```

Run worker (separate terminal):

```bash
celery -A worker.celery_app worker --loglevel=info --concurrency=1
```

### 2) Frontend setup

```bash
cd /home/runner/work/virus-classifier-app/virus-classifier-app/frontend
npm ci
npm run dev
```

Optional environment variable:

- `VITE_API_BASE_URL` (defaults to `http://127.0.0.1:8000`)

Frontend build/lint:

```bash
npm run lint
npm run build
```

---

## API Reference

Base URL: `http://127.0.0.1:8000` (local default)

### `POST /predict`

Single-sequence synchronous prediction.

Request:

```json
{
  "sequence": "ATGCGT...",
  "model_name": "hyenadna"
}
```

Response fields include:

- `influenza_type`
- `confidence`
- `scores`
- `sequence_length`
- `model_used`

### `POST /batch/predict`

Submit batch prediction job.

Request:

```json
{
  "sequences": ["ATG...", "CGT..."],
  "model_name": "xgb"
}
```

Returns a `task_id` and `PENDING` status.

### `GET /batch/predict/{task_id}`

Poll batch status:

- `PENDING`
- `PROGRESS` (includes `progress.current` and `progress.total`)
- `SUCCESS` (includes `results`)
- `FAILURE`

---

## Input Validation Rules

From `/home/runner/work/virus-classifier-app/virus-classifier-app/app/schemas.py`:

- Allowed nucleotide alphabet: `A`, `C`, `T`, `G`, `N` (case-insensitive)
- Batch size limit: **100 sequences**
- Max sequence length: **32,000**
- Empty sequences are rejected

---

## Available Models

Configured in `/home/runner/work/virus-classifier-app/virus-classifier-app/app/registry.py`:

- `hyenadna`
- `logistic_regression`
- `random_forest`
- `xgb`
