- For tasks.md, it is kinda alternate to `Trello` and agile for project management, I plan to keep using Github Issues and ``todo` file. 
- I would prefer using `env.yml` rather than req.txt in my case.
- fb16 has been added, it takes lower memory and get the same accuracy.

## GP Tracking Dashboard — Task Plan (End-to-End, Multi-Worker)

Goal: product-grade realtime incident detection (person/fire/smoke) from live camera streams, with a dashboard that visualizes state + alerts, running safely on multiple workers.

### Guiding constraints

- Low-latency realtime (bounded buffering, backpressure, "latest-frame wins")
- Observable (metrics + structured logs + traces/profiles)
- Reproducible (dependency manifests match imports; clear run commands)
- Testable (pytest tests for API + websocket flows)

---

---

## Phase 1 — Backend architecture for multi-worker

### 1A) Replace in-memory shared state (`app.state`)

Current: `camera_stream` writes to `app.state.camera_metadata` and `dashboard_stream` reads it.
Problem: breaks with multiple workers.
Plan:

- Introduce Redis as the shared state store (single source of truth)
  - Key schema example:
    - `camera:{camera_id}:metadata` -> JSON blob (latest snapshot)
    - `camera:{camera_id}:last_seen` -> timestamp
    - `cameras:active` -> set of active camera_ids
- Choose update model:
  - Option A: dashboard websocket polls Redis at interval (simple, acceptable)
  - Option B: Pub/Sub per camera or global "updates" channel (lower latency, more complex)
- Decide retention/TTL:
  - `metadata` TTL (e.g. 10s) so dead cameras disappear automatically
  - active cameras set cleanup strategy
  Deliverable: backend works with `--workers N` consistently.

### 1B) Add backpressure & compute model

- Implement per-camera processing policy:
  - "latest-frame wins": keep only the newest frame (drop backlog)
  - bounded queue size=1 (or 2) per camera
- Protect event-loop:
  - all CPU heavy ops in executor
  - GPU inference serialized per device or batched (see Phase 2)
  Deliverable: stable under high FPS camera input.

---

## Phase 2 — Realtime inference pipeline (person/fire/smoke)

### 2A) Define contracts (backend <-> dashboard)

- Define a single camera snapshot schema (Pydantic model), including:
  - `camera_id`, `timestamp`, `is_danger`, `danger_labels` (person/fire/smoke)
  - `detections`: list of bboxes with class/conf/coords
  - optional: `depth_points` / occupancy / heatmap summary
- Ensure safe defaults (no mutable list defaults)
Deliverable: versioned JSON schema that dashboard consumes.

### 2B) YOLO inference integration

- Enable YOLO detection in camera websocket handler
- Add thresholds per class (config-driven)
- Implement "danger" rule:
  - danger if any of {person, fire, smoke} above threshold
  - optional: debounce (e.g. require K of last M frames to reduce flicker)
  Deliverable: live detections + `is_danger` updates stored in Redis.

### 2C) Optimization plan (pragmatic)

- Profile baseline end-to-end latency (frame recv -> inference -> stored -> dashboard)
- GPU optimizations:
  - resize strategy (fixed short side)
  - half precision (fp16) if supported
  - optional batching (small batch 2–5) ONLY if it reduces latency at target load
- CPU optimizations:
  - faster JPEG decode path (measure)
  - avoid repeated allocations where possible
  Deliverable: measured latency/FPS targets documented.

---

## Phase 3 — Dashboard: realtime viewer (not just editor)

Current: dashboard is a floorplan editor stored in localStorage.
Plan:

- Add a networking layer:
  - connect to backend websocket `/dashboard/stream`
  - render camera states (danger coloring, badges)
- Map backend camera_ids to floorplan camera nodes:
  - add `camera_id` field to camera nodes in the editor data model
  - UI for assigning/selecting camera_id per placed camera icon
- UX:
  - alert panel + timeline (last N incidents)
  - per-camera details drawer (detections list, last update time)
  Deliverable: dashboard shows realtime danger status on the floorplan.

---

## Phase 4 — Observability & operations

- Metrics:
  - per-camera FPS in/out, inference time, queue drops
  - dashboard connected count, active cameras, Redis latency
- Logging:
  - structured events with `camera_id`, correlation ids
- Health:
  - `/health/ready` checks Redis connectivity + model loaded
- Deployment:
  - docker-compose: backend + redis (+ optional prometheus/grafana)
  - production server command (gunicorn/uvicorn workers) documented
  Deliverable: you can run locally as a “mini production” stack.

---

## Phase 5 — Tests

- Convert websocket scripts into pytest:
  - 2 cameras + 1 dashboard integration test
  - assert Redis contains expected keys and dashboard receives updates
- Add load test (optional):
  - simulate camera FPS streams, ensure bounded memory and acceptable latency
  Deliverable: CI-friendly tests validating the critical path.

---

## Definition of Done (for MVP)

- Multiple workers enabled; state consistent via Redis
- Cameras stream frames, backend detects person/fire/smoke, writes snapshots
- Dashboard websocket receives snapshots and renders danger status
- Metrics + logs + health endpoints are meaningful
- Reproducible install/run documented

---

---

---

---

---

Good — your mindset is correct. Now I’ll give you **focused, actionable guidance** (no fluff).

---

# 🎯 Your Goal

> Turn this into a **real production-grade AI system**, not just a project.

---

# 🧠 1. The rule you MUST follow

👉 **Depth > Features**

If you keep adding features → you stay mid  
If you go deep → you move toward senior

---

# 🏗️ 2. Lock the Architecture (non-negotiable)

Refactor into **strict layers**:

```
/domain        → pure logic (tracking, depth, detection)
/application   → use cases (track_object, process_frame)
/infrastructure→ models, DB, external APIs
/interfaces    → FastAPI routes, UI

