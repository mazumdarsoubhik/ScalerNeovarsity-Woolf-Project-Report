# 🧠 Agentic AI App – MVP Development Plan

## ✅ Phase 1: Project Bootstrapping
- [x] Create 4 GitHub repositories:
  - `frontend` – Streamlit UI
  - `backend` – FastAPI server
  - `agent-server` – Semantic Kernel-based agent handler
  - `tools-server` – FastMCP-based tools interface
- [ ] Add README, `.gitignore`, `requirements.txt`, and base folders

---

## 🗄️ Phase 2: Authentication & Database Setup
- [ ] Design PostgreSQL schema:
  - Tables: `Users`, `Sessions`, `Chats`, `Messages`, `Agents`
- [ ] Implement email-password signup with OTP email verification
- [ ] Add Google SSO login using OAuth 2.0
- [ ] Generate and manage JWT tokens for session auth
- [ ] Use Redis (optional) for session state or message queue

---

## 💬 Phase 3: Chat Messaging Backend
- [ ] Define models for messages (`sender`, `content`, `timestamp`, `agent_tag`)
- [ ] Create chat APIs:
  - `POST /chat/send`
  - `GET /chat/history`
- [ ] Implement Redis PubSub or a simple message queue system
- [ ] Queue messages for agent processing asynchronously

---

## 🧠 Phase 4: Agent & Tool Server Integration
- [ ] Setup `agent-server` using **Semantic Kernel**
  - Parse and route messages to tools using MCP protocol
- [ ] Setup `tools-server` using FastAPI
  - Create basic tool handlers for testing (e.g., echo tool)
- [ ] Implement MCP communication between agent and tools

---

## 🌐 Phase 5: Frontend (Streamlit)
- [ ] Build login screen:
  - Email/Password with OTP
  - Google SSO
- [ ] Build chat UI:
  - Message input
  - Display conversation history
  - Detect `@agentname` usage and format API payloads
- [ ] Connect to backend APIs for chat and login

---

## 🧭 Phase 6: Agent Features (MVP)
- [ ] `@LetsGoOut` agent:
  - Use geolocation + weather API
  - Suggest nearby pleasant places to visit
  - Show activities from Google Maps API
- [ ] `@DocumentQnA` agent:
  - Upload PDF → extract text → generate embeddings
  - Use vector search to answer queries
- [ ] Trigger email + optional push notification after response

---

## 📊 Phase 7: Admin Dashboard (Optional for MVP)
- [ ] Build simple dashboard in Streamlit or a separate admin panel
- [ ] Show metrics:
  - User signups
  - DAU (Daily Active Users)
  - LLM token usage
  - Feedback scores per session
- [ ] Store logs in database or external logging system

---

## 📌 Stretch Goals (Post-MVP)
- [ ] Multi-agent memory context sharing
- [ ] File-based knowledge agents (for research)
- [ ] Add analytics via Grafana or Google Analytics
