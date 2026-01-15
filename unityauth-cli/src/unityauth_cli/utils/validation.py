"""Input validation utilities for UnityAuth CLI.

Provides validation functions for email, password, and other user inputs.
"""

import re
from typing import List


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise
    """
    if not email:
        return False

    # Simple email regex - matches most valid email formats
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 8) -> bool:
    """Validate password meets minimum requirements.

    Args:
        password: Password to validate
        min_length: Minimum password length (default: 8)

    Returns:
        True if password is valid, False otherwise
    """
    return bool(password) and len(password) >= min_length


def validate_name(name: str, field_name: str = "Name", max_length: int = 100) -> List[str]:
    """Validate name field (firstName, lastName).

    Args:
        name: Name to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length (default: 100)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not name or name.strip() == "":
        errors.append(f"{field_name} must not be blank")
    elif len(name) > max_length:
        errors.append(f"{field_name} must be at most {max_length} characters")

    return errors


def validate_tenant_id(tenant_id: int) -> bool:
    """Validate tenant ID is a positive integer.

    Args:
        tenant_id: Tenant ID to validate

    Returns:
        True if valid, False otherwise
    """
    return isinstance(tenant_id, int) and tenant_id > 0


def validate_role_ids(role_ids: str) -> List[int]:
    """Parse and validate comma or pipe-separated role IDs.

    Args:
        role_ids: String of role IDs separated by commas or pipes (e.g., "1,2,3" or "1|2|3")

    Returns:
        List of integer role IDs

    Raises:
        ValueError: If any role ID is not a valid positive integer
    """
    if not role_ids:
        return []

    # Support both comma and pipe separators
    separator = '|' if '|' in role_ids else ','
    parts = [part.strip() for part in role_ids.split(separator)]

    result = []
    for part in parts:
        if not part:
            continue

        try:
            role_id = int(part)
            if role_id <= 0:
                raise ValueError(f"Role ID must be positive: {part}")
            result.append(role_id)
        except ValueError:
            raise ValueError(f"Invalid role ID (must be integer): {part}")

    return result


def validate_status(status: str) -> bool:
    """Validate user status value.

    Args:
        status: Status value to validate

    Returns:
        True if valid (ENABLED or DISABLED), False otherwise
    """
    return status.upper() in ('ENABLED', 'DISABLED')


def validate_url(url: str, require_https: bool = True) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate
        require_https: If True, only HTTPS URLs are valid (default: True)

    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False

    # Simple URL validation
    if require_https:
        return url.startswith('https://')
    else:
        return url.startswith('http://') or url.startswith('https://')
