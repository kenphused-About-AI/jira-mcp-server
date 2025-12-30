# Import modules in a way that allows them to be used
from .config import *  # noqa: F401, F403
from .http_client import *  # noqa: F401, F403
from .jira_api import *  # noqa: F401, F403
from .sanitization import *  # noqa: F401, F403
from .server import *  # noqa: F401, F403
from .tools import *  # noqa: F401, F403

# Configure logging after imports
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,  # Use stdout as required by AGENTS.md
)

__all__ = ["execute_curl", "text_to_adf", "TOOL_HANDLERS", "app"]  # noqa: F405
