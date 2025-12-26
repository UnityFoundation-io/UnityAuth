# UnityAuth CLI Quickstart Guide

**Version**: 1.0.0
**Date**: 2025-12-26
**For**: System and Tenant Administrators

## What is UnityAuth CLI?

The UnityAuth CLI is a command-line tool that enables administrators to manage users, roles, and permissions in UnityAuth without using the web interface. It's designed for:

- **Automation**: Script user provisioning in deployment pipelines
- **Batch Operations**: Create hundreds of users from CSV files
- **Speed**: Perform common tasks 60% faster than the web UI
- **Flexibility**: Integrate with existing administrative scripts and workflows

## Installation

### Prerequisites

- **Python 3.11 or higher** - Check with `python3 --version`
- **UnityAuth API access** - You need the API endpoint URL (e.g., `https://auth.example.com`)
- **Valid credentials** - Email and password for a UnityAuth account with appropriate permissions

### Install via pip

```bash
pip install unityauth-cli
```

### Verify Installation

```bash
unityauth --version
```

You should see output like:
```
unityauth-cli version 1.0.0
```

## First-Time Setup

### 1. Configure API Endpoint

Tell the CLI where your UnityAuth API is located:

```bash
unityauth config set api_url https://auth.example.com
```

Replace `https://auth.example.com` with your actual UnityAuth API endpoint.

### 2. Login

Authenticate with your UnityAuth credentials:

```bash
unityauth login
```

You'll be prompted for:
- **Email**: Your UnityAuth account email
- **Password**: Your password (hidden while typing)

**Successful login output**:
```
✓ Login successful as admin@example.com
```

Your authentication token is now securely stored in your operating system's credential manager (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux).

### 3. Verify Authentication

Check your current session:

```bash
unityauth token-info
```

**Example output**:
```
╭─────────────────┬────────────────────────────────────────╮
│ Field           │ Value                                  │
├─────────────────┼────────────────────────────────────────┤
│ User Email      │ admin@example.com                      │
│ Token Expires   │ 2025-12-27T10:30:00Z                   │
│ API Version     │ 1.0.0                                  │
│ Authenticated   │ Yes                                    │
╰─────────────────┴────────────────────────────────────────╯
```

## Common Tasks

### List Tenants

View all tenants you have access to:

```bash
unityauth tenant list
```

**Example output**:
```
╭──────┬──────────────────╮
│   ID │ Name             │
├──────┼──────────────────┤
│    1 │ Example Corp     │
│    2 │ Acme Inc         │
╰──────┴──────────────────╯
```

### List Users in a Tenant

View all users in a specific tenant:

```bash
unityauth user list --tenant-id 1
```

**Example output**:
```
╭──────┬─────────────────────────┬────────────┬──────────────┬────────╮
│   ID │ Email                   │ First Name │ Last Name    │ Roles  │
├──────┼─────────────────────────┼────────────┼──────────────┼────────┤
│    1 │ unity_admin@example.com │ Unity      │ Administrator│ 1      │
│    2 │ tenant_admin@example.com│ Tenant     │ Admin        │ 2      │
╰──────┴─────────────────────────┴────────────┴──────────────┴────────╯
```

### List Available Roles

See what roles can be assigned to users:

```bash
unityauth role list
```

**Example output**:
```
╭──────┬─────────────────────────┬─────────────────────────────────────╮
│   ID │ Name                    │ Description                         │
├──────┼─────────────────────────┼─────────────────────────────────────┤
│    1 │ Unity Administrator     │ System-wide administrative access   │
│    2 │ Tenant Administrator    │ Tenant-level administrative access  │
│    3 │ Libre311 Admin          │ Libre311 service administrator      │
╰──────┴─────────────────────────┴─────────────────────────────────────╯
```

### Create a Single User

Create a new user with specific roles:

```bash
unityauth user create \
  --email newuser@example.com \
  --first-name John \
  --last-name Doe \
  --password "MySecureP@ss123" \
  --tenant-id 1 \
  --role-ids 2,3
```

**Successful output**:
```
✓ User created successfully (ID: 15)
```

### Update User Roles

Change a user's role assignments for a tenant:

