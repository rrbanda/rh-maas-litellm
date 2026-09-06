"""bootstrap() — apply litellm patches required for Red Hat MaaS compatibility."""


def bootstrap(ssl_verify: bool = False) -> None:
    """Patch litellm and the Google ADK LiteLlm adapter for Red Hat MaaS.

    Two patches are applied:

    1. **SSL verification** — Red Hat internal MaaS endpoints commonly use
       self-signed TLS certificates. ``litellm.ssl_verify`` is set to
       ``ssl_verify`` (defaults to False). Set ``ssl_verify=True`` when the
       endpoint has a CA-signed certificate.

    2. **PDF inline injection** — When the model string starts with ``openai/``,
       ADK's LiteLlm adapter classifies the provider as ``openai`` and tries to
       upload PDFs via ``litellm.acreate_file()`` before sending the chat
       request. MaaS does not implement a file-upload endpoint. Patching
       ``_MEDIA_URL_CONTENT_TYPE_BY_MAJOR_MIME_TYPE["application"] = "image_url"``
       routes ``application/pdf`` inline data through the ``image_url`` branch
       instead, sending PDFs as base64 data URIs which MaaS accepts.

    Call this function once, before creating any :class:`MaaSLiteLlm` instance::

        import rh_maas_litellm
        rh_maas_litellm.bootstrap()

        # or with SSL verification enabled:
        rh_maas_litellm.bootstrap(ssl_verify=True)

    Args:
        ssl_verify: Whether to verify the MaaS endpoint's TLS certificate.
                    Defaults to ``False``.
    """
    import litellm
    from google.adk.models import lite_llm as _lite_llm_module

    litellm.ssl_verify = ssl_verify
    _lite_llm_module._MEDIA_URL_CONTENT_TYPE_BY_MAJOR_MIME_TYPE["application"] = "image_url"
