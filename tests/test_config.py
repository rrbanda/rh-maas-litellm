"""Tests for MaaSConfig."""

import os
import pytest
from rh_maas_litellm import MaaSConfig


def test_defaults_from_env(monkeypatch):
    monkeypatch.setenv("MAAS_BASE_URL", "https://maas.example.com")
    monkeypatch.setenv("MAAS_API_KEY", "sk-test-key")
    monkeypatch.delenv("MAAS_URL_PATH", raising=False)
    monkeypatch.delenv("MAAS_SSL_VERIFY", raising=False)

    cfg = MaaSConfig()
    assert cfg.base_url == "https://maas.example.com"
    assert cfg.api_key == "sk-test-key"
    assert cfg.url_path == "/gemini-external/{model}/v1"
    assert cfg.ssl_verify is False
    assert cfg.is_configured is True


def test_explicit_values():
    cfg = MaaSConfig(
        base_url="https://custom.maas.com",
        api_key="sk-custom",
        url_path="/v1/models/{model}",
        ssl_verify=True,
    )
    assert cfg.is_configured is True
    assert cfg.ssl_verify is True


def test_api_base_interpolates_model():
    cfg = MaaSConfig(
        base_url="https://maas.example.com",
        api_key="sk-test",
        url_path="/gemini-external/{model}/v1",
    )
    assert cfg.api_base("gemini-2.5-flash") == (
        "https://maas.example.com/gemini-external/gemini-2.5-flash/v1"
    )


def test_base_url_trailing_slash_stripped(monkeypatch):
    monkeypatch.setenv("MAAS_BASE_URL", "https://maas.example.com/")
    monkeypatch.setenv("MAAS_API_KEY", "sk-x")
    cfg = MaaSConfig()
    assert not cfg.base_url.endswith("/")


def test_not_configured_when_empty():
    cfg = MaaSConfig(base_url="", api_key="")
    assert cfg.is_configured is False

    cfg2 = MaaSConfig(base_url="https://maas.example.com", api_key="")
    assert cfg2.is_configured is False


def test_ssl_verify_true_from_env(monkeypatch):
    monkeypatch.setenv("MAAS_SSL_VERIFY", "true")
    monkeypatch.setenv("MAAS_BASE_URL", "https://x.com")
    monkeypatch.setenv("MAAS_API_KEY", "k")
    cfg = MaaSConfig()
    assert cfg.ssl_verify is True


def test_ssl_verify_false_variants(monkeypatch):
    for val in ("false", "False", "FALSE", "0", ""):
        monkeypatch.setenv("MAAS_SSL_VERIFY", val)
        monkeypatch.setenv("MAAS_BASE_URL", "https://x.com")
        monkeypatch.setenv("MAAS_API_KEY", "k")
        cfg = MaaSConfig()
        assert cfg.ssl_verify is False, f"Expected False for MAAS_SSL_VERIFY={val!r}"
