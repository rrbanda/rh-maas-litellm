"""get_maas_model() — convenience factory for MaaSLiteLlm instances."""

from __future__ import annotations

from rh_maas_litellm._config import MaaSConfig
from rh_maas_litellm._model import MaaSLiteLlm


def get_maas_model(
    model_name: str,
    config: MaaSConfig | None = None,
) -> MaaSLiteLlm:
    """Create a :class:`MaaSLiteLlm` instance for the given Gemini model.

    Reads connection settings from *config* if provided, otherwise from
    environment variables (via a fresh :class:`MaaSConfig` instantiation).

    Args:
        model_name: Gemini model identifier, e.g. ``"gemini-2.5-flash"``.
                    Used as ``openai/{model_name}`` in the litellm model string
                    and substituted into the URL path template.
        config:     Optional :class:`MaaSConfig`. When ``None`` (default),
                    connection settings are read from environment variables:
                    ``MAAS_BASE_URL``, ``MAAS_API_KEY``, ``MAAS_URL_PATH``,
                    ``MAAS_SSL_VERIFY``.

    Returns:
        A configured :class:`MaaSLiteLlm` instance ready to pass to an ADK
        ``LlmAgent`` as its ``model=`` argument.

    Raises:
        ValueError: If ``MAAS_BASE_URL`` or ``MAAS_API_KEY`` are empty (either
                    from env vars or the supplied config object).

    Example::

        from rh_maas_litellm import bootstrap, get_maas_model
        from google.adk.agents import LlmAgent

        bootstrap()  # apply litellm patches once

        agent = LlmAgent(
            name="MyAgent",
            model=get_maas_model("gemini-2.5-flash"),
            instruction="You are a helpful assistant.",
        )
    """
    cfg = config if config is not None else MaaSConfig()
    if not cfg.is_configured:
        raise ValueError(
            "MaaS endpoint is not configured. "
            "Set the MAAS_BASE_URL and MAAS_API_KEY environment variables, "
            "or pass a MaaSConfig object explicitly."
        )
    return MaaSLiteLlm(
        model=f"openai/{model_name}",
        api_base=cfg.api_base(model_name),
        api_key=cfg.api_key,
        # Strip Gemini-specific parameters (e.g. thinking_config) that the
        # OpenAI-compatible endpoint does not recognise.
        drop_params=True,
    )
