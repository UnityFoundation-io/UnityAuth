"""Unit tests for the UnityAuth API client."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import requests

from unityauth_cli.client import UnityAuthAPIClient
from unityauth_cli.utils.errors import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    VersionMismatchError,
)


class TestClientInitialization:
    """Tests for UnityAuthAPIClient initialization."""

    def test_init_sets_base_url(self):
        """Should set base URL correctly."""
        client = UnityAuthAPIClient("https://auth.example.com")
        assert client.base_url == "https://auth.example.com"

    def test_init_strips_trailing_slash(self):
        """Should strip trailing slash from base URL."""
        client = UnityAuthAPIClient("https://auth.example.com/")
        assert client.base_url == "https://auth.example.com"

    def test_init_sets_default_timeout(self):
        """Should use default timeout of 30 seconds."""
        client = UnityAuthAPIClient("https://auth.example.com")
        assert client.timeout == 30

    def test_init_accepts_custom_timeout(self):
        """Should accept custom timeout."""
        client = UnityAuthAPIClient("https://auth.example.com", timeout=60)
        assert client.timeout == 60

    def test_init_sets_token(self):
        """Should set Authorization header when token provided."""
        client = UnityAuthAPIClient("https://auth.example.com", token="test-token")
        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer test-token"

    def test_init_without_token(self):
        """Should not set Authorization header when no token provided."""
        client = UnityAuthAPIClient("https://auth.example.com")
        assert "Authorization" not in client.session.headers

    def test_init_sets_user_agent(self):
        """Should set User-Agent header."""
        client = UnityAuthAPIClient("https://auth.example.com")
        assert "User-Agent" in client.session.headers
        assert "unityauth-cli" in client.session.headers["User-Agent"]

    def test_init_sets_content_type(self):
        """Should set Content-Type to application/json."""
        client = UnityAuthAPIClient("https://auth.example.com")
        assert client.session.headers["Content-Type"] == "application/json"


class TestTokenManagement:
    """Tests for token management methods."""

    def test_set_token(self):
        """Should set Authorization header."""
        client = UnityAuthAPIClient("https://auth.example.com")
        client.set_token("new-token")
        assert client.session.headers["Authorization"] == "Bearer new-token"

    def test_clear_token(self):
        """Should remove Authorization header."""
        client = UnityAuthAPIClient("https://auth.example.com", token="test-token")
        client.clear_token()
        assert "Authorization" not in client.session.headers

    def test_clear_token_when_not_set(self):
        """Should not raise error when clearing non-existent token."""
        client = UnityAuthAPIClient("https://auth.example.com")
        client.clear_token()  # Should not raise
        assert "Authorization" not in client.session.headers


class TestHTTPMethods:
    """Tests for HTTP method wrappers."""

    @pytest.fixture
    def client(self):
        """Create a client with mocked session."""
        with patch('unityauth_cli.client.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.headers = {}

            client = UnityAuthAPIClient("https://auth.example.com")
            client.session = mock_session
            yield client

    def test_get_request(self, client):
        """Should make GET request to correct URL."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        result = client.get("/api/users")

        client.session.request.assert_called_once()
        call_args = client.session.request.call_args
        assert call_args[0] == ("GET", "https://auth.example.com/api/users")
        assert result == {"data": "test"}

    def test_post_request_with_data(self, client):
        """Should make POST request with JSON data."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{"id": 1}'
        mock_response.json.return_value = {"id": 1}
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        result = client.post("/api/users", data={"email": "test@example.com"})

        client.session.request.assert_called_once()
        call_args = client.session.request.call_args
        assert call_args[0] == ("POST", "https://auth.example.com/api/users")
        assert call_args[1]["json"] == {"email": "test@example.com"}

    def test_put_request(self, client):
        """Should make PUT request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        client.put("/api/users/1", data={"name": "Updated"})

        call_args = client.session.request.call_args
        assert call_args[0] == ("PUT", "https://auth.example.com/api/users/1")

    def test_patch_request(self, client):
        """Should make PATCH request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        client.patch("/api/users/1", data={"roles": [1, 2]})

        call_args = client.session.request.call_args
        assert call_args[0] == ("PATCH", "https://auth.example.com/api/users/1")

    def test_delete_request(self, client):
        """Should make DELETE request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b''
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        result = client.delete("/api/users/1")

        call_args = client.session.request.call_args
        assert call_args[0] == ("DELETE", "https://auth.example.com/api/users/1")
        assert result is None  # Empty response

    def test_empty_response_returns_none(self, client):
        """Should return None for empty response body."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b''
        mock_response.headers = {}
        client.session.request.return_value = mock_response

        result = client.get("/api/logout")

        assert result is None


class TestErrorHandling:
    """Tests for HTTP error handling."""

    @pytest.fixture
    def client(self):
        """Create a client with mocked session."""
        with patch('unityauth_cli.client.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.headers = {}

            client = UnityAuthAPIClient("https://auth.example.com")
            client.session = mock_session
            yield client

    def _make_error_response(self, status_code, message=None, headers=None):
        """Helper to create mock error responses."""
        response = MagicMock()
        response.ok = False
        response.status_code = status_code
        response.headers = headers or {}

        if message:
            response.json.return_value = {"message": message}
            response.text = message
        else:
            response.json.side_effect = ValueError("No JSON")
            response.text = f"HTTP {status_code}"

        return response

    def test_401_raises_authentication_error(self, client):
        """Should raise AuthenticationError for 401 response."""
        client.session.request.return_value = self._make_error_response(
            401, "Invalid credentials"
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.get("/api/users")

        assert "Authentication failed" in exc_info.value.message
        assert "unityauth login" in exc_info.value.details

    def test_403_raises_authorization_error(self, client):
        """Should raise AuthorizationError for 403 response."""
        client.session.request.return_value = self._make_error_response(
            403, "Insufficient permissions"
        )

        with pytest.raises(AuthorizationError) as exc_info:
            client.get("/api/admin")

        assert "Permission denied" in exc_info.value.message
        assert "administrator" in exc_info.value.details.lower()

    def test_404_raises_not_found_error(self, client):
        """Should raise NotFoundError for 404 response."""
        client.session.request.return_value = self._make_error_response(
            404, "User not found"
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.get("/api/users/999")

        assert "not found" in exc_info.value.message.lower()

    def test_400_raises_validation_error(self, client):
        """Should raise ValidationError for 400 response."""
        client.session.request.return_value = self._make_error_response(
            400, "Email is required"
        )

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={})

        assert "Invalid request" in exc_info.value.message

    def test_422_raises_validation_error(self, client):
        """Should raise ValidationError for 422 response."""
        client.session.request.return_value = self._make_error_response(
            422, "Invalid email format"
        )

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={"email": "invalid"})

        assert "Validation failed" in exc_info.value.message

    def test_429_raises_rate_limit_error(self, client):
        """Should raise RateLimitError for 429 response."""
        client.session.request.return_value = self._make_error_response(
            429, "Too many requests", headers={"Retry-After": "120"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.get("/api/users")

        assert "Rate limit" in exc_info.value.message
        assert exc_info.value.retry_after == 120

    def test_429_uses_default_retry_after(self, client):
        """Should use default retry-after when header missing."""
        client.session.request.return_value = self._make_error_response(
            429, "Too many requests"
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.get("/api/users")

        assert exc_info.value.retry_after == 60  # Default

    def test_500_raises_server_error(self, client):
        """Should raise ServerError for 500 response."""
        client.session.request.return_value = self._make_error_response(
            500, "Internal server error"
        )

        with pytest.raises(ServerError) as exc_info:
            client.get("/api/users")

        assert exc_info.value.status_code == 500

    def test_503_raises_server_error(self, client):
        """Should raise ServerError for 503 response."""
        client.session.request.return_value = self._make_error_response(
            503, "Service unavailable"
        )

        with pytest.raises(ServerError) as exc_info:
            client.get("/api/users")

        assert exc_info.value.status_code == 503


class TestNetworkErrors:
    """Tests for network error handling."""

    @pytest.fixture
    def client(self):
        """Create a client with mocked session."""
        with patch('unityauth_cli.client.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.headers = {}

            client = UnityAuthAPIClient("https://auth.example.com")
            client.session = mock_session
            yield client

    def test_connection_error_raises_network_error(self, client):
        """Should raise NetworkError for connection failures."""
        client.session.request.side_effect = requests.ConnectionError("Connection refused")

        with pytest.raises(NetworkError) as exc_info:
            client.get("/api/users")

        assert "Could not connect" in exc_info.value.message
        assert "auth.example.com" in exc_info.value.message

    def test_timeout_raises_network_error(self, client):
        """Should raise NetworkError for request timeouts."""
        client.session.request.side_effect = requests.Timeout("Request timed out")

        with pytest.raises(NetworkError) as exc_info:
            client.get("/api/users")

        assert "timed out" in exc_info.value.message.lower()

    def test_generic_request_exception_raises_network_error(self, client):
        """Should raise NetworkError for other request exceptions."""
        client.session.request.side_effect = requests.RequestException("Unknown error")

        with pytest.raises(NetworkError) as exc_info:
            client.get("/api/users")

        assert "Network error" in exc_info.value.message


class TestErrorMessageExtraction:
    """Tests for extracting error messages from responses."""

    @pytest.fixture
    def client(self):
        """Create a client with mocked session."""
        with patch('unityauth_cli.client.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.headers = {}

            client = UnityAuthAPIClient("https://auth.example.com")
            client.session = mock_session
            yield client

    def test_extracts_message_field(self, client):
        """Should extract 'message' field from error response."""
        response = MagicMock()
        response.ok = False
        response.status_code = 400
        response.headers = {}
        response.json.return_value = {"message": "Email is required"}
        response.text = "some text"
        client.session.request.return_value = response

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={})

        assert "Email is required" in exc_info.value.message

    def test_extracts_error_field(self, client):
        """Should extract 'error' field from error response."""
        response = MagicMock()
        response.ok = False
        response.status_code = 400
        response.headers = {}
        response.json.return_value = {"error": "Bad request format"}
        response.text = "some text"
        client.session.request.return_value = response

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={})

        assert "Bad request format" in exc_info.value.message

    def test_extracts_embedded_message(self, client):
        """Should extract '_embedded.message' field from error response."""
        response = MagicMock()
        response.ok = False
        response.status_code = 400
        response.headers = {}
        response.json.return_value = {"_embedded": {"message": "Validation error"}}
        response.text = "some text"
        client.session.request.return_value = response

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={})

        assert "Validation error" in exc_info.value.message

    def test_falls_back_to_response_text(self, client):
        """Should use response text when JSON parsing fails."""
        response = MagicMock()
        response.ok = False
        response.status_code = 400
        response.headers = {}
        response.json.side_effect = ValueError("No JSON")
        response.text = "Plain text error message"
        client.session.request.return_value = response

        with pytest.raises(ValidationError) as exc_info:
            client.post("/api/users", data={})

        assert "Plain text error message" in exc_info.value.message


class TestRequestTimeout:
    """Tests for request timeout handling."""

    def test_uses_configured_timeout(self):
        """Should use configured timeout for requests."""
        with patch('unityauth_cli.client.requests.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            mock_session.headers = {}

            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.content = b'{}'
            mock_response.json.return_value = {}
            mock_response.headers = {}
            mock_session.request.return_value = mock_response

            client = UnityAuthAPIClient("https://auth.example.com", timeout=45)
            client.session = mock_session

            client.get("/api/users")

            call_kwargs = mock_session.request.call_args[1]
            assert call_kwargs["timeout"] == 45
