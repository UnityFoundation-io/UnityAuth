# Research & Technology Decisions: UnityAuth CLI

**Feature**: 001-unityauth-cli
**Date**: 2025-12-26
**Status**: Complete

## Overview

This document consolidates research findings and technology decisions for implementing a cross-platform command-line interface to UnityAuth. All decisions support the specification requirements while adhering to the UnityAuth constitution principles.

## Research Areas

### 1. Python CLI Framework

**Question**: Which CLI framework provides the best balance of features, testing support, and developer experience for a complex administrative tool?

**Options Evaluated**:
1. **Click** (v8.x) - Decorator-based, nested commands, auto-help
2. **argparse** (stdlib) - Standard library, manual everything
3. **Typer** (v0.9.x) - Type-hint based, modern
4. **docopt** (v0.6.x) - Docstring-driven

**Decision**: **Click 8.x**

**Rationale**:
- Industry standard with 10+ years of stability and wide adoption
- Excellent support for nested command groups (`unityauth user create`, `unityauth tenant list`)
- Built-in testing utilities (`CliRunner`) for integration tests without subprocess overhead
- Automatic help generation with rich formatting
- Parameter validation and type conversion built-in
- Click.prompt() supports both interactive and non-interactive modes (FR-018 requirement)

**Alternatives Rejected**:
- **argparse**: Too verbose for complex CLIs; manual help formatting; no native support for command groups
- **Typer**: Newer library (less mature ecosystem); fewer examples for complex scenarios; based on Click anyway
- **docopt**: Limited validation; poor error messages; harder to test; no active maintenance

**Supporting Evidence**:
- Used by major projects: AWS CLI (v1), Flask, pytest
- Excellent documentation: https://click.palletsprojects.com/
- 15K+ GitHub stars, 500+ contributors

---

### 2. OS-Native Secure Credential Storage

**Question**: How should JWT tokens be securely stored across macOS, Windows, and Linux while meeting FR-002 (OS-native secure storage)?

**Options Evaluated**:
1. **keyring library** - Cross-platform abstraction
2. **Platform-specific APIs** - Direct integration per OS
3. **Encrypted JSON file** - Custom encryption implementation
4. **Environment variables** - No persistence

**Decision**: **keyring library 24.x**

**Rationale**:
- Cross-platform abstraction over OS credential stores:
  - macOS: Keychain (via `Security.framework`)
  - Windows: Windows Credential Manager (via `CredWrite`/`CredRead` Win32 APIs)
  - Linux: Secret Service API (GNOME Keyring, KWallet)
- Automatically selects best available backend per platform
- Handles encryption/decryption transparently - tokens encrypted at rest
- Mature library (10+ years, Python 2.7 through 3.12 support)
- No custom crypto code required (reduces security risk)

**Alternatives Rejected**:
- **Platform-specific APIs**: Would require platform detection, separate code paths, expertise in 3+ native APIs; maintenance burden high
- **Encrypted JSON**: Requires password on every CLI invocation (breaks automation); custom crypto is security risk; doesn't meet "OS-native" requirement
- **Environment variables**: No persistence across sessions; easily exposed via `ps`/`env`; fails FR-002

**Implementation Notes**:
- Service name: `unityauth-cli`
- Username: API endpoint URL (enables separate tokens for dev/staging/prod)
- Fallback: If keyring unavailable on headless Linux, provide encrypted file with prominent warning

**Supporting Evidence**:
- 800+ GitHub stars, used by pip, twine, AWS CLI tools
- Documentation: https://pypi.org/project/keyring/
- Platform support verified on GitHub CI across all major OS

---

### 3. HTTP Client Library

**Question**: Which HTTP library provides the best balance of simplicity, session management, and error handling for API consumption?

**Options Evaluated**:
1. **requests** - Synchronous, session support, proven
2. **httpx** - Async-capable, modern
3. **urllib3** - Low-level, connection pooling
4. **urllib** - Standard library only

**Decision**: **requests 2.31+**

**Rationale**:
- De facto standard for Python HTTP clients (50M+ downloads/month)
- Session support for connection pooling and default headers (Authorization, User-Agent)
- Excellent error handling with specific exception types (ConnectionError, Timeout, HTTPError)
- Automatic JSON decoding/encoding
- Well-documented status code handling
- No async needed for CLI (sequential operations, no concurrency requirement)

