"""User management commands: create, update, list.

Handles user account provisioning and management operations.
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
    success,
    warning,
)
from unityauth_cli.client import UnityAuthAPIClient
from unityauth_cli.formatters.table import format_table
from unityauth_cli.formatters.json_fmt import format_json
from unityauth_cli.formatters.csv_fmt import format_csv
from unityauth_cli.utils.errors import AuthorizationError, ValidationError
from unityauth_cli.utils.validation import validate_email


@click.command()
@click.option('--email', required=True, help='User email address')
@click.option('--first-name', required=True, help='User first name')
@click.option('--last-name', required=True, help='User last name')
@click.option('--password', required=True, help='User password (min 8 characters)')
@click.option('-t', '--tenant-id', required=True, type=int, help='Tenant ID for the user')
@click.option('-r', '--role-ids', required=True, help='Comma-separated role IDs (e.g., "1,2,3")')
@click.option('--dry-run', '-n', is_flag=True, help='Preview changes without executing')
@pass_context
@require_auth
def create(
    ctx: CLIContext,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    tenant_id: int,
    role_ids: str,
    dry_run: bool,
    client: UnityAuthAPIClient,
) -> None:
    """Create a new user account.

    Creates a new user with the specified details and assigns roles.
    Requires Unity Administrator or Tenant Administrator permissions.

    \b
    Finding IDs:
      - Tenant IDs: Run 'unityauth tenant list'
      - Role IDs: Run 'unityauth role list'

    \b
    Examples:
      unityauth user create --email user@example.com --first-name John --last-name Doe --password MyP@ss123 --tenant-id 1 --role-ids "2"
      unityauth user create --email admin@example.com --first-name Jane --last-name Admin --password SecureP@ss --tenant-id 1 --role-ids "1,2"
    """
    try:
        # Validate email format
        if not validate_email(email):
            raise ValidationError("Invalid email format")

        # Validate password length
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        # Validate name lengths
        if not first_name or len(first_name) > 100:
            raise ValidationError("First name must be 1-100 characters")

        if not last_name or len(last_name) > 100:
            raise ValidationError("Last name must be 1-100 characters")

        # Validate tenant ID
        if tenant_id <= 0:
            raise ValidationError("Tenant ID must be a positive integer")

        # Parse role IDs
        try:
            roles = [int(rid.strip()) for rid in role_ids.split(',')]
        except ValueError:
            raise ValidationError("Role IDs must be comma-separated integers")

        if not roles:
            raise ValidationError("At least one role ID must be provided")

        # Build request payload
        payload = {
            'email': email,
            'firstName': first_name,
            'lastName': last_name,
            'password': password,
            'tenantId': tenant_id,
            'roles': roles,
        }

        # Handle dry-run mode
        if dry_run:
            console.print("\n[bold cyan][DRY RUN][/bold cyan] Would create user:")
            console.print(f"  Email: {email}")
            console.print(f"  First Name: {first_name}")
            console.print(f"  Last Name: {last_name}")
            console.print(f"  Tenant ID: {tenant_id}")
            console.print(f"  Role IDs: {', '.join(str(r) for r in roles)}")
            console.print("\nRun without --dry-run to execute.")
            return

        # Make create request
        if ctx.verbose:
            info(f"Creating user {email} in tenant {tenant_id}...")

        response = client.post('/api/users', data=payload)

        # Extract user ID from response
        user_id = response.get('id') if response else None

        if user_id:
            success(f"User created successfully (ID: {user_id})")
        else:
            success(f"User created successfully: {email}")

        if ctx.verbose and response:
            info(f"User details: {response}")

    except ValidationError as e:
        error_msg = str(e)
        # Provide specific guidance for common errors
        if "already exists" in error_msg.lower() or ("invalid request" in error_msg.lower() and "bad request" in error_msg.lower()):
            error(
                f"User creation failed: {error_msg}",
                f"This typically means user '{email}' already exists in tenant {tenant_id}.\n\n"
                f"Options:\n"
                f"  • Update existing user: Get user ID with 'unityauth user list --tenant-id {tenant_id}',\n"
                f"    then run 'unityauth user update <ID> --role-ids \"1,2\"'\n"
                f"  • Use different email: Try a different email address\n"
                f"  • Use different tenant: Change --tenant-id to create user in another tenant"
            )
        else:
            error(error_msg)
        sys.exit(1)
    except AuthorizationError as e:
        error(
            str(e),
            "You need Unity Administrator or Tenant Administrator permissions to create users.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)


@click.command()
@click.argument('user_id', type=int)
@click.option('-t', '--tenant-id', required=True, type=int, help='Tenant ID where user has roles')
@click.option('-r', '--role-ids', required=True, help='Comma-separated role IDs to assign (e.g., "1,2,3")')
@click.option('--dry-run', '-n', is_flag=True, help='Preview changes without executing')
@pass_context
@require_auth
def update(
    ctx: CLIContext,
    user_id: int,
    tenant_id: int,
    role_ids: str,
    dry_run: bool,
    client: UnityAuthAPIClient,
) -> None:
    """Update user roles in a tenant.

    Updates the role assignments for an existing user in a specific tenant.
    This replaces all current roles with the specified roles for that tenant.

    \b
    Finding IDs:
      - User IDs: Run 'unityauth user list --tenant-id <ID>'
      - Tenant IDs: Run 'unityauth tenant list'
      - Role IDs: Run 'unityauth role list'

    \b
    Examples:
      unityauth user update 5 --tenant-id 1 --role-ids "1,2"
      unityauth user update 10 --tenant-id 1 --role-ids "3"
    """
    try:
        # Validate user ID
        if user_id <= 0:
            raise ValidationError("User ID must be a positive integer")

        # Validate tenant ID
        if tenant_id <= 0:
            raise ValidationError("Tenant ID must be a positive integer")

        # Parse role IDs
        try:
            roles = [int(rid.strip()) for rid in role_ids.split(',')]
        except ValueError:
            raise ValidationError("Role IDs must be comma-separated integers")

        if not roles:
            raise ValidationError("At least one role ID must be provided")

        # Build request payload - backend requires tenantId and roles
        payload = {
            'tenantId': tenant_id,
            'roles': roles
        }

        # Handle dry-run mode
        if dry_run:
            console.print("\n[bold cyan][DRY RUN][/bold cyan] Would update user roles:")
            console.print(f"  User ID: {user_id}")
            console.print(f"  Tenant ID: {tenant_id}")
            console.print(f"  New Role IDs: {', '.join(str(r) for r in roles)}")
            console.print("\nRun without --dry-run to execute.")
            return

        # Make update request - use PATCH to /api/users/{id}/roles endpoint
        if ctx.verbose:
            info(f"Updating user {user_id} roles in tenant {tenant_id} to {roles}...")

        result = client.patch(f'/api/users/{user_id}/roles', data=payload)

        success(f"User {user_id} roles updated successfully in tenant {tenant_id}")

        if ctx.verbose and result:
            info(f"Updated user: {result}")

    except AuthorizationError as e:
        error(
            str(e),
            "You need Unity Administrator or Tenant Administrator permissions to update users.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)


@click.command('update-profile')
@click.argument('user_id', type=int)
@click.option('--first-name', help='New first name')
@click.option('--last-name', help='New last name')
@click.option('--password', help='New password (min 8 characters)')
@click.option('--dry-run', '-n', is_flag=True, help='Preview changes without executing')
@pass_context
@require_auth
def update_profile(
    ctx: CLIContext,
    user_id: int,
    first_name: str | None,
    last_name: str | None,
    password: str | None,
    dry_run: bool,
    client: UnityAuthAPIClient,
) -> None:
    """Update your own user profile.

    Updates your profile information (first name, last name, password).
    You can only update your own profile - the user ID must match
    the authenticated user.

    At least one field must be provided.

    \b
    Finding your user ID:
      Run 'unityauth token-info' to see your user ID.

    \b
    Examples:
      unityauth user update-profile 5 --first-name John
      unityauth user update-profile 5 --last-name Smith
      unityauth user update-profile 5 --password NewSecureP@ss123
      unityauth user update-profile 5 --first-name John --last-name Smith --password NewP@ss
    """
    try:
        # Validate user ID
        if user_id <= 0:
            raise ValidationError("User ID must be a positive integer")

        # Ensure at least one field is provided
        if not any([first_name, last_name, password]):
            raise ValidationError(
                "At least one field must be provided: --first-name, --last-name, or --password"
            )

        # Validate password length if provided
        if password and len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        # Validate name lengths if provided
        if first_name and len(first_name) > 100:
            raise ValidationError("First name must be 1-100 characters")

        if last_name and len(last_name) > 100:
            raise ValidationError("Last name must be 1-100 characters")

        # Build request payload - only include non-None fields
        payload = {}
        if first_name:
            payload['firstName'] = first_name
        if last_name:
            payload['lastName'] = last_name
        if password:
            payload['password'] = password

        # Handle dry-run mode
        if dry_run:
            console.print("\n[bold cyan][DRY RUN][/bold cyan] Would update profile:")
            console.print(f"  User ID: {user_id}")
            if first_name:
                console.print(f"  First Name: {first_name}")
            if last_name:
                console.print(f"  Last Name: {last_name}")
            if password:
                console.print("  Password: ********")
            console.print("\nRun without --dry-run to execute.")
            return

        # Make update request
        if ctx.verbose:
            fields = ', '.join(payload.keys())
            info(f"Updating profile for user {user_id} (fields: {fields})...")

        result = client.patch(f'/api/users/{user_id}', data=payload)

        success(f"Profile updated successfully for user {user_id}")

        if ctx.verbose and result:
            info(f"Updated user: {result}")

    except AuthorizationError as e:
        error(
            str(e),
            "You can only update your own profile. The user ID must match your authenticated user.\n"
            "Use 'unityauth token-info' to see your user details."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)


@click.command()
@click.option('-t', '--tenant-id', type=int, required=True, help='Tenant ID to list users from')
@format_option
@pass_context
@require_auth
def list_users(ctx: CLIContext, tenant_id: int, client: UnityAuthAPIClient) -> None:
    """List users in a tenant.

    Lists all users in the specified tenant. Requires Unity Administrator
    or Tenant Administrator permissions for the target tenant.

    \b
    Finding IDs:
      - Tenant IDs: Run 'unityauth tenant list'

    \b
    Examples:
      unityauth user list --tenant-id 1
      unityauth user list --tenant-id 1 -o json
      unityauth user list --tenant-id 1 -o csv
    """
    try:
        # Validate tenant ID
        if tenant_id <= 0:
            raise ValidationError("Tenant ID must be a positive integer")

        # Make list request
        if ctx.verbose:
            info(f"Fetching users for tenant {tenant_id}...")

        # Build endpoint - backend uses /api/tenants/{id}/users
        endpoint = f'/api/tenants/{tenant_id}/users'

        response = client.get(endpoint)

        # Handle empty response
        if not response:
            warning("No users found")
            return

        # Ensure response is a list
        users = response if isinstance(response, list) else [response]

        # Format and display output based on format option
        if ctx.output_format == 'json':
            console.print(format_json(users))
        elif ctx.output_format == 'csv':
            # Define CSV headers
            headers = ['id', 'email', 'firstName', 'lastName', 'roles']
            console.print(format_csv(users, headers))
        else:
            # Table format (default)
            headers = ['ID', 'Email', 'First Name', 'Last Name', 'Roles']

            # Transform data for table display
            rows = []
            for user in users:
                roles_str = ', '.join(str(r) for r in user.get('roles', []))
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
            "You need appropriate permissions to list users.\n"
            "Contact your administrator to grant required permissions."
        )
        sys.exit(3)
    except Exception as e:
        handle_error(e)
