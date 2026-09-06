"""Tests for MaaSLiteLlm."""

import pytest
from unittest.mock import patch
from rh_maas_litellm import MaaSLiteLlm


def _make_model(**kwargs) -> MaaSLiteLlm:
    defaults = dict(
        model="openai/gemini-2.5-flash",
        api_base="https://maas.example.com/gemini-external/gemini-2.5-flash/v1",
        api_key="sk-test",
    )
    defaults.update(kwargs)
    return MaaSLiteLlm(**defaults)


def test_capabilities_output_schema_and_tools_false():
    model = _make_model()
    assert model.capabilities.output_schema_and_tools is False


def test_is_subclass_of_litellm():
    from google.adk.models.lite_llm import LiteLlm
    model = _make_model()
    assert isinstance(model, LiteLlm)


def test_model_string_stored():
    model = _make_model(model="openai/gemini-2.5-pro")
    assert model.model == "openai/gemini-2.5-pro"


def test_drop_params_accepted():
    # Should not raise
    model = _make_model(drop_params=True)
    assert model is not None
