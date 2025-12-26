# Data Model: UnityAuth CLI

**Feature**: 001-unityauth-cli
**Date**: 2025-12-26
**Status**: Design Complete

## Overview

This document defines the command structure, internal data models, and state management for the UnityAuth CLI. The CLI is a stateless tool that stores minimal configuration and credentials, relying primarily on the UnityAuth API for all data operations.

## Command Hierarchy

The CLI uses a resource-oriented command structure with `unityauth` as the root command:

```
unityauth [GLOBAL OPTIONS] COMMAND [COMMAND OPTIONS] [ARGUMENTS]
```

### Global Options

Available on all commands:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--api-url` | string | From config | UnityAuth API endpoint URL |
| `--format` | choice | table | Output format: table, json, csv |
| `--verbose` | flag | false | Enable verbose/debug output |
| `--help` | flag | - | Show help message |
| `--version` | flag | - | Show CLI version |

### Command Tree

```
unityauth/
├── login                    # Authenticate and store token
├── logout                   # Remove stored credentials
├── token-info               # Display current token information
├── config/
│   ├── show                 # Display current configuration
│   ├── set KEY VALUE        # Set configuration value
│   └── edit                 # Open config file in editor
├── user/
│   ├── create               # Create a new user
│   ├── update ID            # Update user profile/roles
│   └── list                 # List users for a tenant
├── tenant/
│   ├── list                 # List accessible tenants
│   └── users ID             # List users in a tenant
├── role/
│   └── list                 # List all available roles
├── permission/
│   ├── get                  # Get user permissions for tenant/service
│   └── check                # Check if user has specific permissions
└── batch/
    └── create-users FILE    # Batch create users from CSV
```

## CLI Internal Entities

### 1. Configuration

**Purpose**: Stores CLI settings and API connection details

**Storage Location**: `~/.config/unityauth-cli/config.yml` (Unix) or `%APPDATA%\unityauth-cli\config.yml` (Windows)

**Schema**:
```yaml
# UnityAuth CLI Configuration File
# Version: 1.0

# API endpoint for UnityAuth instance (required)
api_url: string (URL)

# API version supported by this CLI
api_version: string (semver)

# Default output format for commands
default_format: string (enum: table, json, csv)

# Request timeout in seconds
timeout: integer (default: 30, min: 5, max: 300)

# Batch operation settings
batch:
  max_size: integer (default: 1000)
  continue_on_error: boolean (default: true)
  delay_ms: integer (default: 0, for rate limit throttling)

# Output settings
output:
  show_headers: boolean (default: true)
  table_style: string (default: grid, options: plain, simple, grid, fancy_grid)
  color_enabled: boolean (default: true, auto-detect TTY)
```

**Validation Rules**:
- `api_url`: Must be valid HTTPS URL (HTTP rejected per constraints)
- `api_version`: Must match semantic versioning pattern (e.g., "1.0.0")
- `timeout`: Between 5 and 300 seconds
- `batch.max_size`: Between 1 and 10000

---

### 2. Credentials

**Purpose**: Securely stores JWT authentication token

**Storage**: OS-native secure storage via keyring library
- Service name: `unityauth-cli`
- Username: API endpoint URL (enables multiple environment tokens)
- Password: JWT bearer token

**Access Pattern**:
```python
import keyring

# Store token after login
keyring.set_password('unityauth-cli', api_url, jwt_token)

# Retrieve token for API calls
token = keyring.get_password('unityauth-cli', api_url)

# Delete token on logout
keyring.delete_password('unityauth-cli', api_url)
```

**Security Properties**:
- Encrypted at rest by OS (Keychain/Credential Manager/Secret Service)
- Not accessible to other users on system
- Persists across reboots
- Automatically cleaned up on logout

---

### 3. Session Context

**Purpose**: Runtime context for current command execution

**Lifecycle**: Created at command start, destroyed at command end (ephemeral)

**Schema**:
```python
@dataclass
class SessionContext:
    """Runtime context for CLI command execution."""

    # Configuration
    config: Configuration
    api_url: str
    api_version: str

    # Authentication
    token: Optional[str]  # JWT from keyring
    is_authenticated: bool

    # Current user info (from /api/token_info)
    user_email: Optional[str]
    user_id: Optional[int]
    user_roles: List[Dict[str, Any]]

    # Command execution
    output_format: str  # Resolved from --format or config
    verbose: bool

    # API client
    client: UnityAuthAPIClient
