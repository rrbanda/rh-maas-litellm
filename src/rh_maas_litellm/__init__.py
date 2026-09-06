"""rh-maas-litellm — Google ADK LiteLlm adapter for Red Hat MaaS.

Public API::

    from rh_maas_litellm import MaaSLiteLlm, MaaSConfig, bootstrap, get_maas_model

Typical usage::

    import rh_maas_litellm
    rh_maas_litellm.bootstrap()           # patch litellm once at startup

    model = rh_maas_litellm.get_maas_model("gemini-2.5-flash")
"""

from rh_maas_litellm._bootstrap import bootstrap
from rh_maas_litellm._config import MaaSConfig
from rh_maas_litellm._factory import get_maas_model
from rh_maas_litellm._model import MaaSLiteLlm

__all__ = ["MaaSLiteLlm", "MaaSConfig", "bootstrap", "get_maas_model"]
__version__ = "0.1.0"
