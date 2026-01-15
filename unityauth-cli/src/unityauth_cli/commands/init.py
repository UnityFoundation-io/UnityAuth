"""Init command: First-time setup wizard for UnityAuth CLI.

Guides users through initial configuration and authentication.
"""

import sys

import click
import requests

from unityauth_cli.cli import CLIContext, console, error, info, pass_context, success, warning
from unityauth_cli.config import Configuration
from unityauth_cli.utils.validation import validate_url, validate_email


@click.command()
@click.option(
    '--api-url',
    help='UnityAuth API endpoint URL (skip prompt)',
)
@click.option(
    '--skip-login',
    is_flag=True,
    help='Skip the login step after configuration',
)
@click.option(
    '--allow-http',
    is_flag=True,
    help='Allow insecure HTTP URLs (not recommended)',
)
@pass_context
def init(ctx: CLIContext, api_url: str | None, skip_login: bool, allow_http: bool) -> None:
    """Initialize UnityAuth CLI with first-time setup wizard.

    Guides you through configuring the API endpoint and optionally
    authenticating with your credentials.

    \b
    Examples:
      unityauth init                                    # Interactive setup
      unityauth init --api-url https://auth.example.com # Skip URL prompt
      unityauth init --skip-login                       # Configure only, no login
    """
    console.print()
    console.print("[bold cyan]Welcome to UnityAuth CLI![/bold cyan]")
    console.print("Let's get you set up.\n")

    # Step 1: Get API URL
    if not api_url:
        if not sys.stdin.isatty():
            error(
                "API URL required in non-interactive mode",
                "Use --api-url option to specify the UnityAuth API endpoint"
            )
            sys.exit(4)

        # Show current value if configured
        current_url = ctx.config.get('api_url') if ctx.config else None
        if current_url:
            info(f"Current API URL: {current_url}")

        api_url = click.prompt(
            'API URL',
            default=current_url or 'https://auth.example.com',
            type=str
        )

    # Validate URL format
    api_url = api_url.strip().rstrip('/')

    if not validate_url(api_url, require_https=not allow_http):
        if not allow_http and api_url.startswith('http://'):
            error(
                "HTTP URLs are not allowed by default (insecure)",
                "Use HTTPS or add --allow-http flag if this is intentional"
            )
        else:
            error(
                "Invalid URL format",
                "URL must start with https:// (e.g., https://auth.example.com)"
            )
        sys.exit(4)

    # Step 2: Test connection
    info(f"Testing connection to {api_url}...")

    try:
        # Try to reach the /keys endpoint (public, no auth required)
        response = requests.get(f"{api_url}/keys", timeout=10)

        if response.ok:
            success("Connection successful")
            if ctx.verbose:
                info(f"Server responded with status {response.status_code}")
        else:
            # Server responded but with error
            warning(f"Server responded with status {response.status_code}")
            if not click.confirm("Continue anyway?", default=False):
                info("Setup cancelled")
                sys.exit(0)

    except requests.ConnectionError:
        error(
            f"Could not connect to {api_url}",
            "Check that the URL is correct and the server is running"
        )
        if not click.confirm("Save configuration anyway?", default=False):
            info("Setup cancelled")
            sys.exit(0)
    except requests.Timeout:
        warning("Connection timed out")
        if not click.confirm("Save configuration anyway?", default=False):
            info("Setup cancelled")
            sys.exit(0)
    except requests.RequestException as e:
        warning(f"Connection test failed: {e}")
        if not click.confirm("Save configuration anyway?", default=False):
            info("Setup cancelled")
            sys.exit(0)

    # Step 3: Save configuration
    try:
        config = ctx.config or Configuration()
        config.set('api_url', api_url)
        config.save()
        success(f"Configuration saved to {config.config_path}")
    except Exception as e:
        error(f"Failed to save configuration: {e}")
        sys.exit(4)

    # Step 4: Optionally login
    if not skip_login:
        console.print()
        if sys.stdin.isatty() and click.confirm("Would you like to log in now?", default=True):
            console.print()
            _do_login(api_url, config, ctx.verbose)
        else:
            info("Skipping login. Run 'unityauth login' when ready.")

    # Step 5: Show next steps
    console.print()
    console.print("[bold green]Setup complete![/bold green]")
    console.print()
    console.print("Next steps:")
    console.print("  [dim]$[/dim] unityauth tenant list              [dim]# List your tenants[/dim]")
    console.print("  [dim]$[/dim] unityauth user list --tenant-id 1  [dim]# List users in tenant 1[/dim]")
    console.print("  [dim]$[/dim] unityauth role list                [dim]# List available roles[/dim]")
    console.print("  [dim]$[/dim] unityauth --help                   [dim]# See all commands[/dim]")
    console.print()


def _do_login(api_url: str, config: Configuration, verbose: bool) -> None:
    """Perform login as part of init wizard.

    Args:
        api_url: API endpoint URL
        config: Configuration instance
        verbose: Whether to show verbose output
    """
    from unityauth_cli import auth
    from unityauth_cli.client import UnityAuthAPIClient

    # Get email
    email = click.prompt('Email', type=str)

    if not validate_email(email):
        error("Invalid email format")
        return

    # Get password
    password = click.prompt('Password', hide_input=True, type=str)

    # Attempt login
    if verbose:
        info(f"Authenticating with {api_url}...")

    try:
        timeout = config.get('timeout', 30)
        client = UnityAuthAPIClient(api_url, timeout=timeout)
        response = client.post('/api/login', data={
            'username': email,
            'password': password
        })

        # Extract token from response
        token = response.get('access_token') or response.get('accessToken')
        if not token:
            error("Login failed: No token in response")
            return

        # Store token in keyring
        auth.store_token(api_url, token)
        success(f"Logged in as {email}")

    except Exception as e:
        error(f"Login failed: {e}")
        info("You can try again later with 'unityauth login'")
