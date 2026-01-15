"""Unit tests for CLI decorators (require_auth, require_config)."""

import pytest
from unittest.mock import MagicMock, patch

from unityauth_cli.cli import CLIContext, require_auth, require_config
from unityauth_cli.utils.errors import AuthenticationError, ConfigurationError


class TestRequireConfig:
    """Tests for @require_config decorator."""

    def test_passes_when_api_url_configured(self):
        """Should call wrapped function when API URL is set."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"

        called = []

        @require_config
        def my_command(ctx):
            called.append(True)
            return "success"

        result = my_command(ctx)

        assert called == [True]
        assert result == "success"

    def test_raises_when_api_url_not_configured(self):
        """Should raise ConfigurationError when API URL is None."""
        ctx = CLIContext()
        ctx.api_url = None

        @require_config
        def my_command(ctx):
            return "should not reach"

        with pytest.raises(ConfigurationError) as exc_info:
            my_command(ctx)

        assert "API URL not configured" in exc_info.value.message
        assert "config set api_url" in exc_info.value.details

    def test_raises_when_api_url_empty_string(self):
        """Should raise ConfigurationError when API URL is empty string."""
        ctx = CLIContext()
        ctx.api_url = ""

        @require_config
        def my_command(ctx):
            return "should not reach"

        with pytest.raises(ConfigurationError):
            my_command(ctx)

    def test_preserves_function_metadata(self):
        """Should preserve wrapped function's name and docstring."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"

        @require_config
        def my_special_command(ctx):
            """This is a special command."""
            pass

        assert my_special_command.__name__ == "my_special_command"
        assert "special command" in my_special_command.__doc__


class TestRequireAuth:
    """Tests for @require_auth decorator."""

    @pytest.fixture
    def mock_auth(self):
        """Mock the auth module."""
        with patch('unityauth_cli.auth') as mock:
            yield mock

    @pytest.fixture
    def mock_client_class(self):
        """Mock the UnityAuthAPIClient class."""
        with patch('unityauth_cli.client.UnityAuthAPIClient') as mock:
            yield mock

    def test_raises_when_api_url_not_configured(self, mock_auth, mock_client_class):
        """Should raise ConfigurationError when API URL is None."""
        ctx = CLIContext()
        ctx.api_url = None

        @require_auth
        def my_command(ctx, client):
            return "should not reach"

        with pytest.raises(ConfigurationError) as exc_info:
            my_command(ctx)

        assert "API URL not configured" in exc_info.value.message

    def test_raises_when_not_authenticated(self, mock_auth, mock_client_class):
        """Should raise AuthenticationError when no token exists."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = None

        mock_auth.get_token.return_value = None

        @require_auth
        def my_command(ctx, client):
            return "should not reach"

        with pytest.raises(AuthenticationError) as exc_info:
            my_command(ctx)

        assert "Not authenticated" in exc_info.value.message
        assert "unityauth login" in exc_info.value.details

    def test_creates_client_and_passes_to_command(self, mock_auth, mock_client_class):
        """Should create API client and pass it to wrapped function."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = None

        mock_auth.get_token.return_value = "test-token"
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        received_client = []

        @require_auth
        def my_command(ctx, client):
            received_client.append(client)
            return "success"

        result = my_command(ctx)

        assert result == "success"
        assert received_client[0] is mock_client
        mock_client_class.assert_called_once_with(
            "https://auth.example.com",
            token="test-token",
            timeout=30
        )

    def test_uses_timeout_from_config(self, mock_auth, mock_client_class):
        """Should use timeout from configuration."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = MagicMock()
        ctx.config.get.return_value = 60  # Custom timeout

        mock_auth.get_token.return_value = "test-token"

        @require_auth
        def my_command(ctx, client):
            return "success"

        my_command(ctx)

        mock_client_class.assert_called_once_with(
            "https://auth.example.com",
            token="test-token",
            timeout=60
        )

    def test_uses_default_timeout_when_config_none(self, mock_auth, mock_client_class):
        """Should use default timeout when config is None."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = None

        mock_auth.get_token.return_value = "test-token"

        @require_auth
        def my_command(ctx, client):
            return "success"

        my_command(ctx)

        mock_client_class.assert_called_once_with(
            "https://auth.example.com",
            token="test-token",
            timeout=30  # Default
        )

    def test_passes_additional_args_to_command(self, mock_auth, mock_client_class):
        """Should pass additional arguments to wrapped function."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = None

        mock_auth.get_token.return_value = "test-token"

        received_args = []

        @require_auth
        def my_command(ctx, email, tenant_id, client):
            received_args.extend([email, tenant_id])
            return "success"

        my_command(ctx, "test@example.com", 123)

        assert received_args == ["test@example.com", 123]

    def test_passes_keyword_args_to_command(self, mock_auth, mock_client_class):
        """Should pass keyword arguments to wrapped function."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"
        ctx.config = None

        mock_auth.get_token.return_value = "test-token"

        received_kwargs = {}

        @require_auth
        def my_command(ctx, client, verbose=False, format="table"):
            received_kwargs.update({"verbose": verbose, "format": format})
            return "success"

        my_command(ctx, verbose=True, format="json")

        assert received_kwargs == {"verbose": True, "format": "json"}

    def test_preserves_function_metadata(self, mock_auth, mock_client_class):
        """Should preserve wrapped function's name and docstring."""
        ctx = CLIContext()
        ctx.api_url = "https://auth.example.com"

        @require_auth
        def create_user(ctx, client):
            """Create a new user account."""
            pass

        assert create_user.__name__ == "create_user"
        assert "Create a new user" in create_user.__doc__
