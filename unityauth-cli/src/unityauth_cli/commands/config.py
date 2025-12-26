"""Configuration management commands: show, set, edit.

Handles CLI configuration file operations.
"""

import os
import subprocess
import sys

import click

from unityauth_cli.cli import CLIContext, console, error, info, pass_context, success
from unityauth_cli.formatters.table import format_key_value_table
from unityauth_cli.formatters.json_fmt import format_json


@click.group()
def config() -> None:
    """Manage CLI configuration settings.

    View and modify configuration stored in ~/.config/unityauth-cli/config.yml

    \b
    Examples:
      unityauth config show                              # Display current config
      unityauth config set api_url https://auth.example.com
      unityauth config set default_format json
      unityauth config edit                              # Open in editor
    """
    pass


@config.command()
@pass_context
def show(ctx: CLIContext) -> None:
    """Display current configuration settings.

    Shows all configuration values from the config file.

    \b
    Examples:
      unityauth config show
      unityauth config show --format json
    """
    try:
        if not ctx.config:
            error("Configuration not loaded")
            sys.exit(4)

        # Get all config values
        config_data = ctx.config.config

        # Format output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(config_data))
        else:
            # Flatten nested config for table display
            flat_config = _flatten_config(config_data)
            console.print(format_key_value_table(flat_config))

        info(f"\nConfiguration file: {ctx.config.config_path}")

    except Exception as e:
        from unityauth_cli.cli import handle_error
        handle_error(e)


@config.command()
@click.argument('key')
@click.argument('value')
@pass_context
def set(ctx: CLIContext, key: str, value: str) -> None:
    """Set a configuration value.

    KEY is the configuration key (supports dot notation like 'batch.max_size')
    VALUE is the value to set

    \b
    Examples:
      unityauth config set api_url https://auth.example.com
      unityauth config set default_format json
      unityauth config set timeout 60
      unityauth config set batch.max_size 500
      unityauth config set batch.continue_on_error true
    """
    try:
        if not ctx.config:
            error("Configuration not loaded")
            sys.exit(4)

        # Convert value to appropriate type
        converted_value = _convert_value(value)

        # Set the value
        ctx.config.set(key, converted_value)

        # Save configuration
        ctx.config.save()

        success(f"Configuration updated: {key} = {converted_value}")

        if ctx.verbose:
            info(f"Configuration saved to {ctx.config.config_path}")

    except Exception as e:
        from unityauth_cli.cli import handle_error
        handle_error(e)


@config.command()
@pass_context
def edit(ctx: CLIContext) -> None:
    """Open configuration file in default editor.

    Opens the YAML configuration file in your default text editor.
    Falls back to vi/nano if no editor is configured.

    \b
    Examples:
      unityauth config edit
      EDITOR=nano unityauth config edit
    """
    try:
        if not ctx.config:
            error("Configuration not loaded")
            sys.exit(4)

        config_path = ctx.config.config_path

        # Create config file if it doesn't exist
        if not config_path.exists():
            ctx.config.save()
            info(f"Created new configuration file at {config_path}")

        # Determine editor to use
        editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')

        if not editor:
            # Try common editors
            for candidate in ['nano', 'vi', 'vim', 'notepad']:
                if subprocess.run(['which', candidate], capture_output=True).returncode == 0:
                    editor = candidate
                    break

        if not editor:
            error(
                "No text editor found",
                "Set EDITOR environment variable: export EDITOR=nano"
            )
            sys.exit(4)

        # Open editor
        if ctx.verbose:
            info(f"Opening {config_path} with {editor}...")

        result = subprocess.run([editor, str(config_path)])

        if result.returncode == 0:
            # Reload configuration to validate changes
            ctx.config.load()
            success("Configuration file updated")
        else:
            error(f"Editor exited with code {result.returncode}")
            sys.exit(1)

    except Exception as e:
        from unityauth_cli.cli import handle_error
        handle_error(e)


def _flatten_config(config: dict, prefix: str = '') -> dict:
    """Flatten nested configuration dictionary.

    Args:
        config: Configuration dictionary
        prefix: Key prefix for nested values

    Returns:
        Flattened dictionary with dot-notation keys
    """
    flat = {}
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            flat.update(_flatten_config(value, full_key))
        else:
            flat[full_key] = value

    return flat


def _convert_value(value: str):
    """Convert string value to appropriate Python type.

    Args:
        value: String value to convert

    Returns:
        Converted value (int, bool, or str)
    """
    # Try boolean
    if value.lower() in ('true', 'yes', 'on', '1'):
        return True
    if value.lower() in ('false', 'no', 'off', '0'):
        return False

    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Return as string
    return value
