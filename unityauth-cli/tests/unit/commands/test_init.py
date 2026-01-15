"""Tests for init command (setup wizard)."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from click.testing import CliRunner

from unityauth_cli.cli import cli, register_commands


# Register commands once for all tests
register_commands()


class TestInitCommand:
    """Tests for the init command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_init_help(self, runner):
        """Test init --help shows correct information."""
        result = runner.invoke(cli, ['init', '--help'])

        assert result.exit_code == 0
        assert 'Initialize UnityAuth CLI' in result.output
        assert '--api-url' in result.output
        assert '--skip-login' in result.output
        assert '--allow-http' in result.output

    def test_init_requires_api_url_non_interactive(self, runner):
        """Test init fails without API URL in non-interactive mode."""
        result = runner.invoke(cli, ['init'])

        # Should fail because we're in non-interactive mode (no TTY)
        assert result.exit_code != 0
        assert 'API URL required' in result.output or 'Aborted' in result.output

    def test_init_invalid_url_format(self, runner):
        """Test init rejects invalid URL format."""
        result = runner.invoke(cli, [
            'init',
            '--api-url', 'not-a-url',
            '--skip-login'
        ])

        assert result.exit_code != 0
        assert 'Invalid URL' in result.output or 'https://' in result.output

    def test_init_rejects_http_by_default(self, runner):
        """Test init rejects HTTP URLs without --allow-http flag."""
        result = runner.invoke(cli, [
            'init',
            '--api-url', 'http://auth.example.com',
            '--skip-login'
        ])

        assert result.exit_code != 0
        assert 'HTTP' in result.output or 'insecure' in result.output.lower()

    def test_init_allows_http_with_flag(self, runner):
        """Test init accepts HTTP URLs with --allow-http flag."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.save'):
                result = runner.invoke(cli, [
                    'init',
                    '--api-url', 'http://localhost:8081',
                    '--skip-login',
                    '--allow-http'
                ])

        assert result.exit_code == 0
        assert 'Connection successful' in result.output

    def test_init_success_with_valid_url(self, runner):
        """Test successful init with valid HTTPS URL."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.save'):
                result = runner.invoke(cli, [
                    'init',
                    '--api-url', 'https://auth.example.com',
                    '--skip-login'
                ])

        assert result.exit_code == 0
        assert 'Welcome to UnityAuth CLI' in result.output
        assert 'Connection successful' in result.output
        assert 'Configuration saved' in result.output
        assert 'Setup complete' in result.output

    def test_init_shows_next_steps(self, runner):
        """Test init shows helpful next steps after completion."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.save'):
                result = runner.invoke(cli, [
                    'init',
                    '--api-url', 'https://auth.example.com',
                    '--skip-login'
                ])

        assert result.exit_code == 0
        assert 'Next steps' in result.output
        assert 'tenant list' in result.output
        assert 'user list' in result.output

    def test_init_connection_failure_prompts_continue(self, runner):
        """Test init handles connection failure gracefully."""
        import requests

        with patch('unityauth_cli.commands.init.requests.get', side_effect=requests.ConnectionError()):
            result = runner.invoke(cli, [
                'init',
                '--api-url', 'https://auth.example.com',
                '--skip-login'
            ], input='n\n')  # Answer 'no' to continue prompt

        assert 'Could not connect' in result.output
        assert 'cancelled' in result.output.lower() or result.exit_code == 0

    def test_init_connection_failure_can_continue(self, runner):
        """Test init can continue after connection failure if user confirms."""
        import requests

        with patch('unityauth_cli.commands.init.requests.get', side_effect=requests.ConnectionError()):
            with patch('unityauth_cli.config.Configuration.save'):
                result = runner.invoke(cli, [
                    'init',
                    '--api-url', 'https://auth.example.com',
                    '--skip-login'
                ], input='y\n')  # Answer 'yes' to continue prompt

        assert result.exit_code == 0
        assert 'Configuration saved' in result.output

    def test_init_server_error_prompts_continue(self, runner):
        """Test init handles server errors gracefully."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            result = runner.invoke(cli, [
                'init',
                '--api-url', 'https://auth.example.com',
                '--skip-login'
            ], input='n\n')  # Answer 'no' to continue prompt

        assert 'status 500' in result.output
        assert result.exit_code == 0

    def test_init_skip_login_flag(self, runner):
        """Test --skip-login flag skips the login prompt."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.save'):
                result = runner.invoke(cli, [
                    'init',
                    '--api-url', 'https://auth.example.com',
                    '--skip-login'
                ])

        assert result.exit_code == 0
        # Should not prompt for login
        assert 'Email:' not in result.output
        assert 'Password:' not in result.output

    def test_init_saves_api_url_to_config(self, runner):
        """Test init saves API URL to configuration."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        saved_values = {}

        def mock_set(key, value):
            saved_values[key] = value

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.set', side_effect=mock_set):
                with patch('unityauth_cli.config.Configuration.save'):
                    result = runner.invoke(cli, [
                        'init',
                        '--api-url', 'https://auth.example.com',
                        '--skip-login'
                    ])

        assert result.exit_code == 0
        assert saved_values.get('api_url') == 'https://auth.example.com'

    def test_init_strips_trailing_slash(self, runner):
        """Test init strips trailing slash from API URL."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        saved_values = {}

        def mock_set(key, value):
            saved_values[key] = value

        with patch('unityauth_cli.commands.init.requests.get', return_value=mock_response):
            with patch('unityauth_cli.config.Configuration.set', side_effect=mock_set):
                with patch('unityauth_cli.config.Configuration.save'):
                    result = runner.invoke(cli, [
                        'init',
                        '--api-url', 'https://auth.example.com/',
                        '--skip-login'
                    ])

        assert result.exit_code == 0
        assert saved_values.get('api_url') == 'https://auth.example.com'
