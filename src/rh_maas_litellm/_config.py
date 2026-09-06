"""MaaSConfig — connection settings for Red Hat MaaS endpoints."""

import os
from dataclasses import dataclass, field


@dataclass
class MaaSConfig:
    """Connection settings for a Red Hat MaaS (OpenAI-compatible) endpoint.

    All fields default to env-var reads at *instantiation* time, not at import
    time. This means dotenv.load_dotenv() can be called before the first
    MaaSConfig() call and the values will be picked up correctly.

    Environment variables:
        MAAS_BASE_URL    Base URL of the MaaS proxy, e.g.
                         https://maas.apps.ocp.example.com
        MAAS_API_KEY     Bearer token / API key for authentication.
        MAAS_URL_PATH    Path template for per-model routing. The literal
                         ``{model}`` is replaced with the model name.
                         Default: /gemini-external/{model}/v1
        MAAS_SSL_VERIFY  Set to "true" to enable TLS certificate verification.
                         Default: "false" (Red Hat internal endpoints commonly
                         use self-signed certificates).
    """

    base_url: str = field(
        default_factory=lambda: os.getenv("MAAS_BASE_URL", "").rstrip("/")
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("MAAS_API_KEY", "")
    )
    url_path: str = field(
        default_factory=lambda: os.getenv(
            "MAAS_URL_PATH", "/gemini-external/{model}/v1"
        )
    )
    ssl_verify: bool = field(
        default_factory=lambda: os.getenv("MAAS_SSL_VERIFY", "false").lower() == "true"
    )

    def api_base(self, model_name: str) -> str:
        """Return the full API base URL for the given model name."""
        return self.base_url + self.url_path.format(model=model_name)

    @property
    def is_configured(self) -> bool:
        """True when both base_url and api_key are non-empty."""
        return bool(self.base_url and self.api_key)
