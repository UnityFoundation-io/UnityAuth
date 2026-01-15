"""UnityAuth API client for making HTTP requests.

Handles authentication, request/response processing, and error mapping.
"""

from typing import Any, Dict, Optional

import requests

from unityauth_cli import SUPPORTED_API_VERSION, __version__
from unityauth_cli.utils.errors import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    VersionMismatchError,
)


class UnityAuthAPIClient:
    """HTTP client for UnityAuth API.

    Manages sessions, authentication headers, and error handling.
    """

    def __init__(self, base_url: str, token: Optional[str] = None, timeout: int = 30) -> None:
        """Initialize API client.

        Args:
            base_url: Base URL of UnityAuth API (e.g., https://auth.example.com)
            token: Optional JWT bearer token for authentication
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'unityauth-cli/{__version__}',
            'Content-Type': 'application/json',
        })

        if token:
            self.set_token(token)

        self._version_checked = False

    def set_token(self, token: str) -> None:
        """Set authentication token for subsequent requests.

        Args:
            token: JWT bearer token
        """
        self.session.headers['Authorization'] = f'Bearer {token}'

    def clear_token(self) -> None:
        """Remove authentication token from session."""
        self.session.headers.pop('Authorization', None)

    def get(self, endpoint: str, **kwargs: Any) -> Any:
        """Make GET request to API.

        Args:
            endpoint: API endpoint path (e.g., /api/users)
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            Various UnityAuthCLIError subclasses based on response
        """
        return self._request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Make POST request to API.

        Args:
            endpoint: API endpoint path
            data: Request body as dictionary
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            Various UnityAuthCLIError subclasses based on response
        """
        return self._request('POST', endpoint, json=data, **kwargs)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Make PUT request to API.

        Args:
            endpoint: API endpoint path
            data: Request body as dictionary
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            Various UnityAuthCLIError subclasses based on response
        """
        return self._request('PUT', endpoint, json=data, **kwargs)

    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """Make PATCH request to API.

        Args:
            endpoint: API endpoint path
            data: Request body as dictionary
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            Various UnityAuthCLIError subclasses based on response
        """
        return self._request('PATCH', endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """Make DELETE request to API.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            Various UnityAuthCLIError subclasses based on response
        """
        return self._request('DELETE', endpoint, **kwargs)

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Internal method to make HTTP requests with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            Parsed JSON response or None

        Raises:
            NetworkError: On connection failures
            AuthenticationError: On 401 responses
            PermissionError: On 403 responses
            NotFoundError: On 404 responses
            ValidationError: On 400/422 responses
            RateLimitError: On 429 responses
            ServerError: On 5xx responses
        """
        url = f'{self.base_url}{endpoint}'
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)

            # Debug logging for troubleshooting
            # import sys
            # print(f"DEBUG: {method} {url} -> {response.status_code}", file=sys.stderr)
            # print(f"DEBUG: Response: {response.text[:200] if response.text else 'empty'}", file=sys.stderr)

            # Check version compatibility on first authenticated request
            if not self._version_checked and 'Authorization' in self.session.headers:
                self._check_version_compatibility(response)
                self._version_checked = True

            # Handle HTTP errors
            if not response.ok:
                self._handle_http_error(response)

            # Return JSON if present, otherwise None
            if response.content:
                return response.json()
            return None

        except requests.ConnectionError as e:
            raise NetworkError(
                f"Could not connect to {self.base_url}",
                f"Check API endpoint configuration: unityauth config show\n"
                f"Verify network connectivity: curl {self.base_url}/keys"
            ) from e
        except requests.Timeout as e:
            raise NetworkError(
                f"Request timed out after {self.timeout} seconds",
                "Increase timeout: unityauth config set timeout 60"
            ) from e
        except requests.RequestException as e:
            raise NetworkError(f"Network error: {e}") from e

    def _handle_http_error(self, response: requests.Response) -> None:
        """Map HTTP errors to custom exceptions.

        Args:
            response: HTTP response with error status

        Raises:
            Appropriate UnityAuthCLIError subclass
        """
        status_code = response.status_code

        # Try to extract error message from response
        message = None
        try:
            error_data = response.json()
            # Try multiple possible field names that different frameworks use
            message = (
                error_data.get('message') or
                error_data.get('error') or
                error_data.get('_embedded', {}).get('message') or
                error_data.get('title')
            )
        except Exception:
            pass

        # If no message found in JSON, use response text
        if not message:
            message = response.text if response.text else f"HTTP {status_code}"

        # Map status codes to exceptions
        if status_code == 401:
            raise AuthenticationError(
                f"Authentication failed: {message}",
                "Run: unityauth login"
            )
        elif status_code == 403:
            raise AuthorizationError(
                f"Permission denied: {message}",
                "Contact your administrator to grant required permissions"
            )
        elif status_code == 404:
            raise NotFoundError(f"Resource not found: {message}")
        elif status_code == 400:
            raise ValidationError(f"Invalid request: {message}")
        elif status_code == 422:
            raise ValidationError(f"Validation failed: {message}")
        elif status_code == 429:
            # Extract retry-after header if present
            retry_after = int(response.headers.get('Retry-After', 60))
            raise RateLimitError(
                f"Rate limit exceeded: {message}",
                retry_after=retry_after
            )
        elif status_code >= 500:
            raise ServerError(message, status_code=status_code)
        else:
            raise NetworkError(f"HTTP {status_code}: {message}")

    def _check_version_compatibility(self, response: requests.Response) -> None:
        """Check if CLI version is compatible with API version.

        Args:
            response: Response from API (may contain version header)

        Raises:
            VersionMismatchError: If versions are incompatible
        """
        # Check for version in response headers or body
        api_version = response.headers.get('X-API-Version')

        if not api_version:
            # Try to extract from response if it's token_info endpoint
            try:
                data = response.json()
                api_version = data.get('apiVersion')
            except Exception:
                pass

        if api_version and not api_version.startswith(SUPPORTED_API_VERSION):
            raise VersionMismatchError(
                f"API version {api_version} not compatible with CLI {SUPPORTED_API_VERSION}",
                f"Upgrade CLI: pip install --upgrade unityauth-cli"
            )
