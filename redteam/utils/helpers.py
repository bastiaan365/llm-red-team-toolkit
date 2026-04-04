"""Helper utilities for the red team toolkit."""

import logging
import os
from typing import Any, Dict, Optional
import json

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def expand_env_vars(value: str) -> str:
    """Expand environment variables in a string.

    Args:
        value: String potentially containing ${VAR_NAME} patterns

    Returns:
        String with environment variables expanded

    Raises:
        ValueError: If a referenced environment variable is not set
    """
    import re

    def replace_var(match):
        var_name = match.group(1)
        if var_name not in os.environ:
            raise ValueError(f"Environment variable not set: {var_name}")
        return os.environ[var_name]

    return re.sub(r'\$\{([^}]+)\}', replace_var, value)


def load_json_safe(data: str) -> Dict[str, Any]:
    """Safely load JSON, returning empty dict on failure.

    Args:
        data: JSON string to parse

    Returns:
        Parsed JSON dictionary or empty dict if parsing fails
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, ValueError):
        return {}


def truncate_string(s: str, length: int = 100) -> str:
    """Truncate a string to specified length with ellipsis.

    Args:
        s: String to truncate
        length: Maximum length

    Returns:
        Truncated string
    """
    if len(s) <= length:
        return s
    return s[:length - 3] + "..."


def sanitize_for_html(text: str) -> str:
    """Escape special HTML characters.

    Args:
        text: Text to escape

    Returns:
        HTML-safe string
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def get_severity_color(severity: str) -> str:
    """Get HTML color for severity level.

    Args:
        severity: Severity level (critical, high, medium, low)

    Returns:
        Hex color code
    """
    colors = {
        "critical": "#dc3545",
        "high": "#fd7e14",
        "medium": "#ffc107",
        "low": "#28a745",
        "info": "#17a2b8",
    }
    return colors.get(severity.lower(), "#6c757d")
