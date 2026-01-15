"""Tests for user management commands."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from unityauth_cli.cli import cli, register_commands
from unityauth_cli.utils.errors import AuthorizationError


# Register commands once for all tests
register_commands()


class TestCreateCommand:
    """Tests for the user create command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_create_user_success(self, runner, mock_client):
        """Test successful user creation."""
        mock_client.post.return_value = {
            'id': 1,
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'roles': [2, 3]
        }

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'create',
                    '--email', 'test@example.com',
                    '--first-name', 'Test',
                    '--last-name', 'User',
                    '--password', 'SecureP@ss123',
                    '--tenant-id', '1',
                    '--role-ids', '2,3'
                ])

        assert result.exit_code == 0
        mock_client.post.assert_called_once()
        assert 'created successfully' in result.output

    def test_create_user_invalid_email(self, runner, mock_client):
        """Test that invalid email format raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'create',
                    '--email', 'invalid-email',
                    '--first-name', 'Test',
                    '--last-name', 'User',
                    '--password', 'SecureP@ss123',
                    '--tenant-id', '1',
                    '--role-ids', '2'
                ])

        assert result.exit_code != 0

    def test_create_user_password_too_short(self, runner, mock_client):
        """Test that short password raises error."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'create',
                    '--email', 'test@example.com',
                    '--first-name', 'Test',
                    '--last-name', 'User',
                    '--password', 'short',
                    '--tenant-id', '1',
                    '--role-ids', '2'
                ])

        assert result.exit_code != 0

    def test_create_user_authorization_error(self, runner, mock_client):
        """Test that authorization error is handled correctly."""
        mock_client.post.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'create',
                    '--email', 'test@example.com',
                    '--first-name', 'Test',
                    '--last-name', 'User',
                    '--password', 'SecureP@ss123',
                    '--tenant-id', '1',
                    '--role-ids', '2'
                ])

        assert result.exit_code == 3


class TestUpdateCommand:
    """Tests for the user update command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_update_user_roles_success(self, runner, mock_client):
        """Test successful role update."""
        mock_client.patch.return_value = {
            'id': 5,
            'email': 'test@example.com',
            'roles': [1, 2]
        }

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'update',
                    '5',
                    '--tenant-id', '1',
                    '--role-ids', '1,2'
                ])

        assert result.exit_code == 0
        mock_client.patch.assert_called_once()
        assert 'updated successfully' in result.output

    def test_update_user_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.patch.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'update',
                    '5',
                    '--tenant-id', '1',
                    '--role-ids', '1,2'
                ])

        assert result.exit_code == 3


class TestUpdateProfileCommand:
    """Tests for the user update-profile command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_update_profile_first_name(self, runner, mock_client):
        """Test updating first name."""
        mock_client.patch.return_value = {'id': 5, 'firstName': 'NewName'}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'update-profile',
                    '5',
                    '--first-name', 'NewName'
                ])

        assert result.exit_code == 0
        mock_client.patch.assert_called_once()

    def test_update_profile_all_fields(self, runner, mock_client):
        """Test updating all fields at once."""
        mock_client.patch.return_value = {'id': 5}

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'update-profile',
                    '5',
                    '--first-name', 'John',
                    '--last-name', 'Smith',
                    '--password', 'NewSecureP@ss'
                ])

        assert result.exit_code == 0
        mock_client.patch.assert_called_once()

    def test_update_profile_no_fields_provided(self, runner, mock_client):
        """Test that error is raised when no fields provided."""
        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'update-profile',
                    '5'
                ])

        assert result.exit_code != 0


class TestListUsersCommand:
    """Tests for the user list command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_client(self):
        """Create a mock API client."""
        return MagicMock()

    def test_list_users_success(self, runner, mock_client):
        """Test successful user listing."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user1@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]},
            {'id': 2, 'email': 'user2@example.com', 'firstName': 'User', 'lastName': 'Two', 'roles': [2, 3]},
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.users.console'):
                    with patch('unityauth_cli.commands.users.format_table') as mock_format:
                        mock_format.return_value = 'formatted table'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            'user', 'list',
                            '--tenant-id', '1'
                        ])

        assert result.exit_code == 0
        mock_client.get.assert_called_once_with('/api/tenants/1/users')
        mock_format.assert_called_once()

    def test_list_users_empty_response(self, runner, mock_client):
        """Test handling of empty response."""
        mock_client.get.return_value = None

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'list',
                    '--tenant-id', '1'
                ])

        assert result.exit_code == 0
        assert 'No users found' in result.output

    def test_list_users_json_format(self, runner, mock_client):
        """Test JSON output format."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.users.console'):
                    with patch('unityauth_cli.commands.users.format_json') as mock_format:
                        mock_format.return_value = '{"users": []}'
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--format', 'json',
                            'user', 'list',
                            '--tenant-id', '1'
                        ])

        assert result.exit_code == 0
        mock_format.assert_called_once()

    def test_list_users_authorization_error(self, runner, mock_client):
        """Test authorization error handling."""
        mock_client.get.side_effect = AuthorizationError("Permission denied")

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                result = runner.invoke(cli, [
                    '--api-url', 'https://auth.example.com',
                    'user', 'list',
                    '--tenant-id', '1'
                ])

        assert result.exit_code == 3

    def test_list_users_verbose_output(self, runner, mock_client):
        """Test verbose output."""
        mock_client.get.return_value = [
            {'id': 1, 'email': 'user@example.com', 'firstName': 'User', 'lastName': 'One', 'roles': [1]}
        ]

        with patch('unityauth_cli.auth.get_token', return_value='fake-token'):
            with patch('unityauth_cli.client.UnityAuthAPIClient', return_value=mock_client):
                with patch('unityauth_cli.commands.users.console'):
                    with patch('unityauth_cli.commands.users.format_table', return_value='table'):
                        result = runner.invoke(cli, [
                            '--api-url', 'https://auth.example.com',
                            '--verbose',
                            'user', 'list',
                            '--tenant-id', '1'
                        ])

        assert result.exit_code == 0
        assert 'Total users' in result.output
