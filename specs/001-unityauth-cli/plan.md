# Implementation Plan: UnityAuth Command Line Interface

**Branch**: `001-unityauth-cli` | **Date**: 2025-12-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-unityauth-cli/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a command-line interface tool that provides administrative access to UnityAuth services. The CLI will enable system and tenant administrators to perform user provisioning, role management, permission verification, and batch operations through a simple, fail-fast command structure. The tool consumes existing UnityAuth REST API endpoints and follows a secure-by-default philosophy with OS-native credential storage and version-locked API compatibility.

**Primary Requirement**: Enable scriptable, automated user management workflows that reduce provisioning time by 60% compared to web UI.

**Technical Approach**:
- Python 3.11+ CLI application using Click framework for command structure
- OS-native secure storage libraries (keyring) for encrypted token persistence
- Requests library with session management for API communication
- Tabulate for human-readable output, JSON/CSV export support
- Version pinning to specific UnityAuth API version with compatibility checks

## Technical Context

**Language/Version**: Python 3.11+ (CLI application)
**Primary Dependencies**:
- Click 8.x (command-line interface framework)
- Requests 2.x (HTTP client for API calls)
- Keyring 24.x (OS-native secure credential storage)
- Tabulate 0.9.x (table formatting for output)
- PyYAML 6.x (configuration file parsing)
- Rich 13.x (terminal formatting and progress indicators)

**Storage**:
- Configuration: YAML file in `~/.config/unityauth-cli/config.yml`
- Credentials: OS-native secure storage via keyring library
  - macOS: Keychain
  - Windows: Windows Credential Manager
  - Linux: Secret Service API (GNOME Keyring, KWallet)

**Testing**:
- Pytest for unit tests
- Pytest-mock for mocking API responses
- Click.testing.CliRunner for integration tests
- TestContainers for end-to-end tests against real UnityAuth API

**Target Platform**:
- Cross-platform: macOS, Windows, Linux
- Python 3.11+ required
- Installable via pip (PyPI package)
- Standalone executable builds using PyInstaller (future enhancement)

**Project Type**: Command-line application (API consumer only, no backend service)

**Performance Goals**:
- Single-record operations complete within 5 seconds (includes network latency)
- Batch operations process 100+ user records per minute
- Startup time under 500ms for cached configuration

**Constraints**:
- Version-locked to specific UnityAuth API version
- No automatic retry logic (fail-fast on errors)
- No offline operation (requires active network)
- No password storage (JWT tokens only)
- Must support interactive and non-interactive modes

**Scale/Scope**:
- Administrative tool for system/tenant administrators
- Supports all 13 UnityAuth API endpoints
- Designed for batch operations up to 1000 users per file
- No persistent state beyond configuration and tokens

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Reference**: `.specify/memory/constitution.md` (v1.0.0)

Verify compliance with UnityAuth core principles:

- [x] **API-First Design**: CLI is a pure API consumer; all functionality depends on existing UnityAuth REST API endpoints
- [x] **Security by Default**: JWT token storage uses OS-native encryption; HTTPS required; no password persistence; API version checking prevents security mismatches
- [x] **Multi-Tenancy Isolation**: CLI respects tenant boundaries through API permission enforcement; no cross-tenant operations
- [x] **Database Schema Versioning**: N/A - CLI does not access database directly
- [x] **Environment-Aware Configuration**: Supports multiple API endpoints (dev/staging/prod) via configuration
- [x] **Testing Discipline**: Integration tests planned for auth flows, error handling, batch operations
- [x] **Service Independence**: CLI is completely independent, standalone tool; consumes public API only

**Violations Requiring Justification**: None. CLI is a pure API consumer and aligns fully with all constitution principles.

**Additional Compliance Notes**:
- CLI inherits security from UnityAuth API (JWT validation, permission checks, tenant isolation)
- No database migrations required (read-only API consumer)
- No new backend endpoints needed (uses existing 13 endpoints documented in CLAUDE.md)

## Project Structure

### Documentation (this feature)