```

Rules:

- domain knows NOTHING about FastAPI, DB, or models
- everything injected (dependency injection mindset)

👉 This is where seniors stand out.

---

# 🤖 3. Turn AI into a real pipeline

Right now it's likely “functions”.

Make it:

```
Input → Preprocess → Model → Postprocess → Output

```

Add:

- config-based model selection
- ability to swap models (YOLO, custom, etc.)
- batching support

👉 Think like you're building a mini ML platform.

---

# ⚙️ 4. Backend like a real system

Add:

### Validation

- Pydantic schemas everywhere

### Logging

- structured logs (not print)

### Errors

- custom exceptions
- proper HTTP responses

### API design

- `/v1/track`
- `/v1/detect`

👉 Clean API = senior signal.

---

# 🔄 5. Async + Background processing

Very important:

- heavy tasks (AI inference) → background workers
- use:
  - queue (Redis + Celery or RQ)
  - or FastAPI background tasks (start simple)

👉 This separates juniors from real backend engineers.

---

# 📡 6. Real-time capability (optional but powerful)

If you add:

- WebSocket streaming
- live tracking feed

👉 This becomes a **serious system**

---

# 🧪 7. Testing (DON’T SKIP)

Minimum:

- unit tests for domain
- 1–2 API tests

You’ll learn:

- design quality
- edge cases
- stability

---

# 🐳 8. Production mindset

You already used Docker — good.

Now improve:

- docker-compose (backend + frontend + redis)
- environment configs
- `.env` handling

---

# 📊 9. Observability (very senior move)

Add:

- logging
- simple metrics (time per inference)

Optional:

- Prometheus / Grafana later

---

# 🧩 10. One advanced feature ONLY

Pick ONE:

- model serving system
- real-time tracking
- multi-camera support
- pipeline orchestration

👉 Don’t do all. Depth.

---

# 🛑 When to STOP?

This is critical.

👉 Stop when:

### ✅ You have:

- clean architecture (strict layers)
- working API (well designed)
- AI pipeline (modular)
- async/background processing
- basic tests
- dockerized system

AND:

### ✅ You can explain:

- every design decision
- trade-offs
- how to scale it

👉 If you can **defend your system like an engineer**, you’re ready.

---

# 🚨 When NOT to stop

If:

- code is messy
- logic mixed everywhere
- no tests
- no structure

👉 then you're not done

---

# 🧠 Final truth

Senior ≠ knowing more tools  
Senior = **how you think and structure systems**

---

# 🔥 If you follow this seriously

You won’t just have a project

👉 You’ll have:

- a **portfolio-level system**
- something you can talk about in interviews deeply
- real engineering experience

---

If you want next:  
I can **redesign your current repo structure step-by-step** into a clean architecture version.

---

---

---

---

# 🏗️ The 3-project strategy (this is ideal for you)

## 🥇 1. Core System (YOU ARE BUILDING THIS)

👉 tracking_system

Make it:

- full pipeline (AI + backend + frontend)
- real-time capable
- modular AI system

This becomes:  
👉 your **main flagship project**

---

## 🥈 2. Deep Learning / Research project

Not engineering — research style.

Examples:

- implement a paper (object tracking, SLAM, depth)
- improve a model
- experiment + metrics + evaluation

👉 Shows:

- you understand **math + DL deeply**

---

## 🥉 3. Robotics / Physical AI project

Even simple:

Examples:

- simulation (ROS, Gazebo)
- drone/car control logic
- sensor fusion (camera + something)

👉 Shows:

- you connect **AI with physics/world**

