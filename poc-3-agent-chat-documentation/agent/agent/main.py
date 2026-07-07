from fastapi import FastAPI

from agent.webhooks.outline import router as outline_router
from agent.webhooks.slack_commands import router as slack_commands_router
from agent.webhooks.slack_events import router as slack_events_router

app = FastAPI(title="Outline RAG Agent")
app.include_router(outline_router)
app.include_router(slack_events_router)
app.include_router(slack_commands_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
