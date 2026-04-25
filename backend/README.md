# NutriFlow Backend

Production-focused FastAPI backend for nutrition tracking and guidance.

It solves three core product jobs:
- convert free-text meals into structured macro entries
- maintain reliable day-wise nutrition summaries and streaks
- provide context-aware chat guidance grounded in meals and dashboard state

## Why This Backend Matters

Nutrition apps often fail because logging is tedious and feedback is generic. This backend reduces both issues:

- Low-friction logging: users enter natural language instead of manually filling macro fields
- Reliable tracking: meals are persisted as structured items; daily aggregates are recomputed from source-of-truth meal items
- Actionable coaching: chat replies include current nutrition gaps, recent meal history, and prior conversation context
- Safety fallback: when LLM calls fail, deterministic responses and parsers keep the product usable

## Scope And Business Logic

### 1) Authentication And Session Model
- Email/password registration and login
- PBKDF2-SHA256 password hashing (`200000` iterations)
- Bearer access tokens stored as SHA256 hashes in DB (`auth_tokens`)
- Token revocation and expiry checks on every protected request

### 2) Meal Logging And Parsing
- Input: free-text meal string (`"2 roti and dal"`)
- Parser orchestration modes:
  - `rule_only`
  - `llm_only`
  - `llm_first` (default, with confidence-driven fallback)
- Unknown food names can be captured as `food_candidates` for future catalog enrichment
- Meal updates support:
  - re-parse via new text
  - manual item override with known canonical foods

### 3) Dashboard Aggregation
- Daily summary recomputed from meal_items each time dashboard/meal mutation flows run
- Returns consumed/target/remaining macros
- Computes streak days by walking backward day-by-day until a non-logged day

### 4) Context-Aware Chat
- Chat prompts include:
  - current dashboard macro gaps
  - recent meals over a rolling context window
  - recent chat turns
- Provider connectors: Groq, Gemini, Mistral (+ deterministic mock fallback)
- If provider fails, fallback response still returns practical suggestions

## Tech Stack

- API framework: FastAPI
- Runtime server: Uvicorn
- ORM: SQLAlchemy 2.x
- Validation: Pydantic v2
- Config/env loading: python-dotenv
- Storage: SQLite by default (`sqlite:///./nutriflow.db`), swappable via `DATABASE_URL`
- LLM integration: provider-specific HTTP connectors (urllib-based)

## High-Level Architecture

```text
Frontend (Streamlit / any client)
        |
        v
FastAPI Routers (/api/v1/*)
        |
        v
Service Layer (auth, meals, parser, dashboard, chat)
        |
        +--> LLM Connector Factory -> Groq/Gemini/Mistral/Mock
        |
        v
SQLAlchemy ORM Models -> SQLite/Postgres
```

## Low-Level Request Flows

### A) Meal Create Flow (`POST /api/v1/meals`)

```text
Request -> Auth dependency validates bearer token
        -> ensure_user_and_goal()
        -> create_meal():
             ensure_seed_foods()
             alias_map = food catalog + aliases
             parse_meal_text() via parser orchestrator
             persist meal + meal_items
             recompute_daily_summary()
        -> Response: MealOut (items + totals + confidence)
```

### B) Dashboard Flow (`GET /api/v1/dashboard/today`)

```text
Request -> Auth
        -> ensure_user_and_goal()
        -> get_today_dashboard():
             recompute_daily_summary(day)
             load/create user goal
             compute consumed/target/remaining + streak
        -> Response: DashboardTodayResponse
```

### C) Chat Flow (`POST /api/v1/chat`)

```text
Request -> Auth
        -> ensure_user_and_goal()
        -> create_chat_reply():
             dashboard = get_today_dashboard()
             deterministic fallback reply built
             if LLM_ENABLED:
                fetch recent meals + chat history
                build prompt with context
                connector.generate()
                if success -> use LLM reply
                if fail -> keep fallback reply
             persist user + assistant messages
        -> Response: ChatResponse
```

## Code Structure

```text
backend/
  app/
    api/
      deps.py
      v1/
        endpoints/   # auth, meals, dashboard, chat, health
        router.py
    core/
      config.py
      database.py
      llm/
        connectors/  # groq, gemini, mistral, mock
        factory.py
    db/
      models/        # user, meal, meal_item, daily_summary, chat, auth, etc.
    schemas/         # Pydantic request/response contracts
    services/        # business logic (auth, parser, meals, dashboard, chat)
  test_llm.py        # provider connectivity smoke test
```

## Data Model (Key Tables)

- `users`: identity root
- `user_credentials`: normalized email + password hash
- `auth_tokens`: hashed bearer tokens with expiry/revocation
- `user_goals`: macro targets per user
- `foods`: canonical food catalog + aliases + nutrition defaults
- `food_candidates`: unknown foods proposed by LLM parser
- `meals`: raw meal entries with parser confidence
- `meal_items`: normalized per-food macro rows linked to meals
- `daily_summaries`: day-level aggregates per user
- `chat_messages`: persisted conversational history

