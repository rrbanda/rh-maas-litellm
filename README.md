# rh-maas-litellm

Google ADK `LiteLlm` adapter for **Red Hat MaaS** (Model-as-a-Service) — an OpenAI-compatible Gemini proxy used in Red Hat OpenShift AI environments.

## What it solves

When building [Google ADK](https://github.com/google/adk-python) agents against a Red Hat MaaS endpoint, two problems appear immediately:

| Problem | Symptom | Fix |
|---|---|---|
| **tools + response_format conflict** | HTTP 400: `"Function calling with a response mime type: 'application/json' is unsupported"` | Override `LlmCapabilities` so ADK uses its `SetModelResponseTool` fallback |
| **PDF file-upload path** | MaaS returns 404/500 on file upload | Patch ADK's MIME routing so PDFs are sent as base64 `image_url` data URIs |

This package applies both fixes in one import.

---

## Install

```bash
# From PyPI
pip install rh-maas-litellm

# From GitHub (latest main)
pip install git+https://github.com/rrbanda/rh-maas-litellm.git
```

---

## Quick start

```python
import rh_maas_litellm
from google.adk.agents import LlmAgent
from google.adk.apps import App

# 1. Patch litellm once at startup (SSL + PDF routing)
rh_maas_litellm.bootstrap()

# 2. Create your agent — model reads from MAAS_BASE_URL / MAAS_API_KEY env vars
agent = LlmAgent(
    name="MyAgent",
    model=rh_maas_litellm.get_maas_model("gemini-2.5-flash"),
    instruction="You are a helpful assistant.",
)

app = App(name="my_app", root_agent=agent)
```

Set environment variables:

```bash
export MAAS_BASE_URL=https://maas.apps.ocp.example.com
export MAAS_API_KEY=sk-oai-...
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MAAS_BASE_URL` | *(required)* | Base URL of the MaaS proxy |
| `MAAS_API_KEY` | *(required)* | Bearer token / API key |
| `MAAS_URL_PATH` | `/gemini-external/{model}/v1` | Path template; `{model}` is replaced with the model name |
| `MAAS_SSL_VERIFY` | `false` | Set to `true` for endpoints with a CA-signed cert |

---

## Red Hat MaaS model endpoints

| Model | Path |
|---|---|
| `gemini-2.5-flash` | `/gemini-external/gemini-2.5-flash/v1` |
| `gemini-2.5-pro` | `/gemini-external/gemini-2.5-pro/v1` |
| `gemini-3.5-flash` | `/gemini-external/gemini-3.5-flash/v1` |
| `gemini-3.5-flash-lite` | `/gemini-external/gemini-3.5-flash-lite/v1` |
| `gemini-3.7-flash` | `/gemini-external/gemini-3.7-flash/v1` |

---

## API reference

### `bootstrap(ssl_verify=False)`

Apply litellm patches. Call once before creating any model instance.

```python
rh_maas_litellm.bootstrap()           # self-signed cert (default)
rh_maas_litellm.bootstrap(ssl_verify=True)  # CA-signed cert
```

### `get_maas_model(model_name, config=None) → MaaSLiteLlm`

Create a `MaaSLiteLlm` ready to pass to an ADK agent.

```python
# From environment variables
model = rh_maas_litellm.get_maas_model("gemini-2.5-flash")

# From explicit config
from rh_maas_litellm import MaaSConfig
cfg = MaaSConfig(
    base_url="https://maas.apps.ocp.example.com",
    api_key="sk-oai-...",
    ssl_verify=False,
)
model = rh_maas_litellm.get_maas_model("gemini-2.5-pro", config=cfg)
```

Raises `ValueError` if `MAAS_BASE_URL` or `MAAS_API_KEY` are not set.

### `MaaSLiteLlm`

Subclass of `google.adk.models.lite_llm.LiteLlm`. You can construct it directly if you need full control:

```python
from rh_maas_litellm import MaaSLiteLlm

model = MaaSLiteLlm(
    model="openai/gemini-2.5-flash",
    api_base="https://maas.apps.ocp.example.com/gemini-external/gemini-2.5-flash/v1",
    api_key="sk-oai-...",
    drop_params=True,
)
```

### `MaaSConfig`

Dataclass holding connection settings. All fields have env-var defaults read at instantiation time (not import time), so `dotenv.load_dotenv()` works correctly when called before constructing `MaaSConfig`.

```python
from rh_maas_litellm import MaaSConfig

cfg = MaaSConfig()            # reads from env vars
cfg = MaaSConfig(             # explicit
    base_url="https://...",
    api_key="sk-...",
    url_path="/gemini-external/{model}/v1",
    ssl_verify=False,
)
cfg.is_configured             # True if base_url and api_key are non-empty
cfg.api_base("gemini-2.5-flash")  # → full URL for that model
```

---

## How it works

### Fix 1 — capabilities override

ADK checks `model.capabilities.output_schema_and_tools` to decide whether to send structured output alongside function-calling tools in the same request. When this is `True` (the default for `LiteLlm`), ADK sends both `tools` and `response_format: {type: "json_schema"}` in one request — which MaaS rejects.

`MaaSLiteLlm` overrides `capabilities` to return `LlmCapabilities(output_schema_and_tools=False)`. ADK then injects a `SetModelResponseTool` into the agent's tool list. The agent calls its regular tools first, then calls `set_model_response` as a tool to submit structured output. No conflicting fields in a single request.

### Fix 2 — PDF inline routing

ADK's `LiteLlm` inspects the model string prefix. When it starts with `openai/`, ADK classifies the provider as `openai`, which is listed in `_FILE_ID_REQUIRED_PROVIDERS`. This causes ADK to call `litellm.acreate_file()` to upload PDFs before sending them in a chat request — but MaaS has no file upload endpoint.

`bootstrap()` patches `_MEDIA_URL_CONTENT_TYPE_BY_MAJOR_MIME_TYPE["application"] = "image_url"`. This routes `application/pdf` inline data through the `image_url` branch instead: PDFs are base64-encoded and sent as `data:application/pdf;base64,...` data URIs, which MaaS accepts.

---

## Development

```bash
git clone https://github.com/rrbanda/rh-maas-litellm.git
cd rh-maas-litellm
pip install -e ".[dev]"
pytest tests/ -v
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
