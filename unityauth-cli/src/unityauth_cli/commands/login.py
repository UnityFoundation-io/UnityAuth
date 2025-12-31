"""Authentication commands: login, logout, token-info.

Handles user authentication and session management.
"""

import sys
from typing import Optional

import click

from unityauth_cli import auth
from unityauth_cli.cli import (
    CLIContext,
    console,
    error,
    format_option,
    handle_error,
    info,
    pass_context,
    require_auth,
    require_config,
    success,
    warning,
)
from unityauth_cli.client import UnityAuthAPIClient
from unityauth_cli.formatters.table import format_key_value_table
from unityauth_cli.formatters.json_fmt import format_json
from unityauth_cli.utils.errors import ConfigurationError
from unityauth_cli.utils.validation import validate_email


@click.command()
@click.option(
    '--email',
    envvar='UNITYAUTH_EMAIL',
    help='Email address for login',
)
@click.option(
    '--password',
    envvar='UNITYAUTH_PASSWORD',
    help='Password (will prompt if not provided)',
)
@pass_context
@require_config
def login(ctx: CLIContext, email: Optional[str], password: Optional[str]) -> None:
    """Authenticate with UnityAuth and store credentials.

    Logs in to UnityAuth using email and password, then securely stores
    the JWT token in your operating system's credential manager.

    \b
    Examples:
      unityauth login                              # Interactive mode
      unityauth login --email user@example.com     # Prompt for password
      UNITYAUTH_PASSWORD=secret unityauth login    # Non-interactive
    """
    try:
        # Get email (interactive or from option)
        if not email:
            if not sys.stdin.isatty():
                raise ConfigurationError(
                    "Email required in non-interactive mode",
                    "Use --email option or set UNITYAUTH_EMAIL environment variable"
                )
            email = click.prompt('Email', type=str)

        # Validate email format
        if not validate_email(email):
            error("Invalid email format")
            sys.exit(1)

        # Get password (interactive or from option)
        if not password:
            if not sys.stdin.isatty():
                raise ConfigurationError(
                    "Password required in non-interactive mode",
                    "Use --password option or set UNITYAUTH_PASSWORD environment variable"
                )
            password = click.prompt('Password', hide_input=True, type=str)

        # Make login request
        if ctx.verbose:
            info(f"Authenticating with {ctx.api_url}...")

        # Get timeout from config if available
        timeout = 30
        if ctx.config:
            timeout = ctx.config.get('timeout', 30)

        client = UnityAuthAPIClient(ctx.api_url, timeout=timeout)
        response = client.post('/api/login', data={
            'username': email,
            'password': password
        })

        # Extract token from response
        token = response.get('access_token') or response.get('accessToken')
        if not token:
            error("Login failed: No token in response")
            sys.exit(1)

        # Store token in keyring
        auth.store_token(ctx.api_url, token)

        success(f"Login successful as {email}")

        if ctx.verbose:
            info("Token stored securely in OS credential manager")

    except Exception as e:
        handle_error(e)


@click.command()
@pass_context
@require_config
def logout(ctx: CLIContext) -> None:
    """Remove stored credentials and logout.

    Deletes the stored JWT token from your operating system's credential manager.

    \b
    Examples:
      unityauth logout
    """
    try:
        # Check if token exists
        if not auth.has_token(ctx.api_url):
            warning("No active session found")
            return

        # Delete token from keyring
        auth.delete_token(ctx.api_url)

        success("Logout successful")

        if ctx.verbose:
            info("Token removed from OS credential manager")

    except Exception as e:
        handle_error(e)


@click.command(name='token-info')
@format_option
@pass_context
@require_auth
def token_info(ctx: CLIContext, client: UnityAuthAPIClient) -> None:
    """Display current session and token information.

    Shows details about the currently authenticated session, including
    user email, token expiration, and API version.

    \b
    Examples:
      unityauth token-info
      unityauth token-info -o json
    """
    try:
        # Make token_info request
        if ctx.verbose:
            info(f"Fetching token info from {ctx.api_url}...")

        response = client.get('/api/token_info')

        # Format output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(response))
        else:
            # Extract key fields for table display
            display_data = {
                'User Email': response.get('email') or response.get('userEmail', 'N/A'),
                'User ID': response.get('userId') or response.get('id', 'N/A'),
                'API Endpoint': ctx.api_url,
                'Authenticated': 'Yes',
            }

            # Add expiration if present
            if 'exp' in response or 'expiration' in response:
                exp = response.get('exp') or response.get('expiration')
                display_data['Token Expires'] = exp

            # Add API version if present
            if 'apiVersion' in response:
                display_data['API Version'] = response['apiVersion']

            console.print(format_key_value_table(display_data))

    except Exception as e:
        handle_error(e)
