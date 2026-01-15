"""Tests for login/logout commands."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from unityauth_cli.cli import cli, register_commands
from unityauth_cli.utils.errors import AuthenticationError


# Register commands once for all tests
register_commands()


class TestLoginCommand:
    """Tests for the login command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_login_missing_email_non_interactive(self, runner):
        """Test login without email in non-interactive mode."""
        # In non-interactive mode (no TTY), missing email should fail
        result = runner.invoke(cli, [
            '--api-url', 'https://auth.example.com',
            'login',
            '--password', 'password123'
        ])

        # Should fail because we're in non-interactive mode and email is required
        assert result.exit_code != 0


class TestLogoutCommand:
    """Tests for the logout command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_logout_success(self, runner):
        """Test successful logout."""
        with patch('unityauth_cli.commands.login.auth.has_token', return_value=True):
            with patch('unityauth_cli.commands.login.auth.delete_token', return_value=True):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'logout'
                ])

        assert result.exit_code == 0
        assert 'logout' in result.output.lower() or 'successful' in result.output.lower()

    def test_logout_no_active_session(self, runner):
        """Test logout when no session exists."""
        with patch('unityauth_cli.commands.login.auth.has_token', return_value=False):
            result = runner.invoke(cli, [
                '--api-url', 'https://auth.example.com',
                'logout'
            ])

        # Should still succeed but with warning message
        assert result.exit_code == 0
        assert 'no active session' in result.output.lower()


class TestTokenInfoCommand:
    """Tests for the token-info command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_token_info_success(self, runner, mock_client):
        """Test successful token info retrieval."""
        mock_client.get.return_value = {
            'email': 'user@example.com',
            'name': 'Test User',
            'exp': 1704067200
        }

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.login.console'):
                    with patch('unityauth_cli.commands.login.format_key_value_table', return_value='table'):
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            'token-info'
                        ])

        assert result.exit_code == 0
        mock_client.get.assert_called_once_with('/api/token_info')

    def test_token_info_json_format(self, runner, mock_client):
        """Test token info in JSON format."""
        mock_client.get.return_value = {
            'email': 'user@example.com',
            'name': 'Test User'
        }

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.login.console'):
                    with patch('unityauth_cli.commands.login.format_json') as mock_format:
                        mock_format.return_value = '{"email": "user@example.com"}'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--format', 'json',
                            'token-info'
                        ])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_token_info_not_authenticated(self, runner):
        """Test token info when not authenticated."""
        with patch('unityauth_cli.auth.get_token', return_value=None):
            result = runner.invoke(cli, [
                '--api-url', 'https://auth.example.com',
                'token-info'
            ])

        # Should fail with authentication error
        assert result.exit_code != 0
