def test_settings_loads_from_env():
    from agent.config import get_settings

    settings = get_settings()

    assert settings.anthropic_api_key == "sk-ant-test"
    assert settings.mongodb_uri == "mongodb://localhost:27017/outline_rag_test"
    assert settings.outline_webhook_secret == "whsec_test"
