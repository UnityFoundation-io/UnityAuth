# UnityAuth CLI User Guide

Complete command reference for the UnityAuth command-line interface.

## Table of Contents

- [Global Options](#global-options)
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
- [Tenant Commands](#tenant-commands)
  - [tenant list](#tenant-list)
  - [tenant users](#tenant-users)
- [Role Commands](#role-commands)
  - [role list](#role-list)
- [Output Formats](#output-formats)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Global Options

These options are available for all commands:

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--api-url TEXT` | `UNITYAUTH_API_URL` | Override the API endpoint URL |
| `--format [table\|json\|csv]` | - | Set output format (default: table) |
| `--verbose` | - | Enable debug/verbose output |
| `--version` | - | Show version and exit |
| `--help` | - | Show help message and exit |

**Examples:**

```bash
# Override API URL for a single command
unityauth --api-url https://staging.example.com tenant list

# Get JSON output
unityauth --format json role list

# Enable verbose mode for debugging
unityauth --verbose login
```

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
| API URL | Current API endpoint |
| Token Status | Valid/Expired/Not Found |
| Expires | Token expiration time (if available) |

**Examples:**

```bash
# Table output
unityauth token-info

# JSON output for scripting
unityauth token-info --format json
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

| Option | Description |
|--------|-------------|
| `--email TEXT` | User's email address (must be unique per tenant) |
| `--first-name TEXT` | User's first name (1-100 characters) |
| `--last-name TEXT` | User's last name (1-100 characters) |
| `--password TEXT` | Initial password (minimum 8 characters) |
| `--tenant-id INTEGER` | Tenant ID to assign the user to |
| `--role-ids TEXT` | Comma-separated role IDs (e.g., "1,2,3") |

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
  --tenant-id 1 \
  --role-ids 2

# Create a user with multiple roles
unityauth user create \
  --email admin@example.com \
  --first-name Jane \
  --last-name Admin \
  --password "AdminP@ss456" \
  --tenant-id 1 \
  --role-ids "1,2,3"
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
unityauth user list --tenant-id TENANT_ID
```

**Required Options:**

| Option | Description |
|--------|-------------|
| `--tenant-id INTEGER` | Tenant ID to list users from |

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
unityauth user list --tenant-id 1

# Get JSON output for scripting
unityauth user list --tenant-id 1 --format json

# Export to CSV
unityauth user list --tenant-id 1 --format csv > users.csv
```

---

### user update

Update role assignments for an existing user.

```
unityauth user update USER_ID --tenant-id TENANT_ID --role-ids ROLE_IDS
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `USER_ID` | The user's ID (from `user list`) |

**Required Options:**

| Option | Description |
|--------|-------------|
| `--tenant-id INTEGER` | Tenant ID where roles are assigned |
| `--role-ids TEXT` | Comma-separated role IDs to assign |

**Behavior:**

- Replaces ALL current roles for the user in the specified tenant
- Does not affect roles in other tenants

**Examples:**

```bash
# Update user 5's roles in tenant 1
unityauth user update 5 --tenant-id 1 --role-ids "2,3"

# Assign a single role
unityauth user update 10 --tenant-id 1 --role-ids 2
```

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

# Get JSON output
unityauth tenant list --format json

# Get just tenant names using jq
unityauth tenant list --format json | jq -r '.[].name'
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

# Get JSON output
unityauth tenant users 1 --format json

# Count users in a tenant
unityauth tenant users 1 --format json | jq length
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

# Get JSON output
unityauth role list --format json

# Find a specific role ID
unityauth role list --format json | jq '.[] | select(.name == "Tenant Administrator")'
```

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
unityauth user list --tenant-id 1 --format json > users.json

# Cleanup
unityauth logout
```

---

## Troubleshooting

### "API URL not configured"

```bash
# Check current configuration
unityauth config show

# Set API URL
unityauth config set api_url https://auth.example.com
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
