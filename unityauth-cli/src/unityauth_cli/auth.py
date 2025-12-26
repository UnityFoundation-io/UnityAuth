"""Authentication module for UnityAuth CLI.

Handles token storage and retrieval using OS-native secure storage (keyring).
"""

from typing import Optional

import keyring

from unityauth_cli.utils.errors import AuthenticationError

# Service name for keyring storage
SERVICE_NAME = "unityauth-cli"


def store_token(api_url: str, token: str) -> None:
    """Store JWT token in OS-native secure storage.

    Args:
        api_url: API endpoint URL (used as username for keyring)
        token: JWT bearer token to store

    Raises:
        AuthenticationError: If token storage fails
    """
    try:
        keyring.set_password(SERVICE_NAME, api_url, token)
    except Exception as e:
        raise AuthenticationError(
            f"Failed to store authentication token: {e}",
            "Check that your OS keyring service is available"
        ) from e


def get_token(api_url: str) -> Optional[str]:
    """Retrieve JWT token from OS-native secure storage.

    Args:
        api_url: API endpoint URL (used as username for keyring)

    Returns:
        JWT bearer token if found, None otherwise

    Raises:
        AuthenticationError: If token retrieval fails
    """
    try:
        return keyring.get_password(SERVICE_NAME, api_url)
    except Exception as e:
        raise AuthenticationError(
            f"Failed to retrieve authentication token: {e}",
            "Check that your OS keyring service is available"
        ) from e


def delete_token(api_url: str) -> None:
    """Delete JWT token from OS-native secure storage.

    Args:
        api_url: API endpoint URL (used as username for keyring)

    Raises:
        AuthenticationError: If token deletion fails
    """
    try:
        keyring.delete_password(SERVICE_NAME, api_url)
    except keyring.errors.PasswordDeleteError:
        # Token doesn't exist - not an error
        pass
    except Exception as e:
        raise AuthenticationError(
            f"Failed to delete authentication token: {e}",
            "Check that your OS keyring service is available"
        ) from e


def has_token(api_url: str) -> bool:
    """Check if a token exists for the given API URL.

    Args:
        api_url: API endpoint URL

    Returns:
        True if token exists, False otherwise
    """
    token = get_token(api_url)
    return token is not None
