"""Main CLI command group for UnityAuth CLI.

Defines the root command and global options.
"""

import functools
import sys
from typing import Callable, Optional, TypeVar

import click
from rich.console import Console

from unityauth_cli import __version__
from unityauth_cli.config import Configuration
from unityauth_cli.utils.errors import AuthenticationError, ConfigurationError, UnityAuthCLIError

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

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., None])


def require_auth(f: F) -> F:
    """Decorator that ensures API URL is configured and user is authenticated.

    Checks that:
    1. API URL is configured (from config or --api-url flag)
    2. User has a valid token stored in the keyring
    3. Creates an API client and passes it as the 'client' keyword argument

    Must be used after @pass_context decorator.

    Example:
        @click.command()
        @pass_context
        @require_auth
        def my_command(ctx: CLIContext, client: UnityAuthAPIClient) -> None:
            # client is ready to use
            response = client.get('/api/users')
    """
    @functools.wraps(f)
    def wrapper(ctx: CLIContext, *args, **kwargs):
        # Import here to avoid circular imports
        from unityauth_cli import auth
        from unityauth_cli.client import UnityAuthAPIClient

        # Check API URL is configured
        if not ctx.api_url:
            raise ConfigurationError(
                "API URL not configured",
                "Set API URL: unityauth config set api_url https://auth.example.com"
            )

        # Get token from keyring
        token = auth.get_token(ctx.api_url)
        if not token:
            raise AuthenticationError(
                "Not authenticated",
                "Run: unityauth login"
            )

        # Get timeout from config if available
        timeout = 30
        if ctx.config:
            timeout = ctx.config.get('timeout', 30)

        # Create API client and pass it to the command
        client = UnityAuthAPIClient(ctx.api_url, token=token, timeout=timeout)
        kwargs['client'] = client

        return f(ctx, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


def require_config(f: F) -> F:
    """Decorator that ensures API URL is configured.

    Lighter weight than @require_auth - use when authentication is not required
    (e.g., login command itself).

    Must be used after @pass_context decorator.

    Example:
        @click.command()
        @pass_context
        @require_config
        def login(ctx: CLIContext) -> None:
            # ctx.api_url is guaranteed to be set
            ...
    """
    @functools.wraps(f)
    def wrapper(ctx: CLIContext, *args, **kwargs):
        if not ctx.api_url:
            raise ConfigurationError(
                "API URL not configured",
                "Set API URL: unityauth config set api_url https://auth.example.com"
            )
        return f(ctx, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


def format_option(f: F) -> F:
    """Decorator that adds -o/--format option to a command.

    Allows format to be specified after the command (more intuitive):
        unityauth tenant list -o json

    If provided, overrides the global format from the parent context.
    Must be used before @pass_context decorator.

    Example:
        @click.command()
        @format_option
        @pass_context
        @require_auth
        def list_tenants(ctx: CLIContext, client: UnityAuthAPIClient) -> None:
            # ctx.output_format is set (from local -o or global -o or config)
            ...
    """
    @functools.wraps(f)
    def wrapper(*args, output_format: Optional[str] = None, **kwargs):
        # Override context format if local option provided
        if output_format:
            # Get CLIContext from Click's current context
            click_ctx = click.get_current_context(silent=True)
            if click_ctx:
                cli_ctx = click_ctx.find_object(CLIContext)
                if cli_ctx:
                    cli_ctx.output_format = output_format.lower()

        return f(*args, **kwargs)

    # Apply the click option decorator
    decorated = click.option(
        '-o', '--format',
        'output_format',
        type=click.Choice(['table', 'json', 'csv'], case_sensitive=False),
        help='Output format (default: table)',
    )(wrapper)

    return decorated  # type: ignore[return-value]


@click.group()
@click.option(
    '--api-url',
    envvar='UNITYAUTH_API_URL',
    help='UnityAuth API endpoint URL (overrides config file)',
)
@click.option(
    '-o', '--format',
    'output_format',
    type=click.Choice(['table', 'json', 'csv'], case_sensitive=False),
    help='Output format (default: table)',
)
@click.option(
    '-v', '--verbose',
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
      unityauth role list                # List available roles

    \b
    Option placement:
      Global options (--verbose, --format) go BEFORE the command:
        unityauth --verbose user list
        unityauth -o json tenant list
      Command options go AFTER the command:
        unityauth user create --email user@example.com

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
    from unityauth_cli.commands.init import init
    from unityauth_cli.commands.users import create, update, update_profile, list_users
    from unityauth_cli.commands.tenants import list_tenants, tenant_users
    from unityauth_cli.commands.roles import list_roles
    from unityauth_cli.commands.permissions import list_permissions

    # Register setup command
    cli.add_command(init)

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
    user.add_command(update_profile)
    user.add_command(list_users, name='list')

    # Register tenant discovery commands
    @cli.group()
    def tenant():
        """Tenant discovery and management commands."""
        pass

    tenant.add_command(list_tenants, name='list')
    tenant.add_command(tenant_users, name='users')

    # Register role discovery commands
    @cli.group()
    def role():
        """Role discovery commands."""
        pass

    role.add_command(list_roles, name='list')

    # Register permissions commands
    @cli.group()
    def permissions():
        """Permission discovery and verification commands."""
        pass

    permissions.add_command(list_permissions, name='list')
