# Traffic Surveillance Data Quality & Reliability Platform

A real-time observability and validation platform for traffic surveillance networks. Built to solve the data-quality and camera-health gaps that prevent before/after analysis on AI-based traffic safety deployments.

> **Origin:** Inspired by a real IIT Madras x Mercedes-Benz Research & Development India deployment across 9 Bengaluru locations, where only 3 sites could complete proper before/after analysis due to camera failures, power issues, and recording gaps.

---

## What it does

1. **Camera Health Monitoring** — detects when a camera goes down and classifies the cause (power, network, physical damage).
2. **Real-Time Data Validation** — flags vehicle-count anomalies using statistical + cross-camera checks.
3. **Automated Before/After Comparison** — generates surrogate-safety-measure reports (PET, TTC, speed) on demand.
4. **Conversational Query Interface** — researchers ask plain-English questions; LLM agents query the system and answer.

---

## Architecture (high level)

```
Researcher (Next.js dashboard)
        |
        v
FastAPI backend  ──►  PostgreSQL + TimescaleDB (long-term storage)
        |        ──►  Redis (real-time cache + pub/sub)
        |        ──►  LangGraph agents  ──►  Claude / Gemini API
        |                                ──►  LangSmith (observability)
        v
Background workers ──► simulated cameras / public traffic datasets
        |
        └──► Qdrant (historical pattern similarity)
```

---

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | Next.js + Tailwind |
| Backend API | FastAPI (async) |
| Database | PostgreSQL + TimescaleDB |
| Cache / queue | Redis |
| Vector DB | Qdrant |
| LLM orchestration | LangGraph |
| LLM provider | Claude (Anthropic) |
| LLM observability | LangSmith |
| Vision | OpenCV + YOLOv8 (pretrained) |
| Evaluation | Ragas |
| Containerization | Docker Compose -> AWS ECS |
| Metrics | Prometheus + Grafana |

---

## Local development

### Prerequisites
- Docker Desktop
- Node.js 20+ (for frontend, added in later phases)
- Python 3.12+ (for running tools outside Docker)

### First-time setup
```bash
cp .env.example .env
docker compose up -d --build
```

The backend will be live at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Running the camera simulator
Once the Docker stack is running, start the camera simulator to generate test data:
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt
python simulator/camera_sim.py
```
This registers 5 simulated cameras (KR Puram, TC Palya, Silk Board, Indiranagar, MVIT Sadahalli) and continuously sends heartbeats + traffic telemetry to the backend API.

### Services exposed
| Service | Port |
|---|---|
| FastAPI backend | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| Qdrant | 6333 / 6334 |

---

## Build phases

- [x] **Phase 0** — Project setup, Docker Compose stack, FastAPI skeleton
- [x] **Phase 1** — Camera simulator + database models + heartbeat ingestion
- [ ] **Phase 2** — Camera health monitoring worker + dashboard v1
- [ ] **Phase 3** — Statistical validation engine + Qdrant pattern matching
- [ ] **Phase 4** — LangGraph agents (health, anomaly, comparison) + chat UI
- [ ] **Phase 5** — Polish, deploy to AWS, demo video, write-up

---

## Project layout

```
backend/
  app/
    core/           Config + database engine (database.py, config.py)
    models/         SQLAlchemy table definitions (Camera, Heartbeat, TrafficData, StatusLog)
    routes/         API endpoints (cameras, heartbeats, traffic, health)
    schemas/        Pydantic request/response validation schemas
    main.py         FastAPI app entry point with DB init + route registration
  Dockerfile        Container build instructions for the backend
  requirements.txt  Python dependencies
workers/            Background services (health checker, validators, detectors)
agents/             LangGraph agents + their tools
simulator/          Camera simulator (5 Bengaluru junctions, heartbeats + traffic)
frontend/           Next.js dashboard
evals/              Ragas evaluation suite
infra/              Terraform / k8s configs for deployment
scripts/            DB init scripts (TimescaleDB extension setup)
```