```bash
unityauth user update 15 --tenant-id 1 --role-ids 3,4
```

This replaces the user's existing roles in tenant 1 with roles 3 and 4.

### Check Your Permissions

See what permissions you have in a specific tenant and service:

```bash
unityauth permission get --tenant-id 1 --service-id 1
```

**Example output**:
```
Permissions for admin@example.com in Tenant 1, Service 1:
- AUTH_SERVICE_VIEW-SYSTEM
- AUTH_SERVICE_EDIT-SYSTEM
- AUTH_SERVICE_VIEW-TENANT
- AUTH_SERVICE_EDIT-TENANT
```

## Batch User Creation

### Prepare CSV File

Create a CSV file named `users.csv` with this format:

```csv
email,firstName,lastName,password,tenantId,roleIds
john.doe@example.com,John,Doe,Pass123!,1,2|3
jane.smith@example.com,Jane,Smith,Pass456!,1,3
bob.jones@example.com,Bob,Jones,Pass789!,1,2
```

**Column Requirements**:
- **email** (required): Valid email address
- **firstName** (required): 1-100 characters
- **lastName** (required): 1-100 characters
- **password** (required): Minimum 8 characters
- **tenantId** (required): Positive integer
- **roleIds** (optional): Pipe-separated role IDs (e.g., `2|3|4`)
- **status** (optional): `ENABLED` or `DISABLED` (default: ENABLED)

### Preview Batch Operation (Dry Run)

Before creating users, preview what will happen:

```bash
unityauth batch create-users users.csv --dry-run
```

This validates the file and shows you what would be created without actually making API calls.

### Create Users from CSV

Process the batch file:

```bash
unityauth batch create-users users.csv
```

**Example output**:
```
Processing row 1/3... [████████████████████████████████] 100%
✓ Created 3 users successfully
```

### Handle Errors in Batch

By default, the CLI continues processing even if individual records fail. To stop on the first error:

```bash
unityauth batch create-users users.csv --no-continue-on-error
```

## Output Formats

The CLI supports three output formats:

### Table (Default)

Human-readable tables with borders:

```bash
unityauth tenant list
```

### JSON

Machine-readable JSON for scripting:

```bash
unityauth tenant list --format json
```

**Output**:
```json
[
  {"id": 1, "name": "Example Corp"},
  {"id": 2, "name": "Acme Inc"}
]
```

### CSV

Spreadsheet-compatible CSV format:

```bash
unityauth tenant list --format csv
```

**Output**:
```csv
id,name
1,Example Corp
2,Acme Inc
```

You can pipe JSON output to tools like `jq`:

```bash
unityauth tenant list --format json | jq '.[0].name'
```

## Configuration Management

### View Current Configuration

```bash
unityauth config show
```

### Set Configuration Values

```bash
# Change default output format
unityauth config set default_format json

# Increase request timeout
unityauth config set timeout 60

# Change batch size limit
unityauth config set batch.max_size 500
```

### Edit Configuration File Directly

```bash
unityauth config edit
```

This opens the configuration file in your default text editor.

**Configuration file location**:
- **Linux/macOS**: `~/.config/unityauth-cli/config.yml`
- **Windows**: `%APPDATA%\unityauth-cli\config.yml`

## Automation and Scripting

### Non-Interactive Mode

For automation, provide all parameters as command-line options:

```bash
unityauth login \
  --email admin@example.com \
  --password "$ADMIN_PASSWORD"
```

### Environment Variables

Set credentials via environment variables:

```bash
export UNITYAUTH_EMAIL="admin@example.com"
export UNITYAUTH_PASSWORD="secret"
export UNITYAUTH_API_URL="https://auth.example.com"

unityauth login
```

### Exit Codes

Use exit codes in scripts to handle success/failure:

```bash
if unityauth user create --email test@example.com --first-name Test --last-name User --password "Pass123!" --tenant-id 1 --role-ids 2; then
    echo "User created successfully"
else
    echo "Failed to create user"
    exit 1
fi
```

**Exit codes**:
- `0` - Success
- `1` - General error (validation, network, API)
- `2` - Authentication error
- `3` - Permission error
- `4` - Configuration error

