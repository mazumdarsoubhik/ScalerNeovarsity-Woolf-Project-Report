# NutriFlow Backend

NutriFlow backend is a modular-monolith FastAPI service focused on the core product loop:
- meal logging
- daily dashboard aggregation
- context-aware nutrition chat

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

## Core APIs

- `POST /api/v1/meals`
- `PATCH /api/v1/meals/{meal_id}`
- `DELETE /api/v1/meals/{meal_id}`
- `GET /api/v1/meals/history`
- `GET /api/v1/dashboard/today`
- `POST /api/v1/chat`
