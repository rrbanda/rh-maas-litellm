"""MaaSLiteLlm — Google ADK LiteLlm subclass for Red Hat MaaS endpoints."""

from google.adk.models._capabilities import LlmCapabilities
from google.adk.models.lite_llm import LiteLlm


class MaaSLiteLlm(LiteLlm):
    """ADK ``LiteLlm`` subclass for OpenAI-compatible Red Hat MaaS endpoints.

    Overrides :attr:`capabilities` to return
    ``LlmCapabilities(output_schema_and_tools=False)``.

    **Why this is needed:**

    When an ADK agent has both ``tools`` and ``output_schema``, ADK normally
    sends a single request containing both function-calling tool declarations
    *and* a ``response_format: {type: "json_schema", ...}`` constraint. The
    Red Hat MaaS endpoint rejects this combination with HTTP 400:
    ``"Function calling with a response mime type: 'application/json' is
    unsupported"``.

    Setting ``output_schema_and_tools=False`` tells ADK's
    ``_OutputSchemaRequestProcessor`` that the model cannot handle both at
    once. ADK then injects a synthetic ``SetModelResponseTool`` into the tool
    list. The agent calls its regular tools first, then calls
    ``set_model_response`` to submit structured output as a tool response —
    no ``response_format`` is sent in the same request as other tools.

    Usage::

        from rh_maas_litellm import MaaSLiteLlm

        model = MaaSLiteLlm(
            model="openai/gemini-2.5-flash",
            api_base="https://maas.example.com/gemini-external/gemini-2.5-flash/v1",
            api_key="sk-...",
            drop_params=True,
        )
    """

    @property
    def capabilities(self) -> LlmCapabilities:
        return LlmCapabilities(output_schema_and_tools=False)
