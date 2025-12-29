"""Permission commands: list, check.

Handles permission discovery and verification operations.
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
    success,
    warning,
)
from unityauth_cli.client import UnityAuthAPIClient
from unityauth_cli.formatters.table import format_table
from unityauth_cli.formatters.json_fmt import format_json
from unityauth_cli.formatters.csv_fmt import format_csv
from unityauth_cli.utils.errors import AuthorizationError, ValidationError


@click.command('list')
@click.option('--tenant-id', required=True, type=int, help='Tenant ID to check permissions for')
@click.option('--service-id', required=True, type=int, help='Service ID to check permissions for')
@pass_context
@require_auth
def list_permissions(
    ctx: CLIContext,
    tenant_id: int,
    service_id: int,
    client: UnityAuthAPIClient,
) -> None:
    """List your permissions for a tenant and service.

    Returns all permissions the authenticated user has for the specified
    tenant and service combination.

    \b
    Examples:
      unityauth permissions list --tenant-id 1 --service-id 1
      unityauth permissions list --tenant-id 1 --service-id 1 --format json
    """
    try:
        # Validate IDs
        if tenant_id <= 0:
            raise ValidationError("Tenant ID must be a positive integer")
        if service_id <= 0:
            raise ValidationError("Service ID must be a positive integer")

        if ctx.verbose:
            info(f"Fetching permissions for tenant {tenant_id}, service {service_id}...")

        # Build request payload
        payload = {
            'tenantId': tenant_id,
            'serviceId': service_id,
        }

        # Make POST request to get permissions
        response = client.post('/api/principal/permissions', data=payload)

        # Handle error response (Failure case)
        if response and 'errorMessage' in response:
            error(f"Failed to get permissions: {response['errorMessage']}")
            sys.exit(1)

        # Handle success response
        permissions = response.get('permissions', []) if response else []

        if not permissions:
            warning("No permissions found for this tenant/service combination")
            return

        # Format and display output based on format option
        if ctx.output_format == 'json':
            console.print(format_json({'permissions': permissions}))
        elif ctx.output_format == 'csv':
            # For CSV, create a simple list format
            headers = ['permission']
            rows = [{'permission': perm} for perm in permissions]
            console.print(format_csv(rows, headers))
        else:
            # Table format (default)
            headers = ['Permission']
            rows = [[perm] for perm in permissions]
            console.print(format_table(rows, headers))

        if ctx.verbose:
            info(f"Total permissions: {len(permissions)}")

    except AuthorizationError as e:
        error(
            str(e),
            "You may not have access to this tenant/service combination.\n"
            "Contact your administrator for access."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)
