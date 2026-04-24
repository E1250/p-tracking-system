# Real-Time Multi-Camera Tracking System

A production-grade AI surveillance system that processes live camera streams, detects incidents in real time, and streams alerts to a 2D floor-plan dashboard. Built as a graduation project targeting small-to-medium office environments.

**[Live Dashboard](https://p-tracking-system.vercel.app/)** · **[Gradio Demo](https://huggingface.co/spaces/e1250/tracking_system_demo)** · **[Backend API](https://huggingface.co/spaces/e1250/tracking_system_backend)**

---

## What it does

Cameras stream JPEG frames over WebSocket to the backend. Each frame is processed through a parallel AI pipeline — person detection, depth estimation, and safety detection (fire/smoke) run concurrently. Results are published to Redis and streamed in real time to a React dashboard rendered on a 2D floor plan. When a danger is detected, the camera indicator turns red on the floor plan and person positions are updated using depth-estimated X ratios.

---

## Architecture

```
Cameras (WebSocket) ──► FastAPI backend ──► Redis pub/sub ──► React dashboard
                              │                  │
                    AI pipeline (async)    setex TTL cache
                    YOLO · Depth · Safety
                              │
                    HuggingFace Hub (model weights)
                    MLflow / DagsHub (experiment tracking)
                    Prometheus (metrics)
```

**Key design decisions:**

- **Per-camera `asyncio.Queue(maxsize=1)`** — latest-frame-wins backpressure. Old frames are dropped rather than queued, keeping latency minimal under load.
- **Redis over `app.state`** — allows horizontal scaling across multiple workers. `app.state` is single-worker only.
- **`git subtree push`** — backend deploys independently from the monorepo to HuggingFace Spaces. Frontend deploys to Vercel. One commit triggers both.
- **Dependency injection via `Depends()`** — models are loaded once at startup into `app.state`, injected into routes. Makes unit testing with mocks straightforward.
- **Nested MLflow runs** — one parent run per server session, one child run per camera connection. Tracks inference latency per frame.
- **fp16 inference** — `half=True` on YOLO, `torch.autocast` on DepthAnything for faster GPU throughput.
- **HuggingFace model hosting** — weights are never committed to Git. `hf_hub_download` fetches and caches at startup.

---

## Stack

| Layer | Technology |
|---|---|
| AI | YOLOv8 (person + safety), DepthAnything V2 (depth estimation) |
| Backend | FastAPI, Uvicorn, WebSockets, Redis (async), Pydantic v2 |
| Observability | Prometheus, structlog (JSON), MLflow + DagsHub |
| Frontend | React 19, TypeScript, Vite, react-konva, Immer |
| Deployment | Docker, GitHub Actions, HuggingFace Spaces, Vercel |
| Tooling | ruff, pyright, pytest, pre-commit, hatchling |

---

## Project structure

```
tracking_dashboard/
├── ai/                        # Installable package (pip install -e ./ai)
│   ├── contracts/             # Pydantic schemas (BBox, DetectionResults)
│   ├── detectors/             # YOLO_Detector implementing Detector ABC
│   ├── depth/                 # DepthAnything V2 wrapper
│   ├── domain/                # ABCs: Detector, Depth, Tracker
│   ├── trackers/              # YoloTracker stub
│   └── utils/                 # HuggingFace fetch, constants
├── backend/
│   ├── api/routers/           # camera_stream, dashboard_stream, health, metrics
│   ├── config/                # AppConfig (pydantic-settings, YAML + .env)
│   ├── domain/                # Logger ABC, detection geometry
│   ├── infra/                 # StructLogger, system_metrics
│   ├── services/              # ProcessingPipeline
│   ├── tests/                 # pytest-asyncio, AsyncMock, httpx
│   └── main.py                # FastAPI lifespan, app assembly
├── dashboard/                 # React + Vite + TypeScript
├── gradio/                    # Demo client (image upload → WebSocket)
├── .github/workflows/         # deploy-backend.yml, deploy-gradio.yml
├── pyproject.toml             # hatchling build, ruff, pyright, pytest config
└── .pre-commit-config.yaml    # ruff + pytest on every commit
```

---

## Running locally

**Prerequisites:** Python 3.11+, Node 20+, Redis, conda (recommended)

```bash
# 1. Clone
git clone https://github.com/E1250/p-tracking_system.git
cd p-tracking_system

# 2. Python env
conda create -n tracking-system python=3.11
conda activate tracking-system
pip install -e ./ai
pip install -r backend/requirements-dev.txt

# 3. Config
cp backend/config/.env.example backend/config/.env
# Set redis_url and dagshub_user_token in .env

# 4. Start Redis (Docker)
docker run -d -p 6379:6379 redis

# 5. Start backend
cd backend
uvicorn main:app --reload

# 6. Start dashboard (separate terminal)
cd dashboard
npm install
npm run dev
```

Backend API docs: `http://localhost:8000/docs`  
Health check: `http://localhost:8000/health/ready`  
Prometheus metrics: `http://localhost:8000/metrics`

---

## Testing

```bash
# Unit tests
pytest

# All checks (ruff + pyright + pytest + mkdocs)
bash scripts/run_checks.sh

# Manual integration test (requires running backend)
python tests/test_server.py
```

Pre-commit hooks run ruff and pytest automatically on every `git commit`.

---

## Deployment

Deployment is fully automated via GitHub Actions:

- Push to `main` with changes in `backend/**` → CI runs tests → deploys backend to HuggingFace Spaces via `git subtree push`
- Push to `main` with changes in `gradio/**` → deploys Gradio demo to HuggingFace Spaces
- Dashboard deploys automatically to Vercel on push

**Required secrets:** `HF_TOKEN` (HuggingFace write token)  
**Required HF Space variables:** `redis_url`, `dagshub_user_token`

---

## Models

| Model | Source | Purpose |
|---|---|---|
| YOLOv8n | `Ultralytics/YOLO26` on HF | Person detection |
| YOLO (custom) | `e1250/safety_detection` on HF | Fire and smoke detection |
| DepthAnything V2 ViT-S | `depth-anything/Depth-Anything-V2-Small` on HF | Monocular depth estimation |

Models are fetched at server startup via `hf_hub_download` and cached in `.hf_cache/`. Weights are never stored in Git.

---

## Observability

The system exposes three observability layers:

- **Prometheus** (`/metrics`) — active camera connections, active dashboards, per-camera frame/detection/depth latency histograms, CPU and memory gauges.
- **structlog** — JSON-structured logs with ISO timestamps, stack traces, and contextual fields (camera_id, frame counts).
- **MLflow on DagsHub** — one session-level parent run, nested child runs per camera. Tracks model config and per-frame inference latencies.

---

## Configuration

All configuration lives in `backend/config/config.yaml` with environment variable overrides via `.env`. Priority order: `.env` > environment variables > YAML defaults.

```yaml
# config.yaml — shared defaults
yolo:
  model_name: "yolo26n.pt"
depth:
  encoder: "vits"
  device: "cpu"
intervals:
  realtime_updates_every: 2
```

Override anything in `.env` or HuggingFace Space secrets without touching the YAML.

---

## License

MIT