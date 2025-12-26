"""Unit tests for the auth module (token storage/retrieval)."""

import pytest
from unittest.mock import MagicMock, patch

from unityauth_cli import auth
from unityauth_cli.utils.errors import AuthenticationError


class TestStoreToken:
    """Tests for auth.store_token()."""

    def test_store_token_success(self, mock_keyring):
        """Should store token in keyring successfully."""
        api_url = "https://auth.example.com"
        token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"

        auth.store_token(api_url, token)

        mock_keyring.set_password.assert_called_once_with(
            auth.SERVICE_NAME, api_url, token
        )

    def test_store_token_keyring_failure(self, mock_keyring):
        """Should raise AuthenticationError when keyring fails."""
        mock_keyring.set_password.side_effect = Exception("Keyring unavailable")

        with pytest.raises(AuthenticationError) as exc_info:
            auth.store_token("https://auth.example.com", "token")

        assert "Failed to store authentication token" in exc_info.value.message
        assert "keyring service" in exc_info.value.details.lower()


class TestGetToken:
    """Tests for auth.get_token()."""

    def test_get_token_success(self, mock_keyring):
        """Should retrieve token from keyring."""
        api_url = "https://auth.example.com"
        expected_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
        mock_keyring.get_password.return_value = expected_token

        token = auth.get_token(api_url)

        assert token == expected_token
        mock_keyring.get_password.assert_called_once_with(auth.SERVICE_NAME, api_url)

    def test_get_token_not_found(self, mock_keyring):
        """Should return None when no token exists."""
        mock_keyring.get_password.return_value = None

        token = auth.get_token("https://auth.example.com")

        assert token is None

    def test_get_token_keyring_failure(self, mock_keyring):
        """Should raise AuthenticationError when keyring fails."""
        mock_keyring.get_password.side_effect = Exception("Keyring unavailable")

        with pytest.raises(AuthenticationError) as exc_info:
            auth.get_token("https://auth.example.com")

        assert "Failed to retrieve authentication token" in exc_info.value.message


class TestDeleteToken:
    """Tests for auth.delete_token()."""

    def test_delete_token_success(self, mock_keyring):
        """Should delete token from keyring."""
        api_url = "https://auth.example.com"

        auth.delete_token(api_url)

        mock_keyring.delete_password.assert_called_once_with(auth.SERVICE_NAME, api_url)

    def test_delete_token_not_found(self):
        """Should not raise error when token doesn't exist."""
        with patch('unityauth_cli.auth.keyring') as mock_keyring:
            # Create a mock PasswordDeleteError exception class
            PasswordDeleteError = type('PasswordDeleteError', (Exception,), {})
            mock_keyring.errors.PasswordDeleteError = PasswordDeleteError
            mock_keyring.delete_password.side_effect = PasswordDeleteError()

            # Should not raise
            auth.delete_token("https://auth.example.com")

    def test_delete_token_keyring_failure(self):
        """Should raise AuthenticationError on unexpected keyring failure."""
        with patch('unityauth_cli.auth.keyring') as mock_keyring:
            # Set up PasswordDeleteError as a real exception class
            mock_keyring.errors.PasswordDeleteError = type(
                'PasswordDeleteError', (Exception,), {}
            )
            mock_keyring.delete_password.side_effect = RuntimeError("Unexpected error")

            with pytest.raises(AuthenticationError) as exc_info:
                auth.delete_token("https://auth.example.com")

            assert "Failed to delete authentication token" in exc_info.value.message


class TestHasToken:
    """Tests for auth.has_token()."""

    def test_has_token_true(self, mock_keyring):
        """Should return True when token exists."""
        mock_keyring.get_password.return_value = "some-token"

        result = auth.has_token("https://auth.example.com")

        assert result is True

    def test_has_token_false(self, mock_keyring):
        """Should return False when no token exists."""
        mock_keyring.get_password.return_value = None

        result = auth.has_token("https://auth.example.com")

        assert result is False


class TestServiceName:
    """Tests for service name constant."""

    def test_service_name_is_correct(self):
        """Service name should be 'unityauth-cli'."""
        assert auth.SERVICE_NAME == "unityauth-cli"
