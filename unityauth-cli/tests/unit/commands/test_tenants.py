"""Tests for tenant discovery commands."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from unityauth_cli.cli import cli, register_commands
from unityauth_cli.utils.errors import AuthorizationError


# Register commands once for all tests
register_commands()


class TestListTenantsCommand:
    """Tests for the tenant list command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_list_tenants_success(self, runner, mock_client):
        """Test successful tenant listing."""
        mock_client.get.return_value = [
            {'id': 1, 'name': 'Tenant One'},
            {'id': 2, 'name': 'Tenant Two'},
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_table') as mock_format:
                        mock_format.return_value = 'formatted table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'list'])

        assert result.exit_code == 0
        mock_client.get.assert_called_once_with('/api/tenants')
        mock_format.assert_called_once()

    def test_list_tenants_empty_response(self, runner, mock_client):
        """Test handling of empty response."""
        mock_client.get.return_value = None

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'list'])

        assert result.exit_code == 0
        assert 'No tenants found' in result.output

    def test_list_tenants_empty_list(self, runner, mock_client):
        """Test handling of empty list."""
        mock_client.get.return_value = []

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'list'])

        assert result.exit_code == 0
        assert 'No tenants found' in result.output

    def test_list_tenants_json_format(self, runner, mock_client):
        """Test JSON output format."""
        mock_client.get.return_value = [{'id': 1, 'name': 'Tenant'}]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_json') as mock_format:
                        mock_format.return_value = '[{"id": 1}]'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'json', 'tenant', 'list'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_tenants_csv_format(self, runner, mock_client):
        """Test CSV output format."""
        mock_client.get.return_value = [{'id': 1, 'name': 'Tenant'}]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_csv') as mock_format:
                        mock_format.return_value = 'id,name\n1,Tenant'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'csv', 'tenant', 'list'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_tenants_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.get.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'list'])

        assert result.exit_code == 3

    def test_list_tenants_verbose_output(self, runner, mock_client):
        """Test verbose output."""
        mock_client.get.return_value = [{'id': 1, 'name': 'Tenant'}]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_table', return_value='table'):
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--verbose', 'tenant', 'list'])

        assert result.exit_code == 0
        assert 'Total tenants' in result.output


class TestTenantUsersCommand:
    """Tests for the tenant users command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_tenant_users_success(self, runner, mock_client):
        """Test successful user listing for tenant."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user1@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]},
            {'id': 2, 'email': 'user2@example.com', 'firstName': 'User', 'lastName': 'Two', 'roles': [2, 3]},
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_table') as mock_format:
                        mock_format.return_value = 'formatted table'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'users', '1'])

        assert result.exit_code == 0
        mock_client.get.assert_called_once_with('/api/tenants/1/users')
        mock_format.assert_called_once()

    def test_tenant_users_empty_response(self, runner, mock_client):
        """Test handling of empty response."""
        mock_client.get.return_value = None

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'users', '1'])

        assert result.exit_code == 0
        assert 'No users found' in result.output

    def test_tenant_users_invalid_tenant_id(self, runner, mock_client):
        """Test that invalid tenant ID raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'users', '0'])

        assert result.exit_code != 0

    def test_tenant_users_negative_tenant_id(self, runner, mock_client):
        """Test that negative tenant ID raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'users', '-1'])

        # Click may reject negative integers, checking for non-zero exit
        assert result.exit_code != 0

    def test_tenant_users_json_format(self, runner, mock_client):
        """Test JSON output format."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_json') as mock_format:
                        mock_format.return_value = '[{"id": 1}]'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'json', 'tenant', 'users', '1'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_tenant_users_csv_format(self, runner, mock_client):
        """Test CSV output format."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_csv') as mock_format:
                        mock_format.return_value = 'csv,data'
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--format', 'csv', 'tenant', 'users', '1'])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_tenant_users_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.get.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', 'tenant', 'users', '1'])

        assert result.exit_code == 3

    def test_tenant_users_verbose_output(self, runner, mock_client):
        """Test verbose output."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.tenants.console'):
                    with patch('unityauth_cli.commands.tenants.format_table', return_value='table'):
                        result = runner.invoke(cli, ['--api-url', 'https://auth.example.com', '--verbose', 'tenant', 'users', '1'])

        assert result.exit_code == 0
        assert 'Total users' in result.output