```

**Initialization Flow**:
1. Load configuration from file (or use defaults)
2. Override config with command-line options
3. Load token from keyring (if exists)
4. Create API client with token
5. Verify API version compatibility (first request)

---

### 4. Batch Record

**Purpose**: Represents a single user record from batch CSV file

**CSV Schema** (from spec FR-014):

| Column | Required | Type | Validation | Example |
|--------|----------|------|------------|---------|
| email | Yes | string | Valid email format | user@example.com |
| firstName | Yes | string | Not blank, max 100 chars | John |
| lastName | Yes | string | Not blank, max 100 chars | Doe |
| password | Yes | string | Not blank, min 8 chars | MyP@ssw0rd! |
| tenantId | Yes | integer | Positive integer | 1 |
| roleIds | No | string | Pipe-separated integers | 1\|2\|3 |
| status | No | string | enum: ENABLED, DISABLED | ENABLED |

**Internal Representation**:
```python
@dataclass
class BatchUserRecord:
    """User record from CSV batch file."""

    # Required fields
    email: str
    first_name: str
    last_name: str
    password: str
    tenant_id: int

    # Optional fields
    role_ids: List[int] = field(default_factory=list)
    status: str = "ENABLED"

    # Metadata
    line_number: int  # For error reporting

    def validate(self) -> List[str]:
        """Validate record fields. Returns list of error messages."""
        errors = []

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.email):
            errors.append(f"Line {self.line_number}: Invalid email format")

        if not self.first_name or len(self.first_name) > 100:
            errors.append(f"Line {self.line_number}: firstName must be 1-100 characters")

        if not self.last_name or len(self.last_name) > 100:
            errors.append(f"Line {self.line_number}: lastName must be 1-100 characters")

        if len(self.password) < 8:
            errors.append(f"Line {self.line_number}: password must be at least 8 characters")

        if self.tenant_id <= 0:
            errors.append(f"Line {self.line_number}: tenantId must be positive integer")

        if self.status not in ('ENABLED', 'DISABLED'):
            errors.append(f"Line {self.line_number}: status must be ENABLED or DISABLED")

        return errors

    def to_api_payload(self) -> dict:
        """Convert to UnityAuth API request payload."""
        return {
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'password': self.password,
            'tenantId': self.tenant_id,
            'roles': self.role_ids
        }
```

---

## API Entity Mappings

The CLI consumes UnityAuth API entities. These map directly to API responses:

### User Entity (from API)

**API Endpoint**: `GET /api/users`, `POST /api/users`

**Response Schema**:
```json
{
  "id": integer,
  "email": string,
  "firstName": string,
  "lastName": string,
  "roles": [integer]  // Role IDs
}
```

**CLI Table Output**:
```
ID  Email                    First Name  Last Name  Roles
1   user@example.com         John        Doe        1, 2, 3
```

---

### Tenant Entity (from API)

**API Endpoint**: `GET /api/tenants`

**Response Schema**:
```json
{
  "id": integer,
  "name": string
}
```

**CLI Table Output**:
```
ID  Name
1   Example Corp
2   Acme Inc
```

---

### Role Entity (from API)

**API Endpoint**: `GET /api/roles`

**Response Schema**:
```json
{
  "id": integer,
  "name": string,
  "description": string
}
```

**CLI Table Output**:
```
ID  Name                Description
1   Unity Administrator System-wide admin access
2   Tenant Administrator Tenant-level admin access
```

---

### Permission Response (from API)

**API Endpoint**: `POST /api/principal/permissions`

**Request**:
```json
{
  "tenantId": integer,
  "serviceId": integer
}
```

**Response**:
```json
{
  "permissions": [string],  // e.g., ["AUTH_SERVICE_VIEW-SYSTEM", "AUTH_SERVICE_EDIT-TENANT"]
  "errorMessage": string    // Present on error
}
```

**CLI Output**:
```
Permissions for user@example.com in Tenant 1, Service 1:
- AUTH_SERVICE_VIEW-SYSTEM
- AUTH_SERVICE_EDIT-TENANT
```

---

## State Transitions

### Authentication State Machine

```
┌─────────────┐
│ Logged Out  │
│ (no token)  │
└──────┬──────┘
       │
       │ unityauth login
       │ (success)
       ▼
┌─────────────┐      Token expires         ┌──────────────┐
│ Logged In   │ ─────────────────────────> │ Expired      │
│ (has token) │                             │ (401 error)  │
└──────┬──────┘                             └──────┬───────┘
       │                                           │
       │ unityauth logout                          │
       │                                           │
       │ <─────────────────────────────────────────┘
       │ Re-authentication prompt
       ▼
┌─────────────┐
│ Logged Out  │
└─────────────┘
```

**States**:
1. **Logged Out**: No token in keyring; must run `unityauth login`
2. **Logged In**: Valid token in keyring; automatically included in API requests
3. **Expired**: Token exists but API returns 401; prompt for re-login

**Transitions**:
- Logged Out → Logged In: `unityauth login` with valid credentials
- Logged In → Logged Out: `unityauth logout` (explicit) or token deleted manually
- Logged In → Expired: Token TTL exceeded (detected on 401 response)
- Expired → Logged Out: User declines re-authentication prompt
- Expired → Logged In: User re-authenticates via prompt

---

### Batch Operation State Machine

```
┌──────────┐
│ Validate │ ─────────> [File not found] ──> ERROR
│ CSV File │
└────┬─────┘
     │
     │ [File valid]
     ▼