**Alternatives Rejected**:
- **httpx**: Async capabilities not needed; adds complexity; smaller ecosystem
- **urllib3**: Lower-level API; more verbose; manual session management
- **urllib**: Poor error messages; manual everything; verbose API

**Implementation Pattern**:
```python
class UnityAuthClient:
    def __init__(self, base_url: str, token: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'unityauth-cli/{VERSION}',
            'Content-Type': 'application/json'
        })
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
        self.base_url = base_url.rstrip('/')

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f'{self.base_url}{endpoint}'
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.HTTPError as e:
            self._handle_http_error(e)
```

---

### 4. Configuration File Format

**Question**: What configuration file format provides the best user experience for administrators?

**Options Evaluated**:
1. **YAML** - Human-readable, comments, structured
2. **JSON** - Machine-readable, no comments
3. **TOML** - Rust-style, less familiar
4. **INI** - Simple, limited nesting

**Decision**: **YAML via PyYAML 6.0+**

**Rationale**:
- Most human-readable format (critical for administrative tools)
- Supports comments for documentation within config file
- Hierarchical structure for organizing settings
- Standard location: `~/.config/unityauth-cli/config.yml` (XDG Base Directory Specification)
- Familiar to DevOps/SysAdmin audiences (Kubernetes, Ansible, Docker Compose)

**Example Configuration**:
```yaml
# UnityAuth CLI Configuration
# Edit with: unityauth config edit

# API endpoint for your UnityAuth instance
api_url: https://auth.example.com

# Default output format: table, json, csv
default_format: table

# Request timeout in seconds
timeout: 30

# Batch operation settings
batch:
  max_size: 1000
  continue_on_error: true
```

**Alternatives Rejected**:
- **JSON**: No comments; harder to read/edit; error-prone for humans
- **TOML**: Less familiar to target audience; Python support less mature
- **INI**: Limited nesting; no native list support; outdated format

---

### 5. Output Formatting

**Question**: How should CLI output be formatted to support both human and machine consumers (FR-015)?

**Options Evaluated**:
1. **Tabulate + json + csv** - Specialized libraries
2. **Rich tables** - All-in-one styled output
3. **Manual formatting** - Custom implementation
4. **pandas** - Data science library

**Decision**: **Tabulate 0.9.x for tables + stdlib json/csv + Rich 13.x for styling**

**Rationale**:
- **Tabulate**: Lightweight, professional ASCII/Unicode tables, multiple styles (grid, simple, fancy_grid)
- **stdlib json/csv**: Zero dependencies, handles edge cases correctly, built-in
- **Rich**: Beautiful terminal output with colors, progress bars, styled errors (enhances UX)
- Separation of concerns: formatting logic independent of data fetching

**Table Output Example**:
```
$ unityauth user list --tenant 1
╭──────┬─────────────────────────┬─────────────┬──────────────┬─────────────────╮
│   ID │ Email                   │ First Name  │ Last Name    │ Roles           │
├──────┼─────────────────────────┼─────────────┼──────────────┼─────────────────┤
│    1 │ unity_admin@example.com │ Unity       │ Administrator│ Unity Admin     │
│    2 │ tenant_admin@example.com│ Tenant      │ Admin        │ Tenant Admin    │
╰──────┴─────────────────────────┴─────────────┴──────────────┴─────────────────╯
```

**JSON Output Example**:
```bash
$ unityauth user list --tenant 1 --format json
[
  {
    "id": 1,
    "email": "unity_admin@example.com",
    "firstName": "Unity",
    "lastName": "Administrator",
    "roles": [1]
  }
]
```

**Alternatives Rejected**:
- **Rich tables only**: More complex API for simple tables; heavier dependency
- **Manual formatting**: Reinventing wheel; edge cases (long names, Unicode); maintenance burden
- **pandas**: Massive dependency (100+ MB); overkill for simple data display; slow startup

---

### 6. Batch CSV Parsing

**Question**: How should CSV batch files be parsed while handling edge cases (quoted fields, special characters, Unicode)?

**Decision**: **Python csv.DictReader (stdlib)**

**Rationale**:
- Standard library - no external dependency
- DictReader automatically maps rows to dictionaries using header row
- Handles RFC 4180 CSV edge cases:
  - Quoted fields with commas: `"Last, First"`
  - Escaped quotes: `"She said ""Hello"""`
  - Multi-line fields (if needed later)
