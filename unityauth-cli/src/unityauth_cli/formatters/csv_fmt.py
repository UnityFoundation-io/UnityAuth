"""CSV formatter for spreadsheet-compatible output.

Provides RFC 4180 compliant CSV output.
"""

import csv
import io
from typing import Any, List, Dict


def format_csv(data: List[Dict[str, Any]], fieldnames: List[str] = None) -> str:
    """Format data as CSV.

    Args:
        data: List of dictionaries to format
        fieldnames: Optional list of field names for header row.
                   If None, uses keys from first dictionary.

    Returns:
        CSV-formatted string
    """
    if not data:
        return ""

    # Determine fieldnames from first row if not provided
    if fieldnames is None:
        if isinstance(data[0], dict):
            fieldnames = list(data[0].keys())
        else:
            raise ValueError("Cannot determine CSV fieldnames from data")

    # Use StringIO to write CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')

    # Write header and rows
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()


def format_csv_from_rows(rows: List[List[Any]], header: List[str] = None) -> str:
    """Format list of rows as CSV.

    Args:
        rows: List of lists (each inner list is a row)
        header: Optional header row

    Returns:
        CSV-formatted string
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')

    # Write header if provided
    if header:
        writer.writerow(header)

    # Write data rows
    writer.writerows(rows)

    return output.getvalue()
