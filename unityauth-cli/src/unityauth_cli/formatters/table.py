"""Table formatter using tabulate library.

Provides human-readable ASCII/Unicode table output.
"""

from typing import Any, List, Dict

from tabulate import tabulate


def format_table(
    data: List[Dict[str, Any]],
    headers: str = "keys",
    table_format: str = "grid",
    show_headers: bool = True
) -> str:
    """Format data as a table.

    Args:
        data: List of dictionaries to display
        headers: Header mode - "keys" uses dict keys, "firstrow" uses first row,
                or list of custom headers (default: "keys")
        table_format: Table style - "grid", "simple", "plain", "fancy_grid", etc.
                     (default: "grid")
        show_headers: Whether to show column headers (default: True)

    Returns:
        Formatted table as string
    """
    if not data:
        return "No data to display"

    # If headers are disabled, use empty list
    if not show_headers:
        headers = []

    return tabulate(data, headers=headers, tablefmt=table_format)


def format_key_value_table(data: Dict[str, Any], table_format: str = "grid") -> str:
    """Format key-value pairs as a two-column table.

    Args:
        data: Dictionary of key-value pairs
        table_format: Table style (default: "grid")

    Returns:
        Formatted table as string
    """
    if not data:
        return "No data to display"

    # Convert to list of [key, value] pairs
    rows = [[key, value] for key, value in data.items()]

    return tabulate(rows, headers=["Field", "Value"], tablefmt=table_format)


def format_list(items: List[str], prefix: str = "- ") -> str:
    """Format a list of items with a prefix.

    Args:
        items: List of strings to format
        prefix: Prefix for each line (default: "- ")

    Returns:
        Formatted list as string
    """
    if not items:
        return "No items to display"

    return "\n".join(f"{prefix}{item}" for item in items)