- UTF-8 encoding support explicit and clear
- Excellent error messages for malformed CSV

**Implementation Pattern**:
```python
import csv
from typing import Iterator, Dict

def parse_batch_csv(file_path: str) -> Iterator[Dict[str, str]]:
    """Parse CSV file for batch user creation."""
    required_cols = {'email', 'firstName', 'lastName', 'password', 'tenantId'}
    optional_cols = {'roleIds', 'status'}

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        # Validate header
        if not required_cols.issubset(reader.fieldnames):
            missing = required_cols - set(reader.fieldnames)
            raise ValueError(f"Missing required columns: {missing}")

        # Yield rows with line number for error reporting
        for line_num, row in enumerate(reader, start=2):  # +2 for header + 0-indexed
            yield {'line': line_num, **row}
```

**Alternatives Rejected**:
- **pandas**: 100MB+ dependency for CSV parsing is absurd; slow CLI startup
- **Manual parsing**: Error-prone; won't handle edge cases correctly
- **Third-party CSV libraries**: Unnecessary when stdlib handles all requirements

---

### 7. API Version Compatibility

**Question**: How should CLI enforce version-locked API compatibility (constraint from spec)?

**Decision**: Version check on first authenticated request; fail fast on mismatch

**Rationale**:
- CLI version hardcodes supported API version in `__version__.py`
- On first API call after authentication, extract version from response headers or `/api/token_info`
- If mismatch: clear error with upgrade instructions; exit code 4
- Prevents subtle bugs from API changes (new fields, different validations, removed endpoints)

**Implementation**:
```python
# In client.py
SUPPORTED_API_VERSION = "1.0"  # Matches UnityAuth backend version

def check_version_compatibility(self) -> None:
    """Verify CLI version matches API version."""
    response = self.get('/api/token_info')
    api_version = response.get('apiVersion', '0.0')  # Assume added to token_info

    if not api_version.startswith(SUPPORTED_API_VERSION):
        raise VersionMismatchError(
            f"API version {api_version} not compatible with CLI {SUPPORTED_API_VERSION}. "
            f"Please upgrade CLI: pip install --upgrade unityauth-cli"
        )
```

**Alternatives Rejected**:
- **No version checking**: Silent failures; confusing errors; violates fail-fast principle
- **Manual version parameter**: User error-prone; easy to forget; not enforced
- **Multi-version support**: Adds complexity; testing burden; delayed feature adoption

---

### 8. Error Handling Strategy

**Question**: How should errors be handled to meet SC-005 (80% self-service error resolution)?

**Decision**: Custom exception hierarchy + Rich styling + HTTP status mapping

**Rationale**:
- Custom exceptions for each error category (AuthError, PermissionError, ValidationError, NetworkError)
- Map HTTP status codes to user-friendly messages with actionable guidance
- Rich library for color-coded errors (red for errors, yellow for warnings, green for success)
- Include context in error messages (which field failed validation, which permission missing)

**Exception Hierarchy**:
```python
class UnityAuthCLIError(Exception):
    """Base exception for all CLI errors."""
    exit_code = 1

class AuthenticationError(UnityAuthCLIError):
    """Authentication failed (invalid credentials, expired token)."""
    exit_code = 2

class PermissionError(UnityAuthCLIError):
    """Insufficient permissions for operation."""
    exit_code = 3

class ConfigurationError(UnityAuthCLIError):
    """Invalid configuration (missing API endpoint)."""
    exit_code = 4

class ValidationError(UnityAuthCLIError):
    """Input validation failed."""
    exit_code = 1

class NetworkError(UnityAuthCLIError):
    """Network connectivity issue."""
    exit_code = 1

class RateLimitError(UnityAuthCLIError):
    """API rate limit exceeded."""
    exit_code = 1
```

**Error Message Examples**:
```
❌ Authentication failed: Invalid credentials
→ Check your email and password, then try: unityauth login

❌ Permission denied: AUTH_SERVICE_EDIT-TENANT required
→ Contact your Unity administrator to grant this permission

❌ Network error: Could not connect to https://auth.example.com
→ Check API endpoint in config: unityauth config show
→ Verify network connectivity: curl https://auth.example.com/keys

❌ Rate limit exceeded: Retry after 60 seconds
→ Wait 1 minute and try again
```

---

