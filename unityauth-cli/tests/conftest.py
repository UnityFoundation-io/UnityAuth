"""Shared pytest fixtures for UnityAuth CLI tests."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from unityauth_cli.cli import CLIContext
from unityauth_cli.config import Configuration
from unityauth_cli.client import UnityAuthAPIClient


@pytest.fixture
def mock_config():
    """Create a mock Configuration object."""
    config = MagicMock(spec=Configuration)
    config.get.return_value = None
    config.config = {
        'api_url': 'https://auth.example.com',
        'timeout': 30,
        'default_format': 'table',
    }
    return config


@pytest.fixture
def cli_context(mock_config):
    """Create a CLIContext with mock configuration."""
    ctx = CLIContext()
    ctx.config = mock_config
    ctx.api_url = 'https://auth.example.com'
    ctx.output_format = 'table'
    ctx.verbose = False
    return ctx


@pytest.fixture
def mock_keyring():
    """Mock the keyring module."""
    with patch('unityauth_cli.auth.keyring') as mock:
        yield mock


@pytest.fixture
def mock_requests_session():
    """Mock requests.Session for API client tests."""
    with patch('unityauth_cli.client.requests.Session') as mock:
        session_instance = MagicMock()
        mock.return_value = session_instance
        yield session_instance


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_api_client():
    """Create a mock API client."""
    client = MagicMock(spec=UnityAuthAPIClient)
    client.get.return_value = None
    client.post.return_value = None
    client.patch.return_value = None
    client.delete.return_value = None
    return client
