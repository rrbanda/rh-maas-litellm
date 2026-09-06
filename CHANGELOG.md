# Changelog

## 0.1.0 (2026-09-06)

Initial release.

- `MaaSLiteLlm` — ADK `LiteLlm` subclass with `capabilities.output_schema_and_tools=False`
- `bootstrap()` — patches litellm SSL verification and ADK PDF MIME routing
- `MaaSConfig` — dataclass for MaaS connection settings with env-var defaults
- `get_maas_model()` — convenience factory; raises `ValueError` if not configured
