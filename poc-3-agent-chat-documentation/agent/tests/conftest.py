import pytest


@pytest.fixture(autouse=True)
def base_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017/outline_rag_test")
    monkeypatch.setenv("OUTLINE_BASE_URL", "https://outline.example.test")
    monkeypatch.setenv("OUTLINE_API_TOKEN", "ol_test")
    monkeypatch.setenv("OUTLINE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "slack_test")

    from agent.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