```text
specs/001-unityauth-cli/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output: Python CLI best practices, OS keyring integration
├── data-model.md        # Phase 1 output: CLI command structure, configuration schema
├── quickstart.md        # Phase 1 output: Installation, first login, basic commands
├── contracts/           # Phase 1 output: Command schemas, output formats
│   ├── commands.yml     # CLI command specifications (subcommands, arguments, options)
│   └── outputs.yml      # Output format schemas (JSON, CSV, table structures)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (new component in repository root)

```text
unityauth-cli/                      # NEW: Python CLI Application
├── src/
│   └── unityauth_cli/
│       ├── __init__.py
│       ├── __main__.py             # Entry point for 'python -m unityauth_cli'
│       ├── cli.py                  # Click command group definitions
│       ├── config.py               # Configuration management
│       ├── auth.py                 # Authentication and token management
│       ├── client.py               # API client (requests wrapper)
│       ├── commands/               # Command implementations
│       │   ├── __init__.py
│       │   ├── login.py            # auth login/logout/token-info
│       │   ├── users.py            # user create/update/list
│       │   ├── tenants.py          # tenant list/users
│       │   ├── roles.py            # role list
│       │   ├── permissions.py      # permission get/check
│       │   └── batch.py            # batch create-users
│       ├── formatters/             # Output formatting
│       │   ├── __init__.py
│       │   ├── table.py            # Tabulate formatters
│       │   ├── json_fmt.py         # JSON output
│       │   └── csv_fmt.py          # CSV output
│       └── utils/                  # Utilities
│           ├── __init__.py
│           ├── validation.py       # Input validation
│           └── errors.py           # Custom exceptions
├── tests/
│   ├── unit/                       # Unit tests (pytest)
│   ├── integration/                # Integration tests (CliRunner)
│   └── fixtures/                   # Test data (sample CSV files, mock responses)
├── pyproject.toml                  # Poetry/setuptools project metadata
├── requirements.txt                # Pinned dependencies
├── requirements-dev.txt            # Development dependencies
├── README.md                       # CLI installation and usage guide
└── .gitignore

