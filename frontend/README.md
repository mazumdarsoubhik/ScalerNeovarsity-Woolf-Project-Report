# NutriFlow Frontend (UI)

Production-oriented Streamlit UI for meal logging, day-wise nutrition tracking, history management, and contextual nutrition chat.

It solves four core UX jobs:
- let users log meals in natural language with minimal friction
- visualize daily macro progress and streak signal clearly
- support correction workflows (edit/delete) directly in UI
- provide conversational guidance grounded in user meal context

## Why This UI Matters

Nutrition products fail when the interface adds too much effort between intent and action. This frontend reduces that gap:

- Fast capture: one-screen meal text logging with optional eaten timestamp
- Actionable visibility: macro cards show consumed vs target vs remaining
- Reliable correction loop: every listed meal can be edited/deleted in place
- Low-context switching: auth, tracking, history, chat, and settings in one app shell
- Operational simplicity: one Streamlit app with explicit backend URL control

## Scope And UI Logic

### 1) Authentication UX
- Single auth panel with mode switch: `Login` / `Register`
- Email + password form validation (required fields)
- Session bootstrap via `GET /auth/me` on app load when token exists
- Expired/invalid token handling: clear auth state and force re-login

### 2) Today Tab (Primary Tracking Surface)
- Meal logging form:
  - free-text meal description
  - optional meal type (`breakfast/lunch/snack/dinner`)
  - optional eaten date/time
- Dashboard for selected day:
  - macro cards: calories/protein/carbs/fat/fibre
  - consumed, target, remaining shown per macro
  - meal count + streak days summary
- Same-day meal list with inline edit/delete actions

### 3) History Tab (Exploration + Correction)
- Date-range filters (`start_date`, `end_date`) + pagination (`limit`, `offset`)
- Validation prevents invalid date range (`start > end`)
- Previous/Next navigation updates offset in session state
- Per-meal expanders expose text, confidence, macro totals, edit/delete controls

### 4) Chat Tab (Context-Aware Guidance)
- Chat transcript persisted in session (`chat_messages`)
- Optional `context_day` date sent with prompt
- Assistant replies rendered in chat UI with loading spinner
- Error replies are surfaced in conversation when backend call fails

### 5) Settings Tab (Runtime Control)
- Backend base URL editable at runtime
- Health check button calls backend health endpoint
- URL change invalidates auth intentionally (forces re-login)
- Logout path clears local auth state (best-effort backend logout)

## Tech Stack

- UI framework: Streamlit
- HTTP client: requests
- Date utilities: python-dateutil (dependency present)
- Runtime: Python 3.x
- App model: single-page Streamlit app with tabbed layout + session state

## High-Level UI Architecture

```text
User
  |
  v
Streamlit App Shell (app.py)
  |
  +--> Auth Gate (ui_auth.py)
  |
  +--> Today Tab (ui_today.py)
  +--> History Tab (ui_history.py)
  +--> Chat Tab (ui_chat.py)
  +--> Settings Tab (ui_settings.py)
  |
  v
BackendClient (client.py)
  |
  v
NutriFlow Backend API (/api/v1/*)
```

## Low-Level Interaction Flows

### A) App Bootstrap + Session Restore

```text
App start
  -> init_state() seeds defaults in st.session_state
  -> construct BackendClient(base_url, access_token)
  -> if token exists and user profile missing:
       call /auth/me
       success -> hydrate auth_user_id/auth_email
       failure -> clear auth + rerun to login view
  -> if no token: render auth panel
  -> else render tabs
```

### B) Meal Log Flow (Today)

```text
User submits log form
  -> client.create_meal(text, meal_type, eaten_at)
  -> success banner + rerun
  -> fetch dashboard(day)
  -> fetch meals history filtered to selected day
  -> render macro cards + meal rows
```

### C) Meal Edit/Delete Flow (Today/History)

```text
Edit submit
  -> PATCH /meals/{meal_id}
  -> success + rerun
  -> on 404: warn and rerun

Delete click
  -> DELETE /meals/{meal_id}
  -> success + rerun
  -> on 404: warn and rerun
```

### D) Chat Flow

```text
User sends prompt
  -> append user message to session transcript
  -> POST /chat {message, context_day}
  -> append assistant response (or error text) to transcript
```

## API Surface Consumed By UI

Base API prefix is hard-coded in client as `/api/v1`.

Public:
- `GET /health`
- `POST /auth/register`
- `POST /auth/login`

Protected:
- `POST /auth/logout`
- `GET /auth/me`
- `POST /meals`
- `PATCH /meals/{meal_id}`
- `DELETE /meals/{meal_id}`
- `GET /meals/history`
- `GET /dashboard/today`
- `POST /chat`

## State Model (Streamlit Session)

Initialized keys:
- `backend_url` (default `http://localhost:8080`)
- `access_token`, `auth_user_id`, `auth_email`
- `chat_messages` (list)
- `history_filters`:
  - `start_date`, `end_date`
  - `limit` (default `20`), `offset` (default `0`)
- `last_error`

## Code Structure

```text
frontend/
  app.py              # app shell, auth gating, tab composition
  streamlit-app.py    # compatibility entrypoint (imports app)
  client.py           # typed backend API wrapper + error handling
  state.py            # session-state initialization/helpers
  ui_auth.py          # login/register UI
  ui_today.py         # log meal + dashboard + same-day meal list
  ui_history.py       # filtered history + pagination + edit/delete
  ui_chat.py          # chat transcript + prompt flow
  ui_settings.py      # backend URL, health check, logout
  requirements.txt
```

## Local Development

From `frontend/`:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
py -3 -m pip install -r requirements.txt
py -3 -m streamlit run app.py
```

Compatibility entrypoint (same behavior):

```bash
py -3 -m streamlit run streamlit-app.py
```

Default backend URL expected by UI: `http://localhost:8080`

## Deployment Options

This repository does not include Docker/IaC for frontend deployment. Baseline options:

### 1) Local/Team VM (Systemd)
- Create virtualenv on server
- Install `requirements.txt`
- Run Streamlit bound to host/port
- Manage process with `systemd`
- Put Nginx/Caddy in front for TLS and routing

Example service command:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 2) Streamlit Community Cloud / Managed PaaS
- Deploy `frontend/` as app root
- Configure Python dependencies from `requirements.txt`
- Ensure backend API is publicly reachable
- Set backend URL in Settings after first launch

## Operational Notes

- UI assumes backend responses follow documented schemas; shape drift will surface as runtime errors.
- URL changes intentionally clear auth state to avoid token/domain mismatch.
- Errors are stored in `last_error` and also rendered near interaction points.
- Chat history is per-session only (browser tab/session), not durable client-side storage.

## Security Notes

- Access token is kept in Streamlit session state for the active session.
- Always run frontend and backend over HTTPS in production.
- Do not expose internal/private backend URLs to untrusted clients.

## Known Limitations / Future Improvements

- No automated UI tests currently
- No client-side caching or optimistic updates
- No role/permission-specific UI branches
- No first-class theming/branding system yet