## API Surface

Base prefix is configurable via `API_V1_PREFIX` (default `/api/v1`).

Public:
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

Protected (Bearer token required):
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/meals`
- `PATCH /api/v1/meals/{meal_id}`
- `DELETE /api/v1/meals/{meal_id}`
- `GET /api/v1/meals/history`
- `GET /api/v1/dashboard/today`
- `POST /api/v1/chat`

## Configuration

Create `backend/.env` with values below.

### Core
- `APP_NAME` (default: `NutriFlow Backend`)
- `API_V1_PREFIX` (default: `/api/v1`)
- `DATABASE_URL` (default: `sqlite:///./nutriflow.db`)

### Auth
- `AUTH_TOKEN_TTL_MINUTES` (default: `10080`)

### LLM Chat + Parser
- `LLM_ENABLED` (`true|false`, default: `true`)
- `LLM_PROVIDER` (`groq|gemini|mistral|...`, unknown values route to mock connector)
- `LLM_MODEL` (provider model id)
- `LLM_TIMEOUT_SECONDS` (default: `20`)
- `LLM_MAX_TOKENS` (default: `512`)
- `GROQ_API_KEY`, `GROQ_BASE_URL`
- `GEMINI_API_KEY`, `GEMINI_BASE_URL`
- `MISTRAL_API_KEY`, `MISTRAL_BASE_URL`

### Meal Parsing
- `MEAL_PARSER_MODE` (`llm_first|rule_only|llm_only`, default: `llm_first`)
- `MEAL_PROMPT_VERSION` (default: `v1`)
- `MEAL_LLM_MIN_CONFIDENCE` (default: `0.65`)

## Local Development

From `backend/`:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --reload --port 8080
```

Health check:

```bash
curl http://localhost:8080/api/v1/health
```

## Example Auth + Protected Calls

Register:

```bash
curl -X POST http://localhost:8080/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@example.com\",\"password\":\"StrongPass123\"}"
```

Use returned `access_token`:

```bash
curl -X GET http://localhost:8080/api/v1/dashboard/today ^
  -H "Authorization: Bearer <access_token>"
```

Create meal:

```bash
curl -X POST http://localhost:8080/api/v1/meals ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"2 roti and dal\",\"meal_type\":\"lunch\"}"
```

Chat:

```bash
curl -X POST http://localhost:8080/api/v1/chat ^
  -H "Authorization: Bearer <access_token>" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"What should I eat for dinner?\"}"
```

## LLM Provider Health Check

From project root:

```bash
py backend/test_llm.py
```

This verifies connector-level calls for Groq, Gemini, and Mistral (if keys exist).

## Server Deployment (Linux VM/Bare Metal)

This repo does not include Docker or IaC files, so recommended baseline is:
- Python virtualenv
- Uvicorn process managed by systemd
- Reverse proxy (Nginx/Caddy) for TLS and public ingress

### 1) Install And Run App User

```bash
sudo adduser --system --group nutriflow
sudo mkdir -p /opt/nutriflow
sudo chown -R nutriflow:nutriflow /opt/nutriflow
```

Copy backend code to `/opt/nutriflow/backend`, then:

```bash
cd /opt/nutriflow/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure Environment

Create `/opt/nutriflow/backend/.env` with production values:
- strong DB URL (prefer Postgres for multi-user production)
- valid provider keys
- appropriate token TTL

### 3) Systemd Unit

`/etc/systemd/system/nutriflow-backend.service`

```ini
[Unit]
Description=NutriFlow Backend
After=network.target

[Service]
User=nutriflow
Group=nutriflow
WorkingDirectory=/opt/nutriflow/backend
EnvironmentFile=/opt/nutriflow/backend/.env
ExecStart=/opt/nutriflow/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable/start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nutriflow-backend
sudo systemctl start nutriflow-backend
sudo systemctl status nutriflow-backend
```

### 4) Reverse Proxy

Route `https://<domain>/` to `http://127.0.0.1:8080`.
Ensure timeout and body-size settings align with request sizes.

## Operational Notes

- Startup runs `Base.metadata.create_all(...)`; this is acceptable for small deployments but migrations are recommended for controlled schema evolution.
- SQLite is suitable for local/small usage; use Postgres for concurrent production workloads.
- Chat and parser resiliency are designed so LLM outages degrade gracefully rather than breaking core features.

## Security Notes

- Never commit real API keys in `.env`.
- Rotate leaked provider keys immediately.
- Use HTTPS in production and keep bearer tokens only on trusted clients.
- Add rate limiting and request logging at reverse proxy/API gateway level for internet-facing deployments.

## Known Limitations / Future Improvements

- No migration tooling committed yet (Alembic recommended)
- No built-in background jobs/queues for heavy parsing workloads
- No containerization files in repo
- Limited automated tests; add endpoint + service tests for regression safety
