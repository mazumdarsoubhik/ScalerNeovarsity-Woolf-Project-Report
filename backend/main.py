from fastapi import FastAPI
from backend.routes import chat

app = FastAPI(
    title="🧠 Mental Health Advisor API",
    description="A minimal FastAPI wrapper around the mental-health LLM agent.",
    version="1.0.0",
)

# Include routes
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Mental Health Advisor API. POST to /chat to talk."}
