"""Tests for role discovery commands."""

import pytest
from unittest.mock import MagicMock, patch
import click
from click.testing import CliRunner

from unityauth_cli.commands.roles import list_roles
from unityauth_cli.cli import cli, register_commands
from unityauth_cli.utils.errors import AuthorizationError


# Register commands once for all tests
register_commands()


class TestListRolesCommand:
    """Tests for the role list command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_list_roles_success(self, runner, mock_client):
        """Test successful role listing."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Unity Administrator', 'description': 'System admin role'},
            {'id': 2, 'name': 'Tenant Administrator', 'description': 'Tenant admin role'},
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_table') as mock_format:
                        mock_format.return_value = 'formatted table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        mock_client.get.assert_called_once_with('/api/roles')
        mock_format.assert_called_once()

    def test_list_roles_empty_response(self, runner, mock_client):
        """Test handling of empty response."""
        mock_client.get.return_value = None

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        assert 'No roles found' in result.output

    def test_list_roles_empty_list(self, runner, mock_client):
        """Test handling of empty list."""
        mock_client.get.return_value = []

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        assert 'No roles found' in result.output

    def test_list_roles_json_format(self, runner, mock_client):
        """Test JSON output format."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Admin', 'description': 'Admin role'}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_json') as mock_format:
                        mock_format.return_value = '[{"id": 1}]'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'json', 'role', 'list'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_roles_csv_format(self, runner, mock_client):
        """Test CSV output format."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Admin', 'description': 'Admin role'}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_csv') as mock_format:
                        mock_format.return_value = 'id,name,description\n1,Admin,Admin role'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'csv', 'role', 'list'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_roles_handles_null_description(self, runner, mock_client):
        """Test that null description is handled correctly."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Admin', 'description': None}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_table') as mock_format:
                        mock_format.return_value = 'table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        # Check that N/A is used for null description
        rows = mock_format.call_args[0][0]
        assert rows[0][2] == 'N/A'

    def test_list_roles_handles_empty_description(self, runner, mock_client):
        """Test that empty description is handled correctly."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Admin', 'description': ''}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_table') as mock_format:
                        mock_format.return_value = 'table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        # Check that N/A is used for empty description
        rows = mock_format.call_args[0][0]
        assert rows[0][2] == 'N/A'

    def test_list_roles_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.get.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 3

    def test_list_roles_verbose_output(self, runner, mock_client):
        """Test verbose output."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Admin', 'description': 'Admin role'},
            {'id': 2, 'name': 'User', 'description': 'User role'},
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_table', return_value='table'):
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--verbose', 'role', 'list'])

        assert result.exit_code == 0
        assert 'Total roles' in result.output

    def test_list_roles_single_role_as_dict(self, runner, mock_client):
        """Test handling when response is a single dict instead of list."""
        mock_client.get.return_value = {'id': 1, 'name': 'Admin', 'description': 'Role'}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.roles.console'):
                    with patch('unityauth_cli.commands.roles.format_table') as mock_format:
                        mock_format.return_value = 'table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        assert result.exit_code == 0
        # Should wrap single dict in list
        mock_format.assert_called_once()

    def test_list_roles_not_authenticated(self, runner):
        """Test that unauthenticated request fails with AuthenticationError."""
        with patch('unityauth_cli.auth.get_token', return_value=None):
            result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'role', 'list'])

        # AuthenticationError is raised but Click wraps it, resulting in exit code 1
        assert result.exit_code != 0
        assert result.exception is not None
