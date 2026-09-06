"""Tests for get_maas_model()."""

import pytest
from rh_maas_litellm import MaaSConfig, MaaSLiteLlm, get_maas_model


_GOOD_CONFIG = MaaSConfig(
    base_url="https://maas.example.com",
    api_key="sk-test",
    url_path="/gemini-external/{model}/v1",
    ssl_verify=False,
)


def test_returns_maas_litellm():
    model = get_maas_model("gemini-2.5-flash", config=_GOOD_CONFIG)
    assert isinstance(model, MaaSLiteLlm)


def test_model_string_prefixed_openai():
    model = get_maas_model("gemini-2.5-flash", config=_GOOD_CONFIG)
    assert model.model == "openai/gemini-2.5-flash"


def test_api_base_contains_model_name():
    # Verify the config builds the right URL (LiteLlm doesn't expose api_base as a field)
    assert "gemini-2.5-pro" in _GOOD_CONFIG.api_base("gemini-2.5-pro")
    model = get_maas_model("gemini-2.5-pro", config=_GOOD_CONFIG)
    assert isinstance(model, MaaSLiteLlm)
    assert model.model == "openai/gemini-2.5-pro"


def test_raises_when_not_configured():
    bad = MaaSConfig(base_url="", api_key="")
    with pytest.raises(ValueError, match="MAAS_BASE_URL"):
        get_maas_model("gemini-2.5-flash", config=bad)


def test_raises_when_no_api_key():
    bad = MaaSConfig(base_url="https://maas.example.com", api_key="")
    with pytest.raises(ValueError):
        get_maas_model("gemini-2.5-flash", config=bad)


def test_reads_from_env(monkeypatch):
    monkeypatch.setenv("MAAS_BASE_URL", "https://env.maas.com")
    monkeypatch.setenv("MAAS_API_KEY", "sk-env-key")
    monkeypatch.delenv("MAAS_URL_PATH", raising=False)

    model = get_maas_model("gemini-2.5-flash")
    assert isinstance(model, MaaSLiteLlm)
    assert model.model == "openai/gemini-2.5-flash"
    # Verify config picks up env vars correctly
    cfg = MaaSConfig()
    assert "env.maas.com" in cfg.api_base("gemini-2.5-flash")


def test_capabilities_output_schema_and_tools_false():
    model = get_maas_model("gemini-2.5-flash", config=_GOOD_CONFIG)
    assert model.capabilities.output_schema_and_tools is False
