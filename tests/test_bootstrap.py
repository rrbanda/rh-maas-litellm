"""Tests for bootstrap()."""

import pytest
import litellm
from rh_maas_litellm import bootstrap


def test_bootstrap_sets_ssl_verify_false():
    bootstrap(ssl_verify=False)
    assert litellm.ssl_verify is False


def test_bootstrap_sets_ssl_verify_true():
    bootstrap(ssl_verify=True)
    assert litellm.ssl_verify is True
    # Reset to safe default
    bootstrap(ssl_verify=False)


def test_bootstrap_patches_pdf_mime():
    from google.adk.models import lite_llm as _m
    bootstrap()
    assert _m._MEDIA_URL_CONTENT_TYPE_BY_MAJOR_MIME_TYPE.get("application") == "image_url"


def test_bootstrap_idempotent():
    # Calling twice should not raise
    bootstrap()
    bootstrap()
