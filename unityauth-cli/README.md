# UnityAuth CLI

Command-line interface for UnityAuth administration.

## Overview

The UnityAuth CLI is a cross-platform command-line tool that enables system and tenant administrators to manage users, roles, and permissions in UnityAuth without using the web interface. It's designed for automation, batch operations, and scriptable workflows.

## Features

- **User Management**: Create, update, and list users
- **Authentication**: Secure login with OS-native token storage
- **Role & Tenant Discovery**: List available tenants and roles
- **Permission Verification**: Check user permissions for debugging
- **Batch Operations**: Create hundreds of users from CSV files
- **Multiple Output Formats**: Table, JSON, and CSV output
- **Automation-Friendly**: Non-interactive mode for scripts and CI/CD

## Installation

### Prerequisites

Before installing the UnityAuth CLI, ensure you have:

- **Python 3.11 or higher**
- **pip** (Python package installer)
- **UnityAuth API endpoint URL**
- **Valid UnityAuth administrator credentials**

#### Verify Python Installation

Check if Python 3.11+ is installed:

```bash
python3 --version
```

You should see output like `Python 3.11.x` or higher.

#### Install Python (if needed)

If Python is not installed or the version is too old:

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install python3.11 python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/) and run the installer. Make sure to check "Add Python to PATH" during installation.

#### Verify pip Installation

Check if pip is available:

```bash
python3 -m pip --version
```

If pip is not available, install it:

```bash
# Download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip
python3 get-pip.py

# Clean up
rm get-pip.py
```

### Install from PyPI (Production)

Once Python and pip are configured:

```bash
python3 -m pip install unityauth-cli
```

### Install for Development

For local development and testing:

```bash
# Clone the repository (if needed)
cd /path/to/UnityAuth/unityauth-cli

# Install in editable mode with development dependencies
python3 -m pip install -e .

# Or install with dev dependencies
python3 -m pip install -e ".[dev]"
```

### Verify Installation

Confirm the CLI is installed correctly:

```bash
unityauth --version
```

You should see output like `unityauth-cli version 1.0.0`.

## Quick Start

### 1. Configure API Endpoint

```bash
unityauth config set api_url https://auth.example.com
```

### 2. Login

```bash
unityauth login
```

You'll be prompted for your email and password. Your authentication token will be securely stored in your OS credential manager.

### 3. List Tenants

```bash
unityauth tenant list
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

## Common Commands

### Authentication

```bash
unityauth login                    # Login with credentials
unityauth logout                   # Remove stored token
unityauth token-info               # Display current session info
```

### User Management

```bash
unityauth user create ...          # Create a new user
unityauth user list --tenant-id 1  # List users in a tenant
unityauth user update USER_ID ...  # Update user roles
```

### Discovery

```bash
unityauth tenant list              # List accessible tenants
unityauth role list                # List available roles
unityauth permission get ...       # Get user permissions
```

### Batch Operations

```bash
unityauth batch create-users users.csv           # Create users from CSV
unityauth batch create-users users.csv --dry-run # Preview without creating
```

## Output Formats

The CLI supports three output formats:

- **table** (default): Human-readable ASCII tables
- **json**: Machine-readable JSON for scripting
- **csv**: Spreadsheet-compatible CSV

Example:

```bash
unityauth tenant list --format json | jq '.[0].name'
```

## Automation

### Non-Interactive Mode

Provide all parameters via command-line options:

```bash
unityauth login --email admin@example.com --password "$ADMIN_PASSWORD"
```

### Environment Variables

```bash
export UNITYAUTH_API_URL="https://auth.example.com"
export UNITYAUTH_EMAIL="admin@example.com"
export UNITYAUTH_PASSWORD="secret"

unityauth login
```

### Exit Codes

- `0`: Success
- `1`: General error (validation, network, API)
- `2`: Authentication error
- `3`: Permission error
- `4`: Configuration error

## Documentation

- [Quickstart Guide](../specs/001-unityauth-cli/quickstart.md) - Detailed usage examples
- [API Endpoints](../CLAUDE.md) - UnityAuth API reference
- [Project README](../README.md) - Main UnityAuth documentation

## Development

### Setting Up Development Environment

```bash
# Navigate to the CLI directory
cd unityauth-cli

# Install development dependencies
python3 -m pip install -r requirements-dev.txt

# Or install in editable mode with dev extras
python3 -m pip install -e ".[dev]"
```

### Running Tests

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=unityauth_cli
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Security

- **Token Storage**: JWT tokens are encrypted at rest using OS-native credential stores (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux)
- **HTTPS Required**: API communication requires HTTPS
- **No Password Storage**: Passwords are never stored; only JWT tokens
- **Secure CSV Handling**: CSV files containing passwords should be deleted after batch operations

## Support

- **GitHub Issues**: https://github.com/UnityFoundation-io/UnityAuth/issues
- **Documentation**: See [CLAUDE.md](../CLAUDE.md) for UnityAuth architecture

## License

MIT License - See LICENSE file for details
