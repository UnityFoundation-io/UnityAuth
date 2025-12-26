"""Role discovery commands: list.

Handles role listing and discovery operations.
"""

import sys

import click

from unityauth_cli.cli import (
    CLIContext,
    console,
    error,
    handle_error,
    info,
    pass_context,
    require_auth,
    warning,
)
from unityauth_cli.client import UnityAuthAPIClient
from unityauth_cli.formatters.table import format_table
from unityauth_cli.formatters.json_fmt import format_json
from unityauth_cli.formatters.csv_fmt import format_csv
from unityauth_cli.utils.errors import AuthorizationError


@click.command('list')
@pass_context
@require_auth
def list_roles(ctx: CLIContext, client: UnityAuthAPIClient) -> None:
    """List all available roles.

    Lists all roles defined in the system with their descriptions.
    Requires Unity Administrator or Tenant Administrator permissions.

    \b
    Examples:
      unityauth role list
      unityauth role list --format json
      unityauth role list --format csv
    """
    try:
        if ctx.verbose:
            info("Fetching available roles...")

        response = client.get('/api/roles')

        # Handle empty response
        if not response:
            warning("No roles found")
            return

        # Ensure response is a list
        roles = response if isinstance(response, list) else [response]

        if not roles:
            warning("No roles found")
            return

        # Format and display output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(roles))
        elif ctx.output_format == 'csv':
            headers = ['id', 'name', 'description']
            console.print(format_csv(roles, headers))
        else:
            # Table format (default)
            headers = ['ID', 'Name', 'Description']
            rows = [
                [
                    role.get('id', 'N/A'),
                    role.get('name', 'N/A'),
                    role.get('description', '') or 'N/A'
                ]
                for role in roles
            ]
            console.print(format_table(rows, headers))

        if ctx.verbose:
            info(f"Total roles: {len(roles)}")

    except AuthorizationError as e:
        error(
            str(e),
            "You need Unity Administrator or Tenant Administrator permissions to list roles.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)
