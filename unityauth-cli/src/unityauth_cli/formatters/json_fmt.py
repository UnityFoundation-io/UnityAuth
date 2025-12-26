"""JSON formatter for machine-readable output.

Provides JSON output suitable for piping to jq or other tools.
"""

import json
from typing import Any


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as pretty-printed JSON.

    Args:
        data: Data to format (must be JSON-serializable)
        indent: Number of spaces for indentation (default: 2)

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def format_json_compact(data: Any) -> str:
    """Format data as compact JSON (no whitespace).

    Args:
        data: Data to format (must be JSON-serializable)

    Returns:
        Compact JSON string
    """
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
