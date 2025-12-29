"""Tests for permission discovery commands."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from unityauth_cli.cli import cli, register_commands
from unityauth_cli.utils.errors import AuthorizationError


# Register commands once for all tests
register_commands()


class TestListPermissionsCommand:
    """Tests for the permissions list command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_list_permissions_success(self, runner, mock_client):
        """Test successful permission listing."""
        mock_client.post.return_value = {
            'permissions': ['AUTH_SERVICE_VIEW-SYSTEM', 'AUTH_SERVICE_EDIT-TENANT']
        }

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.permissions.console'):
                    with patch('unityauth_cli.commands.permissions.format_table') as mock_format:
                        mock_format.return_value = 'formatted table'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            'permissions', 'list',
                            '--tenant-id', '1',
                            '--service-id', '1'
                        ])

        assert result.exit_code == 0
        mock_client.post.assert_called_once_with('/api/principal/permissions', data={
            'tenantId': 1,
            'serviceId': 1
        })
        mock_format.assert_called_once()

    def test_list_permissions_empty_response(self, runner, mock_client):
        """Test handling of empty permissions."""
        mock_client.post.return_value = {'permissions': []}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '1',
                    '--service-id', '1'
                ])

        assert result.exit_code == 0
        assert 'No permissions found' in result.output

    def test_list_permissions_null_response(self, runner, mock_client):
        """Test handling of null response."""
        mock_client.post.return_value = None

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '1',
                    '--service-id', '1'
                ])

        assert result.exit_code == 0
        assert 'No permissions found' in result.output

    def test_list_permissions_error_response(self, runner, mock_client):
        """Test handling of error response from API."""
        mock_client.post.return_value = {'errorMessage': 'No tenant found.'}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '1',
                    '--service-id', '1'
                ])

        assert result.exit_code == 1

    def test_list_permissions_json_format(self, runner, mock_client):
        """Test JSON output format."""
        mock_client.post.return_value = {'permissions': ['PERM1', 'PERM2']}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.permissions.console'):
                    with patch('unityauth_cli.commands.permissions.format_json') as mock_format:
                        mock_format.return_value = '{"permissions": ["PERM1"]}'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--format', 'json',
                            'permissions', 'list',
                            '--tenant-id', '1',
                            '--service-id', '1'
                        ])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_permissions_csv_format(self, runner, mock_client):
        """Test CSV output format."""
        mock_client.post.return_value = {'permissions': ['PERM1', 'PERM2']}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.permissions.console'):
                    with patch('unityauth_cli.commands.permissions.format_csv') as mock_format:
                        mock_format.return_value = 'permission\nPERM1\nPERM2'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--format', 'csv',
                            'permissions', 'list',
                            '--tenant-id', '1',
                            '--service-id', '1'
                        ])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_permissions_invalid_tenant_id(self, runner, mock_client):
        """Test that invalid tenant ID raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '0',
                    '--service-id', '1'
                ])

        assert result.exit_code != 0

    def test_list_permissions_invalid_service_id(self, runner, mock_client):
        """Test that invalid service ID raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '1',
                    '--service-id', '0'
                ])

        assert result.exit_code != 0

    def test_list_permissions_negative_ids(self, runner, mock_client):
        """Test that negative IDs raise error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '-1',
                    '--service-id', '-1'
                ])

        assert result.exit_code != 0

    def test_list_permissions_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.post.side_effect = AuthorizationError("Not authorized")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'permissions', 'list',
                    '--tenant-id', '1',
                    '--service-id', '1'
                ])

        assert result.exit_code == 3

    def test_list_permissions_verbose_output(self, runner, mock_client):
        """Test verbose output."""
        mock_client.post.return_value = {'permissions': ['PERM1', 'PERM2']}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.permissions.console'):
                    with patch('unityauth_cli.commands.permissions.format_table', return_value='table'):
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--verbose',
                            'permissions', 'list',
                            '--tenant-id', '1',
                            '--service-id', '1'
                        ])

        assert result.exit_code == 0
        assert 'Total permissions' in result.output
