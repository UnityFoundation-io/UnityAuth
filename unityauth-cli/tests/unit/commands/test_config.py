"""Tests for configuration management commands."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from unityauth_cli.commands.config import _flatten_config, _convert_value
from unityauth_cli.cli import cli, register_commands


# Register commands once for all tests
register_commands()


class TestShowCommand:
    """Tests for the config show command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_show_success(self, runner):
        """Test successful config display."""
        mock_config = MagicMock()
        mock_config.config = {
            'api_url': 'https://auth.example.com',
            'default_format': 'table'
        }
        mock_config.config_path = Path('/home/user/.config/unityauth-cli/config.yml')

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            with patch('unityauth_cli.commands.config.console'):
                with patch('unityauth_cli.commands.config.format_key_value_table', return_value='table'):
                    result = runner.invoke(cli, ['config', 'show'])

        assert result.exit_code == 0

    def test_show_json_format(self, runner):
        """Test config display in JSON format."""
        mock_config = MagicMock()
        mock_config.config = {'api_url': 'https://auth.example.com'}
        mock_config.config_path = Path('/home/user/.config/unityauth-cli/config.yml')

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            with patch('unityauth_cli.commands.config.console'):
                with patch('unityauth_cli.commands.config.format_json') as mock_format:
                    mock_format.return_value = '{"api_url": "https://auth.example.com"}'
                    result = runner.invoke(cli, ['--format', 'json', 'config', 'show'])

        assert result.exit_code == 0
        mock_format.assert_called_once()


class TestSetCommand:
    """Tests for the config set command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_set_string_value(self, runner):
        """Test setting a string value."""
        mock_config = MagicMock()
        mock_config.config = {}
        mock_config.config_path = Path('/home/user/.config/unityauth-cli/config.yml')

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            result = runner.invoke(cli, ['config', 'set', 'api_url', 'https://new.example.com'])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with('api_url', 'https://new.example.com')
        mock_config.save.assert_called_once()

    def test_set_integer_value(self, runner):
        """Test setting an integer value."""
        mock_config = MagicMock()
        mock_config.config = {}
        mock_config.config_path = Path('/home/user/.config/unityauth-cli/config.yml')

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            result = runner.invoke(cli, ['config', 'set', 'timeout', '60'])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with('timeout', 60)

    def test_set_boolean_value(self, runner):
        """Test setting a boolean value."""
        mock_config = MagicMock()
        mock_config.config = {}
        mock_config.config_path = Path('/home/user/.config/unityauth-cli/config.yml')

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            result = runner.invoke(cli, ['config', 'set', 'verbose', 'true'])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with('verbose', True)


class TestEditCommand:
    """Tests for the config edit command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_edit_success(self, runner):
        """Test successful config edit."""
        mock_config = MagicMock()
        mock_config.config_path = MagicMock(spec=Path)
        mock_config.config_path.exists.return_value = True
        mock_config.config_path.__str__ = lambda self: '/home/user/.config/unityauth-cli/config.yml'

        with patch('unityauth_cli.cli.Configuration', return_value=mock_config):
            with patch.dict('os.environ', {'EDITOR': 'nano'}):
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = MagicMock(returncode=0)
                    result = runner.invoke(cli, ['config', 'edit'])

        assert result.exit_code == 0
        mock_config.load.assert_called_once()


class TestFlattenConfig:
    """Tests for the _flatten_config helper function."""

    def test_flatten_simple_dict(self):
        """Test flattening a simple dictionary."""
        config = {'api_url': 'https://example.com', 'timeout': 30}
        result = _flatten_config(config)
        assert result == {'api_url': 'https://example.com', 'timeout': 30}

    def test_flatten_nested_dict(self):
        """Test flattening a nested dictionary."""
        config = {
            'api_url': 'https://example.com',
            'batch': {
                'max_size': 100,
                'continue_on_error': False
            }
        }
        result = _flatten_config(config)
        assert result == {
            'api_url': 'https://example.com',
            'batch.max_size': 100,
            'batch.continue_on_error': False
        }

    def test_flatten_deeply_nested_dict(self):
        """Test flattening a deeply nested dictionary."""
        config = {
            'level1': {
                'level2': {
                    'level3': 'value'
                }
            }
        }
        result = _flatten_config(config)
        assert result == {'level1.level2.level3': 'value'}

    def test_flatten_empty_dict(self):
        """Test flattening an empty dictionary."""
        result = _flatten_config({})
        assert result == {}


class TestConvertValue:
    """Tests for the _convert_value helper function."""

    def test_convert_boolean_true_variations(self):
        """Test conversion of various true values."""
        assert _convert_value('true') is True
        assert _convert_value('True') is True
        assert _convert_value('TRUE') is True
        assert _convert_value('yes') is True
        assert _convert_value('on') is True

    def test_convert_boolean_false_variations(self):
        """Test conversion of various false values."""
        assert _convert_value('false') is False
        assert _convert_value('False') is False
        assert _convert_value('FALSE') is False
        assert _convert_value('no') is False
        assert _convert_value('off') is False

    def test_convert_integer(self):
        """Test conversion of integer values."""
        assert _convert_value('42') == 42
        assert _convert_value('-10') == -10

    def test_convert_float(self):
        """Test conversion of float values."""
        assert _convert_value('3.14') == 3.14
        assert _convert_value('-2.5') == -2.5

    def test_convert_string(self):
        """Test conversion of string values."""
        assert _convert_value('hello') == 'hello'
        assert _convert_value('https://example.com') == 'https://example.com'
        assert _convert_value('') == ''