┌──────────────┐
│ Validate All │ ───> [Missing columns] ──> ERROR
│ Rows Schema  │ ───> [Invalid data] ────> ERROR
└──────┬───────┘
       │
       │ [All rows valid]
       ▼
┌──────────────┐
│ Process Rows │
│ Sequentially │
└──────┬───────┘
       │
       ├─> [Row N success] ──> Continue
       │
       ├─> [Row N failure + continue_on_error] ──> Log error, Continue
       │
       └─> [Row N failure + !continue_on_error] ──> STOP, Report failures

       After all rows:
       ▼
┌──────────────┐
│ Report       │
│ Summary      │ ───> Exit 0 if all success
└──────────────┘ ───> Exit 1 if any failures
```

---

## Error Handling

### Error Categories and Exit Codes

| Category | Exit Code | Examples | User Action |
|----------|-----------|----------|-------------|
| Success | 0 | Operation completed | None |
| General Error | 1 | Validation, network, API error | Check error message |
| Authentication | 2 | Invalid credentials, expired token | Run `unityauth login` |
| Permission | 3 | Insufficient privileges | Contact administrator |
| Configuration | 4 | Missing API URL, invalid config | Run `unityauth config show` |

### Error Response Mapping

| HTTP Status | CLI Exception | Exit Code | User Message |
|-------------|---------------|-----------|--------------|
| 400 | ValidationError | 1 | "Invalid request: {details}" |
| 401 | AuthenticationError | 2 | "Authentication required. Run: unityauth login" |
| 403 | PermissionError | 3 | "Permission denied: {permission} required" |
| 404 | NotFoundError | 1 | "Resource not found: {resource}" |
| 422 | ValidationError | 1 | "Validation failed: {field}: {message}" |
| 429 | RateLimitError | 1 | "Rate limit exceeded. Retry after {seconds}s" |
| 500+ | ServerError | 1 | "Server error. Contact administrator if persists" |

---

## Output Formats

### Table Format (Default)

**Features**:
- Human-readable ASCII/Unicode tables
- Auto-sized columns based on content
- Headers enabled by default
- Truncation for very long values (with ellipsis)
- Color-coded (errors red, success green)

**Example**:
```
╭──────┬────────────────────┬────────────┬───────────┬────────╮
│   ID │ Email              │ First Name │ Last Name │ Roles  │
├──────┼────────────────────┼────────────┼───────────┼────────┤
│    1 │ admin@example.com  │ Admin      │ User      │ 1, 2   │
│    2 │ tenant@example.com │ Tenant     │ Admin     │ 2      │
╰──────┴────────────────────┴────────────┴───────────┴────────╯
```

---

### JSON Format

**Features**:
- Machine-readable structured data
- Pretty-printed with 2-space indentation
- Valid JSON array or object
- Suitable for piping to `jq`

**Example**:
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

---

### CSV Format

**Features**:
- RFC 4180 compliant
- Header row included
- Quoted fields for special characters
- UTF-8 encoding
- Suitable for Excel or data processing

**Example**:
```csv
id,email,firstName,lastName,roles
1,admin@example.com,Admin,User,"1,2"
2,tenant@example.com,Tenant,Admin,2
```

---

## Validation Rules

### Input Validation

| Field | Rules | Error Message |
|-------|-------|---------------|
| email | Valid email format (regex) | "Invalid email format" |
| password | Min 8 characters | "Password must be at least 8 characters" |
| firstName | Not blank, max 100 chars | "First name must be 1-100 characters" |
| lastName | Not blank, max 100 chars | "Last name must be 1-100 characters" |
| tenantId | Positive integer | "Tenant ID must be a positive integer" |
| roleIds | Comma/pipe-separated integers | "Role IDs must be integers" |
| api_url | Valid HTTPS URL | "API URL must be a valid HTTPS URL" |

### Configuration Validation

| Setting | Rules | Default |
|---------|-------|---------|
| api_url | Required, HTTPS | None (must be set) |
| timeout | 5-300 seconds | 30 |
| batch.max_size | 1-10000 | 1000 |
| default_format | table, json, or csv | table |

---

## Performance Considerations

### Batch Processing

- **Sequential Processing**: Rows processed one at a time (no parallelism)
- **Expected Throughput**: 100+ records/minute (per SC-002)
- **Rate Limiting**: Optional `--delay` parameter adds milliseconds between requests
- **Memory Usage**: Stream CSV parsing (no full file in memory)

### Caching Strategy

**No Caching**: CLI is stateless by design
- Tenant/role lists fetched fresh on each `list` command
- No local database or cache files
- Simplifies implementation and avoids stale data

### Network Optimization

- **Session Reuse**: Single `requests.Session` per command execution (connection pooling)
- **Timeout**: Configurable (default 30s)
- **Retries**: None (fail-fast per design decision)

---

## Next Steps

1. Implement entities in Python using `@dataclass` decorators
2. Create validation functions for each entity
3. Implement output formatters (table, JSON, CSV)
4. See [contracts/commands.yml](contracts/commands.yml) for detailed command specifications
5. See [quickstart.md](quickstart.md) for end-user documentation
