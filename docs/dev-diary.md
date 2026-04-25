# NutriFlow Development Diary

Last updated: 2026-04-25

## Phase 1: Foundation and Project Setup
- [x] Monorepo structure with `backend/` and `frontend/`
- [x] Base dependencies and run instructions documented
- [x] FastAPI app bootstrap and Streamlit app bootstrap

## Phase 2: Authentication and User Context
- [x] Email/password register and login APIs
- [x] Bearer token auth for protected APIs
- [x] Token expiry + revocation handling
- [x] Frontend auth UI (`Login` / `Register`)
- [x] Session restore via `GET /auth/me`
- [x] Logout flow in frontend settings

## Phase 3: Meal Logging and Parsing
- [x] `POST /api/v1/meals` for free-text meal logging
- [x] Parser orchestration modes: `rule_only`, `llm_only`, `llm_first`
- [x] Deterministic parsing + alias mapping + fallback assumptions
- [x] Unknown food capture as `food_candidates`
- [x] Meal update with re-parse or manual item override
- [x] Meal delete flow with consistency handling

## Phase 4: Dashboard and Aggregation
- [x] `GET /api/v1/dashboard/today` with consumed/target/remaining
- [x] Daily summary recomputation from source meal items
- [x] Streak computation and exposure in dashboard output
- [x] Frontend macro cards and daily summary rendering

## Phase 5: History and Correction UX
- [x] `GET /api/v1/meals/history` with date range + pagination
- [x] Frontend history tab with filters and prev/next pagination
- [x] Inline edit/delete controls in Today and History views
- [x] Error handling for stale/deleted records (e.g., `404`)

## Phase 6: Context-Aware Chat
- [x] `POST /api/v1/chat` endpoint
- [x] Chat context includes dashboard gaps and recent history
- [x] LLM connector support (Groq, Gemini, Mistral, Mock)
- [x] Deterministic fallback when provider fails
- [x] Chat persistence (`chat_messages`)
- [x] Frontend chat tab with per-session transcript

## Phase 7: Ops and Deployment Readiness
- [x] Health endpoint
- [x] Environment-variable driven backend config
- [x] Local run instructions for backend and frontend
- [x] Baseline VM/systemd deployment notes in README files
- [ ] Docker/IaC assets (not implemented yet)
- [ ] Automated CI/CD pipeline (not implemented yet)

## Current Product Status
- [x] Core MVP loop is complete end-to-end:
  - auth -> meal logging -> dashboard -> history correction -> chat
- [x] Backend and frontend feature parity is in place for core flows
- [ ] Production hardening remains:
  - automated tests expansion
  - rate limiting / deeper security controls
  - observability depth (metrics/tracing)

## Documentation and Report Alignment Status
- [x] Auth narrative updated to bearer-token model
- [x] Abstract reduced below 300 words in report draft
- [ ] Remaining report TODOs:
  - mandatory front matter sections
  - required diagrams (use case, class, ER, deployment, flow)
  - deployment section write-up
  - final conclusion and references
  - benchmark evidence for one flagship feature