### Example Automation Script

```bash
#!/bin/bash
# Automated user provisioning script

set -e  # Exit on error

# Login
unityauth login --email "$ADMIN_EMAIL" --password "$ADMIN_PASSWORD"

# Create users from CSV
unityauth batch create-users new_employees.csv

# Verify tenant status
unityauth tenant list --format json | jq '.[] | select(.id == 1)'

# Logout
unityauth logout

echo "Provisioning complete"
```

## Troubleshooting

### Authentication Issues

**Problem**: `✗ Authentication failed: Invalid credentials`

**Solutions**:
1. Verify your email and password are correct
2. Check API endpoint: `unityauth config show`
3. Test API directly: `curl https://your-api-url/keys`

### Permission Errors

**Problem**: `✗ Permission denied: AUTH_SERVICE_EDIT-TENANT required`

**Solution**: Contact your Unity administrator to grant the necessary permission.

### Network Issues

**Problem**: `✗ Network error: Could not connect to https://auth.example.com`

**Solutions**:
1. Check API URL: `unityauth config show`
2. Verify network connectivity: `ping auth.example.com`
3. Check firewall rules

### Token Expiration

**Problem**: `✗ Authentication required. Run: unityauth login`

**Solution**: Your token has expired. Login again:

```bash
unityauth login
```

### Configuration Problems

**Problem**: `✗ Configuration error: Missing API URL`

**Solution**: Set the API endpoint:

```bash
unityauth config set api_url https://auth.example.com
```

### Batch File Errors

**Problem**: `✗ Batch operation failed: Missing required columns: firstName`

**Solution**: Ensure your CSV has all required columns with correct spelling:
```csv
email,firstName,lastName,password,tenantId
```

## Advanced Usage

### Rate Limiting

If you encounter rate limiting errors, add a delay between batch requests:

```bash
unityauth batch create-users users.csv --delay 100
```

This adds a 100ms delay between each API request.

### Verbose Output

Enable debug output to troubleshoot issues:

```bash
unityauth --verbose user create --email test@example.com ...
```

### Multiple Environments

Store credentials for different environments (dev, staging, prod):

```bash
# Development
unityauth config set api_url https://auth-dev.example.com
unityauth login --email dev_admin@example.com

# Production (different API URL = different stored token)
unityauth config set api_url https://auth.example.com
unityauth login --email prod_admin@example.com
```

The CLI stores separate tokens for each API endpoint.

## Getting Help

### Command Help

Get help for any command:

```bash
unityauth --help
unityauth user create --help
unityauth batch create-users --help
```

### Support Resources

- **GitHub Issues**: https://github.com/your-org/unityauth-cli/issues
- **Documentation**: See [CLAUDE.md](../../../CLAUDE.md) in the UnityAuth repository
- **API Documentation**: Your UnityAuth API endpoint + `/docs` (if available)

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for automation scripts
3. **Rotate passwords regularly** for CLI accounts
4. **Limit CLI account permissions** to only what's needed
5. **Logout when done** on shared machines: `unityauth logout`
6. **Protect CSV files** with user passwords - delete after use

## Next Steps

- Explore all commands: `unityauth --help`
- Set up automated user provisioning with batch files
- Integrate CLI into CI/CD pipelines
- Create custom scripts for your organization's workflows
- Review the [specification](spec.md) for detailed feature information

## Quick Reference

### Most Common Commands

```bash
# Authentication
unityauth login
unityauth logout
unityauth token-info

# User Management
unityauth user create --email EMAIL --first-name FIRST --last-name LAST --password PASS --tenant-id ID --role-ids IDS
unityauth user list --tenant-id ID
unityauth user update USER_ID --tenant-id ID --role-ids IDS

# Discovery
unityauth tenant list
unityauth role list
unityauth permission get --tenant-id ID --service-id ID

# Batch Operations
unityauth batch create-users FILE.csv
unityauth batch create-users FILE.csv --dry-run

# Configuration
unityauth config show
unityauth config set api_url URL
```

---

**Ready to get started?** Run `unityauth login` and begin managing your UnityAuth users from the command line!
