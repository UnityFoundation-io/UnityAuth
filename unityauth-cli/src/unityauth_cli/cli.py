"""Main CLI command group for UnityAuth CLI.

Defines the root command and global options.
"""

import sys
from typing import Optional

import click
from rich.console import Console

from unityauth_cli import __version__
from unityauth_cli.config import Configuration
from unityauth_cli.utils.errors import UnityAuthCLIError

# Global console for Rich output
console = Console()


class CLIContext:
    """Context object passed to all CLI commands."""

    def __init__(self) -> None:
        """Initialize CLI context."""
        self.config: Optional[Configuration] = None
        self.api_url: Optional[str] = None
        self.output_format: str = "table"
        self.verbose: bool = False


pass_context = click.make_pass_decorator(CLIContext, ensure=True)


@click.group()
@click.option(
    '--api-url',
    envvar='UNITYAUTH_API_URL',
    help='UnityAuth API endpoint URL (overrides config file)',
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['table', 'json', 'csv'], case_sensitive=False),
    help='Output format (default: table)',
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose/debug output',
)
@click.version_option(version=__version__, prog_name='unityauth-cli')
@click.pass_context
def cli(ctx: click.Context, api_url: Optional[str], output_format: Optional[str], verbose: bool) -> None:
    """UnityAuth CLI - Command-line interface for UnityAuth administration.

    Manage users, roles, and permissions in UnityAuth from the command line.

    \b
    Common commands:
      unityauth login                    # Authenticate and store token
      unityauth user create ...          # Create a new user
      unityauth user list --tenant-id 1  # List users in tenant
      unityauth tenant list              # List accessible tenants
      unityauth batch create-users FILE  # Batch create from CSV

    For command-specific help:
      unityauth COMMAND --help
    """
    # Initialize CLI context
    cli_ctx = ctx.ensure_object(CLIContext)
    cli_ctx.verbose = verbose

    # Load configuration
    try:
        cli_ctx.config = Configuration()

        # Override API URL if provided
        if api_url:
            cli_ctx.api_url = api_url
        else:
            cli_ctx.api_url = cli_ctx.config.get('api_url')

        # Set output format
        if output_format:
            cli_ctx.output_format = output_format.lower()
        else:
            cli_ctx.output_format = cli_ctx.config.get('default_format', 'table')

    except Exception as e:
        error(f"Failed to initialize CLI: {e}")
        sys.exit(4)


def success(message: str) -> None:
    """Display success message in green.

    Args:
        message: Success message to display
    """
    console.print(f"✓ {message}", style="bold green")


def error(message: str, details: str = "") -> None:
    """Display error message in red.

    Args:
        message: Error message to display
        details: Optional additional details or guidance
    """
    console.print(f"✗ {message}", style="bold red")
    if details:
        console.print(f"→ {details}", style="yellow")


def warning(message: str) -> None:
    """Display warning message in yellow.

    Args:
        message: Warning message to display
    """
    console.print(f"⚠ {message}", style="bold yellow")


def info(message: str) -> None:
    """Display info message.

    Args:
        message: Info message to display
    """
    console.print(message)


def handle_error(e: Exception) -> None:
    """Handle CLI errors and exit with appropriate code.

    Args:
        e: Exception to handle
    """
    if isinstance(e, UnityAuthCLIError):
        error(e.message, e.details)
        sys.exit(e.exit_code)
    else:
        error(f"Unexpected error: {e}")
        sys.exit(1)


# Import and register commands
# Avoid circular imports by importing here rather than at module level
def register_commands() -> None:
    """Register all CLI commands with the main group."""
    from unityauth_cli.commands.login import login, logout, token_info
    from unityauth_cli.commands.config import config
    from unityauth_cli.commands.users import create, update, list_users

    # Register authentication commands
    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(token_info)

    # Register configuration commands
    cli.add_command(config)

    # Register user management commands
    @cli.group()
    def user():
        """User account management commands."""
        pass

    user.add_command(create)
    user.add_command(update)
    user.add_command(list_users, name='list')
