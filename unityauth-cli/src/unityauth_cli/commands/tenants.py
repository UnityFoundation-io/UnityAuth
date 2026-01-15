"""Tenant discovery commands: list, users.

Handles tenant listing and user discovery operations.
"""

import sys

import click

from unityauth_cli.cli import (
    CLIContext,
    console,
    error,
    format_option,
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
from unityauth_cli.utils.errors import AuthorizationError, ValidationError


@click.command('list')
@format_option
@pass_context
@require_auth
def list_tenants(ctx: CLIContext, client: UnityAuthAPIClient) -> None:
    """List accessible tenants.

    Lists all tenants accessible to the current user.
    Unity Administrators see all tenants.
    Tenant Administrators see only their assigned tenants.

    \b
    Tenant IDs are used in:
      - 'unityauth user list --tenant-id <ID>'
      - 'unityauth user create --tenant-id <ID>'
      - 'unityauth permissions list --tenant-id <ID>'

    \b
    Examples:
      unityauth tenant list
      unityauth tenant list -o json
      unityauth tenant list -o csv
    """
    try:
        if ctx.verbose:
            info("Fetching accessible tenants...")

        response = client.get('/api/tenants')

        # Handle empty response
        if not response:
            warning("No tenants found")
            return

        # Ensure response is a list
        tenants = response if isinstance(response, list) else [response]

        if not tenants:
            warning("No tenants found")
            return

        # Format and display output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(tenants))
        elif ctx.output_format == 'csv':
            headers = ['id', 'name']
            console.print(format_csv(tenants, headers))
        else:
            # Table format (default)
            headers = ['ID', 'Name']
            rows = [
                [tenant.get('id', 'N/A'), tenant.get('name', 'N/A')]
                for tenant in tenants
            ]
            console.print(format_table(rows, headers))

        if ctx.verbose:
            info(f"Total tenants: {len(tenants)}")

    except AuthorizationError as e:
        error(
            str(e),
            "You need Unity Administrator or Tenant Administrator permissions to list tenants.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)


@click.command('users')
@click.argument('tenant_id', type=int)
@format_option
@pass_context
@require_auth
def tenant_users(ctx: CLIContext, tenant_id: int, client: UnityAuthAPIClient) -> None:
    """List users in a tenant.

    Lists all users belonging to the specified tenant.
    Requires appropriate permissions to view tenant users.

    \b
    Examples:
      unityauth tenant users 1
      unityauth tenant users 1 -o json
      unityauth tenant users 2 -o csv
    """
    try:
        # Validate tenant ID
        if tenant_id <= 0:
            raise ValidationError("Tenant ID must be a positive integer")

        if ctx.verbose:
            info(f"Fetching users for tenant {tenant_id}...")

        response = client.get(f'/api/tenants/{tenant_id}/users')

        # Handle empty response
        if not response:
            warning(f"No users found in tenant {tenant_id}")
            return

        # Ensure response is a list
        users = response if isinstance(response, list) else [response]

        if not users:
            warning(f"No users found in tenant {tenant_id}")
            return

        # Format and display output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(users))
        elif ctx.output_format == 'csv':
            headers = ['id', 'email', 'firstName', 'lastName', 'roles']
            console.print(format_csv(users, headers))
        else:
            # Table format (default)
            headers = ['ID', 'Email', 'First Name', 'Last Name', 'Roles']
            rows = []
            for user in users:
                roles = user.get('roles', [])
                if isinstance(roles, list):
                    roles_str = ', '.join(str(r) for r in roles)
                else:
                    roles_str = str(roles) if roles else 'None'
                rows.append([
                    user.get('id', 'N/A'),
                    user.get('email', 'N/A'),
                    user.get('firstName', 'N/A'),
                    user.get('lastName', 'N/A'),
                    roles_str if roles_str else 'None'
                ])
            console.print(format_table(rows, headers))

        if ctx.verbose:
            info(f"Total users: {len(users)}")

    except AuthorizationError as e:
        error(
            str(e),
            "You need appropriate permissions to list tenant users.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)