# Repository root files to update:
CLAUDE.md                           # Add CLI section with installation and usage
README.md                           # Add CLI reference to project overview
```

**Structure Decision**:
- New standalone Python package `unityauth-cli` at repository root level
- Separate from `AuthGenHash` (Java-based password hash generator)
- Uses Click for command hierarchy (main command `unityauth` with subcommands)
- Follows Python best practices: src layout, pyproject.toml, type hints
- Installable via `pip install -e .` for development or `pip install unityauth-cli` from PyPI

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No constitution violations | All principles satisfied |

## Phase 0: Research & Decisions

**Status**: COMPLETE

### Research Tasks

1. **Python CLI Framework Selection**
   - **Decision**: Click 8.x
   - **Rationale**: Industry standard for complex CLIs; excellent support for nested commands, automatic help generation, parameter validation, and testing utilities. Better than argparse (verbose, manual help), Typer (less mature), or docopt (limited validation).
   - **Alternatives Considered**: argparse (too verbose), Typer (newer, smaller ecosystem), docopt (limited flexibility)

2. **OS-Native Secure Storage Integration**
   - **Decision**: keyring library 24.x with platform-specific backends
   - **Rationale**: Cross-platform abstraction over OS credential stores. Handles macOS Keychain, Windows Credential Manager, and Linux Secret Service automatically. Mature library with 10+ years of development.
   - **Alternatives Considered**: Direct integration with platform APIs (complex, platform-specific code), plaintext config with permissions (insecure), encrypted JSON (requires password input every time)

3. **HTTP Client and Session Management**
   - **Decision**: requests library with custom Session class
   - **Rationale**: De facto standard Python HTTP library. Session support for connection pooling and default headers. Well-tested with excellent error handling.
   - **Alternatives Considered**: httpx (async not needed for CLI), urllib3 (lower-level, more complex)

4. **Configuration File Format**
   - **Decision**: YAML in `~/.config/unityauth-cli/config.yml`
   - **Rationale**: Human-readable, supports comments, more intuitive than JSON for configuration. Standard location for CLI configs on Unix-like systems; AppData on Windows.
   - **Alternatives Considered**: JSON (less readable, no comments), TOML (less familiar), INI (limited structure)

5. **Output Formatting Strategy**
   - **Decision**: Tabulate for tables, native json module, csv module
   - **Rationale**: Tabulate provides professional-looking ASCII tables with minimal code. Native modules for JSON/CSV avoid extra dependencies. Rich library for progress bars and styled output.
   - **Alternatives Considered**: PrettyTable (less actively maintained), manual formatting (reinventing wheel)

6. **CSV Batch File Parsing**
   - **Decision**: Python csv.DictReader with UTF-8 encoding
   - **Rationale**: Standard library support, handles quoted fields and special characters correctly. DictReader maps to column names from header row.
   - **Alternatives Considered**: pandas (heavyweight dependency), manual parsing (error-prone)

7. **API Version Compatibility Checking**
   - **Decision**: Store supported API version in CLI metadata; check against `/api/token_info` response or custom header
   - **Rationale**: Fail-fast on version mismatch. Token info endpoint provides authenticated context and can include version metadata.
   - **Alternatives Considered**: No checking (silent failures), manual version parameter (user error-prone)

8. **Error Handling and User Feedback**
   - **Decision**: Custom exception hierarchy; Rich for styled error messages; HTTP status code mapping to user-friendly messages
   - **Rationale**: Clear error messages required by SC-005 (80% self-service error resolution). Rich provides color-coded output for errors, warnings, success.
   - **Alternatives Considered**: Plain print statements (less visible), logging only (not user-facing)

9. **Testing Strategy**
   - **Decision**: Pytest with Click.testing.CliRunner for command tests; pytest-mock for API mocking; TestContainers for E2E
   - **Rationale**: CliRunner allows isolated testing of CLI commands without subprocess overhead. Mocking enables fast unit tests. TestContainers ensures compatibility with real API.
   - **Alternatives Considered**: Manual subprocess testing (slow, brittle), no E2E tests (insufficient confidence)

10. **Interactive vs Non-Interactive Mode**
    - **Decision**: Click.prompt() for interactive; require all parameters for non-interactive; detect TTY to auto-select
    - **Rationale**: FR-018 requires both modes. TTY detection (`sys.stdin.isatty()`) allows automatic mode selection for automation.
    - **Alternatives Considered**: Always require all params (poor UX), always prompt (breaks automation)

### Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| CLI Framework | Click | 8.1+ | Industry standard, nested commands, testing support |
| HTTP Client | Requests | 2.31+ | Proven reliability, session management, excellent docs |
| Secure Storage | Keyring | 24.3+ | Cross-platform OS credential store abstraction |
| Configuration | PyYAML | 6.0+ | Human-readable config files with comments |
| Table Output | Tabulate | 0.9+ | Professional ASCII table formatting |
| Styled Output | Rich | 13.7+ | Progress bars, colored errors, improved UX |
| CSV Parsing | Python csv | stdlib | Standard library, handles edge cases |
| Testing | Pytest | 7.4+ | Modern testing framework with fixtures |
| Test Mocking | pytest-mock | 3.12+ | Simplified mocking for API responses |
| E2E Testing | TestContainers | 3.7+ | Real UnityAuth API for integration tests |

### Key Design Decisions

1. **Command Structure**: Top-level `unityauth` command with subcommands organized by resource type:
   - `unityauth login/logout/token-info` (authentication)
   - `unityauth user create/update/list` (user management)
   - `unityauth tenant list/users` (tenant discovery)
   - `unityauth role list` (role discovery)
   - `unityauth permission get/check` (permission verification)
   - `unityauth batch create-users` (batch operations)

2. **Configuration Precedence** (highest to lowest):
   - Command-line arguments/options
   - Environment variables (UNITYAUTH_API_URL, UNITYAUTH_API_VERSION)
   - Configuration file (~/.config/unityauth-cli/config.yml)
   - Interactive prompts (if TTY detected)

3. **Error Exit Codes**:
   - 0: Success
   - 1: General error (validation, network, API error)
   - 2: Authentication error (invalid credentials, expired token)
   - 3: Permission error (insufficient privileges)
   - 4: Configuration error (missing API endpoint, invalid config)

4. **Batch Operation Behavior**:
   - Validate entire CSV before processing (fail-fast on schema errors)
   - Process records sequentially (no parallel requests to avoid rate limits)
   - Continue on individual record failures (collect errors for summary)
   - Dry-run mode outputs planned operations without API calls

5. **Token Storage Strategy**:
   - Store JWT in keyring with service name "unityauth-cli" and username as API endpoint
   - Allows multiple configurations (dev/staging/prod) with separate tokens
   - Token expiration handled by auto-retry with re-authentication prompt

## Phase 1: Design & Contracts

**Status**: COMPLETE

### Data Model

See [data-model.md](data-model.md) for complete entity and command structure documentation.

**Key Entities**:
- **Configuration**: API endpoint, default output format, timeout settings
- **Credentials**: JWT token stored in OS keyring
- **Command Context**: Current API session, authenticated user info
- **Batch Record**: CSV row mapping (email, firstName, lastName, password, tenantId, roleIds)

### API Contracts

See [contracts/](contracts/) directory for detailed command and output specifications.

**Command Schemas**: [contracts/commands.yml](contracts/commands.yml)
**Output Formats**: [contracts/outputs.yml](contracts/outputs.yml)

### Quickstart Guide

See [quickstart.md](quickstart.md) for installation instructions, first-time setup, and common usage examples.

## Implementation Phases (Post-Planning)

**Note**: The following phases are NOT executed by `/speckit.plan`. Run `/speckit.tasks` to generate actionable task breakdown.

### Phase 2: Task Generation (via /speckit.tasks)

Tasks will be generated based on prioritized user stories from spec.md:
- P1: Authentication (login, logout, token storage)
- P2: User Management (create, update, list)
- P3: Tenant/Role Discovery
- P4: Permission Verification
- P5: Batch Operations

### Phase 3: Implementation (via /speckit.implement)

Execute tasks from tasks.md with dependency ordering and independent testing.

### Phase 4: Validation

- Unit test coverage >80% for business logic
- Integration tests for all commands
- E2E test against TestContainers UnityAuth API
- Manual testing on macOS, Windows, Linux

## Dependencies

**External**:
- UnityAuth backend API deployed and accessible
- Python 3.11+ installed on target platform
- OS-native credential store available (Keychain/Credential Manager/Secret Service)

**Internal**:
- No new backend endpoints required (uses existing 13 API endpoints)
- No database migrations required
- No frontend changes required

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Keyring library fails on some Linux distros | High | Provide fallback to encrypted file storage; document keyring setup requirements |
| API version mismatch after UnityAuth upgrade | Medium | Clear error message with upgrade instructions; version check on first API call |
| CSV parsing fails on malformed files | Low | Comprehensive validation with specific error messages before processing |
| Rate limiting impacts batch operations | Low | Document expected throughput (100/min); provide --delay option to slow requests |
| Token expiration during long batch | Medium | Detect 401 responses, prompt for re-auth, resume from last successful record |

## Success Metrics

- **SC-001**: First-time user completes login and user creation in <30 seconds ✓
- **SC-002**: Batch processing achieves 100+ records/minute ✓
- **SC-003**: Single operations complete in <5 seconds ✓
- **SC-004**: 60% time reduction vs web UI (measured via user feedback)
- **SC-005**: 80% error self-resolution (tracked via support tickets)
- **SC-006**: Fully automated workflows possible (CI/CD integration)
- **SC-007**: Configuration setup <2 minutes (timed user testing)
- **SC-008**: Output readable in 80-column terminals ✓

## Next Steps

1. **Run `/speckit.tasks`** to generate dependency-ordered task list in tasks.md
2. **Review generated artifacts**:
   - [research.md](research.md) - Technology decisions and rationale
   - [data-model.md](data-model.md) - Command structure and entities
   - [contracts/](contracts/) - Command schemas and output formats
   - [quickstart.md](quickstart.md) - User-facing installation guide
3. **Begin implementation** via `/speckit.implement` or manual task execution
4. **Update CLAUDE.md** with CLI installation and usage documentation after implementation
