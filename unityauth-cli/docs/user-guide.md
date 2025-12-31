# UnityAuth CLI User Guide

Complete command reference for the UnityAuth command-line interface.

## Table of Contents

- [Global Options](#global-options)
- [Setup Commands](#setup-commands)
  - [init](#init)
- [Authentication Commands](#authentication-commands)
  - [login](#login)
  - [logout](#logout)
  - [token-info](#token-info)
- [Configuration Commands](#configuration-commands)
  - [config show](#config-show)
  - [config set](#config-set)
  - [config edit](#config-edit)
- [User Management Commands](#user-management-commands)
  - [user create](#user-create)
  - [user list](#user-list)
  - [user update](#user-update)
  - [user update-profile](#user-update-profile)
- [Tenant Commands](#tenant-commands)
  - [tenant list](#tenant-list)
  - [tenant users](#tenant-users)
- [Role Commands](#role-commands)
  - [role list](#role-list)
- [Permissions Commands](#permissions-commands)
  - [permissions list](#permissions-list)
- [Known Limitations](#known-limitations)
- [Output Formats](#output-formats)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Global Options

These options are available for all commands:

| Option | Short | Environment Variable | Description |
|--------|-------|---------------------|-------------|
| `--api-url TEXT` | | `UNITYAUTH_API_URL` | Override the API endpoint URL |
| `--format [table\|json\|csv]` | `-o` | - | Set output format (default: table) |
| `--verbose` | `-v` | - | Enable debug/verbose output |
| `--version` | | - | Show version and exit |
| `--help` | | - | Show help message and exit |

**Examples:**

```bash
# Override API URL for a single command
unityauth --api-url https://staging.example.com tenant list

# Get JSON output (using short flag)
unityauth -o json role list

# Enable verbose mode for debugging (using short flag)
unityauth -v login

# Combine short flags
unityauth -v -o json tenant list
```

---

## Setup Commands

### init

Initialize UnityAuth CLI with a guided setup wizard. This is the recommended first command for new users.

```
unityauth init [OPTIONS]
```

**Options:**

| Option | Description |
|--------|-------------|
| `--api-url TEXT` | UnityAuth API endpoint URL (skips prompt if provided) |
| `--skip-login` | Skip the login step after configuration |
| `--allow-http` | Allow insecure HTTP URLs (not recommended for production) |

**Behavior:**

1. Prompts for API URL (or accepts via `--api-url`)
2. Tests connection to the UnityAuth server
3. Saves configuration to `~/.config/unityauth-cli/config.yml`
4. Optionally prompts to log in (in interactive mode)
5. Displays helpful next steps

**Examples:**

```bash
# Interactive setup (recommended for first-time users)
unityauth init

# Non-interactive setup with API URL
unityauth init --api-url https://auth.example.com --skip-login

# Setup for local development (allows HTTP)
unityauth init --api-url http://localhost:8081 --allow-http --skip-login
```

**Sample Output:**

```
Welcome to UnityAuth CLI!
Let's get you set up.

API URL: https://auth.example.com
Testing connection to https://auth.example.com...
✓ Connection successful
✓ Configuration saved to ~/.config/unityauth-cli/config.yml

Would you like to log in now? [Y/n]: y
Email: admin@example.com
Password: ********
✓ Logged in as admin@example.com

Setup complete!

Next steps:
  $ unityauth tenant list       # List your tenants
  $ unityauth user list -t 1    # List users in tenant 1
  $ unityauth role list         # List available roles
  $ unityauth --help            # See all commands
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Setup successful |
| 4 | Configuration error (invalid URL, connection failed) |

---

## Authentication Commands

### login

Authenticate with UnityAuth and store credentials securely.

```
unityauth login [OPTIONS]
```

**Options:**

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--email TEXT` | `UNITYAUTH_EMAIL` | Email address for login |
| `--password TEXT` | `UNITYAUTH_PASSWORD` | Password (prompts if not provided) |

**Behavior:**

- In interactive mode (TTY), prompts for email and password
- In non-interactive mode, requires `--email` and `--password` or environment variables
- Stores JWT token in OS-native credential manager:
  - macOS: Keychain
  - Windows: Credential Manager
  - Linux: Secret Service (GNOME Keyring, KWallet)

**Examples:**

```bash
# Interactive login (recommended)
unityauth login

# Login with email, prompt for password
unityauth login --email admin@example.com

# Non-interactive login for scripts
unityauth login --email admin@example.com --password "MySecretP@ss"

# Using environment variables
export UNITYAUTH_EMAIL="admin@example.com"
export UNITYAUTH_PASSWORD="MySecretP@ss"
unityauth login
```

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Login successful |
| 2 | Invalid credentials |
| 4 | API URL not configured |

---

### logout

Remove stored credentials and end the current session.

```
unityauth logout
```

**Behavior:**

- Deletes the stored JWT token from the OS credential manager
- Does not invalidate the token on the server (tokens expire naturally)

**Example:**

```bash
unityauth logout
# Output: ✓ Logged out successfully
```

---

### token-info

Display information about the current session and authentication token.

```
unityauth token-info
```

**Output Fields:**

| Field | Description |
|-------|-------------|
| Email | Authenticated user's email |
| Name | User's full name (if available) |
| API Endpoint | Current API endpoint |
| Authenticated | Yes (shown when authenticated) |
| Token Expires | Token expiration time (Unix timestamp) |

**Examples:**

```bash
# Table output
unityauth token-info

# JSON output for scripting
unityauth token-info -o json
```

**Sample Output:**

```
+---------------+-------------------------+
| Field         | Value                   |
+===============+=========================+
| Email         | admin@example.com       |
+---------------+-------------------------+
| Name          | Admin User              |
+---------------+-------------------------+
| API Endpoint  | https://auth.example.com|
+---------------+-------------------------+
| Authenticated | Yes                     |
+---------------+-------------------------+
| Token Expires | 1767196697              |
+---------------+-------------------------+
```

---

## Configuration Commands

### config show

Display current configuration settings.

```
unityauth config show
```

**Output:**

Shows all configured values from `~/.config/unityauth-cli/config.yml`:

```yaml
api_url: https://auth.example.com
default_format: table
timeout: 30
```

---

### config set

Set a configuration value.

```
unityauth config set KEY VALUE
```

**Available Keys:**

| Key | Description | Example |
|-----|-------------|---------|
| `api_url` | UnityAuth API endpoint | `https://auth.example.com` |
| `default_format` | Default output format | `table`, `json`, `csv` |
| `timeout` | Request timeout in seconds | `30`, `60` |

**Examples:**

```bash
# Set API endpoint
unityauth config set api_url https://auth.example.com

# Change default output format
unityauth config set default_format json

# Increase timeout for slow connections
unityauth config set timeout 60
```

---

### config edit

Open configuration file in the default text editor.

```
unityauth config edit
```

**Behavior:**

- Opens `~/.config/unityauth-cli/config.yml` in `$EDITOR` or system default editor
- Creates the file if it doesn't exist

---

## User Management Commands

### user create

Create a new user account with role assignments.

```
unityauth user create [OPTIONS]
```

**Required Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--email TEXT` | | User's email address (must be unique per tenant) |
| `--first-name TEXT` | | User's first name (1-100 characters) |
| `--last-name TEXT` | | User's last name (1-100 characters) |
| `--password TEXT` | | Initial password (minimum 8 characters) |
| `--tenant-id INTEGER` | `-t` | Tenant ID to assign the user to |
| `--role-ids TEXT` | `-r` | Comma-separated role IDs (e.g., "1,2,3") |

**Optional Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | `-n` | Preview the user creation without actually creating |

**Required Permissions:**

- `AUTH_SERVICE_EDIT-SYSTEM` (Unity Administrator), or
- `AUTH_SERVICE_EDIT-TENANT` (Tenant Administrator for the target tenant)

**Examples:**

```bash
# Create a basic user with one role
unityauth user create \
  --email user@example.com \
  --first-name John \
  --last-name Doe \
  --password "SecureP@ss123" \
  -t 1 \
  -r 2

# Create a user with multiple roles (using short flags)
unityauth user create \
  --email admin@example.com \
  --first-name Jane \
  --last-name Admin \
  --password "AdminP@ss456" \
  -t 1 -r "1,2,3"

# Preview user creation without executing (dry run)
unityauth user create --dry-run \
  --email user@example.com \
  --first-name John \
  --last-name Doe \
  --password "SecureP@ss123" \
  -t 1 -r 2
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "User already exists" | Email already used in this tenant | Use different email or update existing user |
| "Permission denied" | Insufficient permissions | Use account with admin permissions |
| "Tenant not found" | Invalid tenant ID | Check tenant ID with `tenant list` |

---

### user list

List all users in a specific tenant.

```
unityauth user list -t TENANT_ID
```

**Required Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--tenant-id INTEGER` | `-t` | Tenant ID to list users from |

**Output Columns:**

| Column | Description |
|--------|-------------|
| ID | User's unique identifier |
| Email | User's email address |
| First Name | User's first name |
| Last Name | User's last name |
| Roles | Assigned role IDs |

**Examples:**

```bash
# List users in tenant 1
unityauth user list -t 1

# Get JSON output for scripting (using short flags)
unityauth user list -t 1 -o json

# Export to CSV
unityauth user list -t 1 -o csv > users.csv
```

---

### user update

Update role assignments for an existing user.

```
unityauth user update USER_ID -t TENANT_ID -r ROLE_IDS
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `USER_ID` | The user's ID (from `user list`) |

**Required Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--tenant-id INTEGER` | `-t` | Tenant ID where roles are assigned |
| `--role-ids TEXT` | `-r` | Comma-separated role IDs to assign |

**Optional Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--dry-run` | `-n` | Preview the role changes without actually updating |

**Behavior:**

- Replaces ALL current roles for the user in the specified tenant
- Does not affect roles in other tenants

**Examples:**

```bash
# Update user 5's roles in tenant 1
unityauth user update 5 -t 1 -r "2,3"

# Assign a single role
unityauth user update 10 -t 1 -r 2

# Preview role changes without executing (dry run)
unityauth user update 5 --dry-run -t 1 -r "2,3"
```

---

### user update-profile

Update your own user profile (first name, last name, or password).

```
unityauth user update-profile USER_ID [OPTIONS]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `USER_ID` | Your user ID (from `token-info`) |

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--first-name TEXT` | | New first name (1-100 characters) |
| `--last-name TEXT` | | New last name (1-100 characters) |
| `--password TEXT` | | New password (minimum 8 characters) |
| `--dry-run` | `-n` | Preview the profile changes without actually updating |

**Behavior:**

- This is a **self-service** command: you can only update your own profile
- The `USER_ID` must match your authenticated user ID exactly
- At least one option must be provided
- Only the specified fields are updated; others remain unchanged

**Important Limitation:**

This command cannot be used by administrators to update other users' profiles. The backend enforces that the authenticated user can only modify their own account. To update another user's name or password, use the web interface or API directly.

**Examples:**

```bash
# First, check your user ID
unityauth token-info

# Update your first name
unityauth user update-profile 5 --first-name John

# Update your last name
unityauth user update-profile 5 --last-name Smith

# Change your password
unityauth user update-profile 5 --password "NewSecureP@ss123"

# Update multiple fields at once
unityauth user update-profile 5 --first-name John --last-name Smith --password "NewP@ss"

# Preview profile changes without executing (dry run)
unityauth user update-profile 5 --dry-run --first-name John --last-name Smith
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "User ID mismatch" | The user ID doesn't match your authenticated user | Use `token-info` to find your correct user ID. You can only update your own profile. |
| "At least one field must be provided" | No options specified | Provide `--first-name`, `--last-name`, or `--password` |
| "Password must be at least 8 characters" | Password too short | Use a longer password |

**Note:** To update another user's profile or roles, use `user update` (requires admin permissions).

---

## Tenant Commands

### tenant list

List all tenants accessible to the current user.

```
unityauth tenant list
```

**Behavior:**

- Unity Administrators see all tenants
- Tenant Administrators see only their assigned tenants

**Output Columns:**

| Column | Description |
|--------|-------------|
| ID | Tenant's unique identifier |
| Name | Tenant's display name |

**Examples:**

```bash
# List all accessible tenants
unityauth tenant list

# Get JSON output (using short flag)
unityauth tenant list -o json

# Get just tenant names using jq
unityauth tenant list -o json | jq -r '.[].name'
```

---

### tenant users

List all users belonging to a specific tenant.

```
unityauth tenant users TENANT_ID
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `TENANT_ID` | The tenant's ID |

**Output Columns:**

| Column | Description |
|--------|-------------|
| ID | User's unique identifier |
| Email | User's email address |
| First Name | User's first name |
| Last Name | User's last name |
| Roles | Assigned role IDs |

**Examples:**

```bash
# List users in tenant 1
unityauth tenant users 1

# Get JSON output (using short flag)
unityauth tenant users 1 -o json

# Count users in a tenant
unityauth tenant users 1 -o json | jq length
```

---

## Role Commands

### role list

List all roles defined in the system.

```
unityauth role list
```

**Output Columns:**

| Column | Description |
|--------|-------------|
| ID | Role's unique identifier |
| Name | Role's display name |
| Description | Role's description |

**Examples:**

```bash
# List all roles
unityauth role list

# Get JSON output (using short flag)
unityauth role list -o json

# Find a specific role ID
unityauth role list -o json | jq '.[] | select(.name == "Tenant Administrator")'
```

---

## Permissions Commands

### permissions list

List your permissions for a specific tenant and service.

```
unityauth permissions list -t TENANT_ID -s SERVICE_ID
```

**Required Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--tenant-id INTEGER` | `-t` | Tenant ID to check permissions for |
| `--service-id INTEGER` | `-s` | Service ID to check permissions for |

**Output:**

Returns all permissions the authenticated user has for the specified tenant and service combination.

**Examples:**

```bash
# List your permissions for tenant 1 and Libre311 service (ID: 1)
unityauth permissions list -t 1 -s 1

# Get JSON output (using short flags)
unityauth permissions list -t 1 -s 1 -o json

# Get CSV output
unityauth permissions list -t 1 -s 1 -o csv
```

**Sample Output:**

```
┌───────────────────────────────┐
│ Permission                    │
├───────────────────────────────┤
│ AUTH_SERVICE_VIEW-SYSTEM      │
│ AUTH_SERVICE_EDIT-SYSTEM      │
│ LIBRE311_ADMIN_VIEW-TENANT    │
│ LIBRE311_ADMIN_EDIT-TENANT    │
└───────────────────────────────┘
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| "No tenant found" | Invalid tenant ID | Check tenant ID with `tenant list` |
| "The service does not exist" | Invalid service ID | See [Known Limitations](#known-limitations) |
| "Tenant/Service not available" | User not authorized for this combination | Contact your administrator |

---

## Known Limitations

### Service Discovery

**There is currently no API endpoint to list available services.** The UnityAuth backend does not expose a `/api/services` endpoint, so the CLI cannot provide a `service list` command.

**What this means:**

- Commands that require `--service-id` (like `permissions list`) need you to know the service ID in advance
- Service IDs are configured by database administrators and are deployment-specific

**Current Services:**

In most UnityAuth deployments, the following service is available:

| ID | Name | Description |
|----|------|-------------|
| 1 | Libre311 | Libre311 citizen request management system |

**Workaround:**

If you don't know the service ID, contact your UnityAuth administrator or check the database directly:

```sql
SELECT id, name, description, status FROM service;
```

**For Developers:**

To add a `service list` command, a new API endpoint would need to be implemented in the UnityAuth backend (e.g., `GET /api/services`).

---

## Output Formats

### Table (Default)

Human-readable ASCII table format:

```
┌────┬─────────────────────┬────────────┬───────────┬───────┐
│ ID │ Email               │ First Name │ Last Name │ Roles │
├────┼─────────────────────┼────────────┼───────────┼───────┤
│ 1  │ admin@example.com   │ Admin      │ User      │ 1, 2  │
│ 2  │ user@example.com    │ Regular    │ User      │ 3     │
└────┴─────────────────────┴────────────┴───────────┴───────┘
```

### JSON

Machine-readable JSON for scripting:

```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "firstName": "Admin",
    "lastName": "User",
    "roles": [1, 2]
  }
]
```

### CSV

Spreadsheet-compatible comma-separated values:

```csv
id,email,firstName,lastName,roles
1,admin@example.com,Admin,User,"1, 2"
2,user@example.com,Regular,User,3
```

---

## Exit Codes

| Code | Name | Description |
|------|------|-------------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Validation, network, or API error |
| 2 | Authentication Error | Invalid credentials or expired token |
| 3 | Authorization Error | Insufficient permissions |
| 4 | Configuration Error | Missing or invalid configuration |

**Scripting Example:**

```bash
#!/bin/bash
unityauth login --email "$EMAIL" --password "$PASSWORD"
case $? in
  0) echo "Login successful" ;;
  2) echo "Invalid credentials" >&2; exit 1 ;;
  4) echo "API URL not configured" >&2; exit 1 ;;
  *) echo "Unknown error" >&2; exit 1 ;;
esac
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `UNITYAUTH_API_URL` | API endpoint URL | `https://auth.example.com` |
| `UNITYAUTH_EMAIL` | Login email | `admin@example.com` |
| `UNITYAUTH_PASSWORD` | Login password | `secret` |

**Usage in Scripts:**

```bash
#!/bin/bash
export UNITYAUTH_API_URL="https://auth.example.com"
export UNITYAUTH_EMAIL="admin@example.com"
export UNITYAUTH_PASSWORD="$ADMIN_PASSWORD"

# Login
unityauth login

# Perform operations
unityauth user list -t 1 -o json > users.json

# Cleanup
unityauth logout
```

---

## Troubleshooting

### "API URL not configured"

```bash
# First-time setup (recommended)
unityauth init

# Or manually set API URL
unityauth config set api_url https://auth.example.com

# Check current configuration
unityauth config show
```

### "Not authenticated"

```bash
# Check current session
unityauth token-info

# Re-authenticate
unityauth login
```

### "Permission denied"

Your account lacks the required permissions. Contact your Unity Administrator to grant:

- `AUTH_SERVICE_VIEW-SYSTEM` or `AUTH_SERVICE_VIEW-TENANT` for read operations
- `AUTH_SERVICE_EDIT-SYSTEM` or `AUTH_SERVICE_EDIT-TENANT` for write operations

### Network/Connection Errors

```bash
# Test connectivity
curl -I https://auth.example.com/keys

# Increase timeout
unityauth config set timeout 60

# Use verbose mode for debugging
unityauth --verbose tenant list
```

### Token Expired

```bash
# Check token status
unityauth token-info

# Re-authenticate
unityauth logout
unityauth login
```
