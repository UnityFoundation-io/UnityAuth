# UnityAuth CLI

Command-line interface for UnityAuth administration.

## Overview

The UnityAuth CLI is a cross-platform command-line tool that enables system and tenant administrators to manage users, roles, and permissions in UnityAuth without using the web interface. It's designed for automation, batch operations, and scriptable workflows.

## Current Status

| Feature | Status |
|---------|--------|
| Authentication (login/logout/token-info) | Implemented |
| User Management (create/list/update/update-profile) | Implemented |
| Tenant Discovery (list/users) | Implemented |
| Role Discovery (list) | Implemented |
| Permissions Discovery (list) | Implemented |
| Configuration Management | Implemented |
| Service Discovery (list) | Not Available (see [Known Limitations](#known-limitations)) |
| Batch Operations | Planned |

## Installation

### Prerequisites

- **Python 3.11 or higher**
- **pip** (Python package installer)
- **UnityAuth API endpoint URL**
- **Valid UnityAuth administrator credentials**

#### Verify Python Installation

```bash
python3 --version
# Should show Python 3.11.x or higher
```

#### Install Python (if needed)

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/) and run the installer. Check "Add Python to PATH" during installation.

### Install from Source (Development)

```bash
cd unityauth-cli

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
python3 -m pip install -e .
```

### Verify Installation

```bash
unityauth --version
```

## Quick Start

### 1. Configure API Endpoint

```bash
unityauth config set api_url https://auth.example.com
```

### 2. Login

```bash
unityauth login
# Enter email and password when prompted
```

Your authentication token is securely stored in your OS credential manager (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux).

### 3. Explore the System

```bash
# List accessible tenants
unityauth tenant list

# List available roles
unityauth role list

# List users in a tenant
unityauth tenant users 1
```

### 4. Create a User

```bash
unityauth user create \
  --email newuser@example.com \
  --first-name John \
  --last-name Doe \
  --password "MySecureP@ss123" \
  --tenant-id 1 \
  --role-ids 2,3
```

## Command Structure

```
unityauth
├── login          # Authenticate with UnityAuth
├── logout         # Remove stored credentials
├── token-info     # Display session information
├── config         # Configuration management
│   ├── show       # Display current config
│   ├── set        # Set a config value
│   └── edit       # Open config in editor
├── user           # User management
│   ├── create     # Create a new user
│   ├── list       # List users in a tenant
│   ├── update     # Update user roles
│   └── update-profile  # Update your own profile
├── tenant         # Tenant discovery
│   ├── list       # List accessible tenants
│   └── users      # List users in a tenant
├── role           # Role discovery
│   └── list       # List available roles
└── permissions    # Permission discovery
    └── list       # List your permissions for a tenant/service
```

## Global Options

All commands support these global options:

| Option | Description |
|--------|-------------|
| `--api-url TEXT` | Override API URL from config |
| `--format [table\|json\|csv]` | Output format (default: table) |
| `--verbose` | Enable debug output |
| `--version` | Show version and exit |
| `--help` | Show help message |

## Output Formats

```bash
# Human-readable table (default)
unityauth tenant list

# Machine-readable JSON
unityauth tenant list --format json

# Spreadsheet-compatible CSV
unityauth tenant list --format csv

# Pipe JSON to jq for processing
unityauth tenant list --format json | jq '.[0].name'
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `UNITYAUTH_API_URL` | API endpoint URL |
| `UNITYAUTH_EMAIL` | Login email address |
| `UNITYAUTH_PASSWORD` | Login password (for non-interactive mode) |

Example:
```bash
export UNITYAUTH_API_URL="https://auth.example.com"
unityauth login --email admin@example.com
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (validation, network, API) |
| 2 | Authentication error |
| 3 | Permission/authorization error |
| 4 | Configuration error |

## Configuration

Configuration is stored in `~/.config/unityauth-cli/config.yml`:

```yaml
api_url: https://auth.example.com
default_format: table
timeout: 30
```

Manage configuration:
```bash
unityauth config show              # View current settings
unityauth config set api_url URL   # Set API endpoint
unityauth config set timeout 60    # Set request timeout
unityauth config edit              # Open in editor
```

## Known Limitations

### No Service Discovery API

The UnityAuth backend does not expose an API endpoint to list available services. This means:

- **No `service list` command**: The CLI cannot retrieve a list of services
- **Service IDs must be known in advance**: Commands like `permissions list` require a `--service-id` that users must know beforehand

**Common Service IDs:**

| ID | Name | Description |
|----|------|-------------|
| 1 | Libre311 | Libre311 citizen request management |

**Workaround:** Contact your UnityAuth administrator for the correct service ID, or query the database directly if you have access:

```sql
SELECT id, name, description FROM service WHERE status = 'ENABLED';
```

**For Backend Developers:** To enable service discovery in the CLI, implement a `GET /api/services` endpoint in the UnityAuth backend.

## Documentation

- [User Guide](docs/user-guide.md) - Complete command reference

- [API Reference](docs/api-reference.md) - UnityAuth API documentation

## Development

### Setup

```bash
cd unityauth-cli
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/unit/
pytest --cov=unityauth_cli
```

### Code Quality

```bash
black src/           # Format code
flake8 src/          # Lint
mypy src/            # Type checking
```

## Security

- **Token Storage**: JWT tokens encrypted using OS-native credential stores
- **HTTPS Required**: All API communication uses HTTPS
- **No Password Storage**: Only JWT tokens are persisted, never passwords
- **Secure Prompts**: Password input is hidden when typing

## License

MIT License - See LICENSE file for details.