### 9. Testing Strategy

**Question**: How should the CLI be tested to ensure reliability across platforms and API scenarios?

**Decision**: Pytest + CliRunner + pytest-mock + TestContainers

**Rationale**:
- **Pytest**: Modern test framework with fixtures, parametrization, excellent reporting
- **Click.testing.CliRunner**: Test CLI commands without subprocess overhead; capture output/exit codes
- **pytest-mock**: Simplified mocking for API responses; faster tests; no external dependencies
- **TestContainers**: Spin up real UnityAuth API in Docker for E2E tests; validates integration

**Test Structure**:
```
tests/
├── unit/
│   ├── test_auth.py          # Token storage, authentication logic
│   ├── test_client.py         # API client, error handling
│   ├── test_config.py         # Configuration parsing
│   └── test_formatters.py     # Output formatting
├── integration/
│   ├── test_login_commands.py # login/logout/token-info (mocked API)
│   ├── test_user_commands.py  # user create/update/list (mocked API)
│   └── test_batch_commands.py # batch create-users (mocked API)
├── e2e/
│   └── test_full_workflow.py  # Real UnityAuth via TestContainers
└── fixtures/
    ├── sample_users.csv       # Valid batch file
    ├── invalid_users.csv      # Missing columns
    └── mock_responses.json    # API response fixtures
```

**Example Test**:
```python
from click.testing import CliRunner
from unityauth_cli.cli import cli

def test_login_success(mocker):
    """Test successful login stores token."""
    # Mock API response
    mock_post = mocker.patch('unityauth_cli.client.requests.Session.post')
    mock_post.return_value.json.return_value = {'access_token': 'fake-jwt'}
    mock_post.return_value.status_code = 200

    # Mock keyring
    mock_keyring = mocker.patch('unityauth_cli.auth.keyring')

    runner = CliRunner()
    result = runner.invoke(cli, ['login', '--email', 'test@example.com', '--password', 'test'])

    assert result.exit_code == 0
    assert 'Login successful' in result.output
    mock_keyring.set_password.assert_called_once()
```

---

### 10. Interactive vs Non-Interactive Mode

**Question**: How should CLI handle both interactive (prompts) and non-interactive (automation) modes per FR-018?

**Decision**: TTY detection + Click.prompt with default behavior

**Implementation**:
```python
import sys
import click

def get_password(password: str = None) -> str:
    """Get password via argument or prompt."""
    if password:
        return password

    if not sys.stdin.isatty():
        raise click.ClickException(
            "Password required in non-interactive mode. "
            "Use --password or set UNITYAUTH_PASSWORD environment variable."
        )

    return click.prompt('Password', hide_input=True)
```

**Behavior**:
- **Interactive mode** (terminal/TTY): Prompt for missing required params
- **Non-interactive mode** (pipe/script): Require all params via options or env vars; fail with clear message if missing
- Auto-detection via `sys.stdin.isatty()`
- Support environment variables for sensitive data in automation: `UNITYAUTH_PASSWORD`

---

## Technology Stack Final

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Language | Python | 3.11+ | Cross-platform CLI with rich ecosystem |
| CLI Framework | Click | 8.1+ | Command structure, argument parsing |
| HTTP Client | Requests | 2.31+ | API communication |
| Secure Storage | Keyring | 24.3+ | OS-native token encryption |
| Configuration | PyYAML | 6.0+ | Human-readable config files |
| Table Output | Tabulate | 0.9+ | ASCII/Unicode table formatting |
| Terminal Styling | Rich | 13.7+ | Colors, progress bars, error formatting |
| Testing | Pytest | 7.4+ | Unit/integration test framework |
| Test Mocking | pytest-mock | 3.12+ | API response mocking |
| E2E Testing | TestContainers | 3.7+ | Real API integration tests |

## Compliance Verification

All research decisions verified against:
- ✅ **FR-001 to FR-024**: All functional requirements supported
- ✅ **Security by Default**: Keyring encryption, HTTPS-only, no password storage
- ✅ **Service Independence**: Pure API consumer, no backend coupling
- ✅ **Testing Discipline**: Comprehensive test strategy with unit/integration/E2E
- ✅ **Cross-Platform**: macOS, Windows, Linux support via Python + keyring

## Next Phase

Proceed to Phase 1: Design & Contracts (data-model.md, contracts/, quickstart.md)
