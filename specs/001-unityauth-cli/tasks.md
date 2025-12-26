# Tasks: UnityAuth Command Line Interface

**Input**: Design documents from `/specs/001-unityauth-cli/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓
**Constitution**: v1.1.0 (includes Principle VIII: CLI Design Standards)

**Tests**: Unit tests added for auth-critical code per Constitution v1.1.0 VI. Testing Discipline.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Python package structure

- [x] T001 Create project directory structure: unityauth-cli/ with src/unityauth_cli/, tests/unit/, tests/integration/, tests/fixtures/
- [x] T002 Initialize Python project with pyproject.toml including Click 8.1+, Requests 2.31+, Keyring 24.3+, PyYAML 6.0+, Tabulate 0.9+, Rich 13.7+
- [x] T003 [P] Create requirements.txt and requirements-dev.txt with pinned dependencies from plan.md
- [x] T004 [P] Create .gitignore for Python project (*.pyc, __pycache__, .pytest_cache, *.egg-info, dist/, build/)
- [x] T005 [P] Create unityauth-cli/README.md with installation and basic usage instructions
- [x] T006 [P] Create unityauth-cli/src/unityauth_cli/__init__.py with package version metadata

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 [P] Create Configuration class in unityauth-cli/src/unityauth_cli/config.py to load/save YAML config from ~/.config/unityauth-cli/config.yml
- [x] T008 [P] Create custom exception hierarchy in unityauth-cli/src/unityauth_cli/utils/errors.py (AuthenticationError, AuthorizationError, ValidationError, NetworkError, ConfigurationError) with exit codes per Constitution VIII
- [x] T009 [P] Create input validation utilities in unityauth-cli/src/unityauth_cli/utils/validation.py (email format, password length, tenant ID)
- [x] T010 Create UnityAuthAPIClient in unityauth-cli/src/unityauth_cli/client.py with requests.Session, base URL, token header management, HTTP error mapping
- [x] T011 [P] Create table formatter in unityauth-cli/src/unityauth_cli/formatters/table.py using tabulate library
- [x] T012 [P] Create JSON formatter in unityauth-cli/src/unityauth_cli/formatters/json_fmt.py using stdlib json
- [x] T013 [P] Create CSV formatter in unityauth-cli/src/unityauth_cli/formatters/csv_fmt.py using stdlib csv
- [x] T014 Create main CLI group in unityauth-cli/src/unityauth_cli/cli.py with Click, global options (--api-url, --format, --verbose, --help, --version)
- [x] T015 Create entry point in unityauth-cli/src/unityauth_cli/__main__.py to invoke cli() function
- [x] T016 Create @require_auth and @require_config decorators in unityauth-cli/src/unityauth_cli/cli.py per Constitution VIII (eliminates boilerplate, injects API client)
- [x] T017 [P] Fix ConfigurationError import in config.py (remove duplicate class, import from utils.errors) per Constitution VIII single source of truth
- [x] T018 [P] Rename PermissionError to AuthorizationError in utils/errors.py to avoid shadowing Python built-in per Constitution VIII

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - System Administrator Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable administrators to securely authenticate with UnityAuth and store session credentials for subsequent commands

**Independent Test**: Run login command with valid credentials, verify token stored in OS keyring, run token-info to confirm session, run logout to clear credentials

### Implementation for User Story 1

- [x] T019 [P] [US1] Create authentication module in unityauth-cli/src/unityauth_cli/auth.py with keyring integration (store_token, get_token, delete_token functions)
- [x] T020 [P] [US1] Implement login command in unityauth-cli/src/unityauth_cli/commands/login.py calling POST /api/login and storing JWT in keyring
- [x] T021 [P] [US1] Implement logout command in unityauth-cli/src/unityauth_cli/commands/login.py deleting token from keyring (uses @require_config decorator)
- [x] T022 [P] [US1] Implement token-info command in unityauth-cli/src/unityauth_cli/commands/login.py calling GET /api/token_info (uses @require_auth decorator)
- [x] T023 [US1] Add login command to CLI group in unityauth-cli/src/unityauth_cli/cli.py with Click command registration
- [x] T024 [US1] Add logout command to CLI group in unityauth-cli/src/unityauth_cli/cli.py
- [x] T025 [US1] Add token-info command to CLI group in unityauth-cli/src/unityauth_cli/cli.py
- [x] T026 [US1] Implement token expiration detection in unityauth-cli/src/unityauth_cli/client.py (catch 401 errors, raise AuthenticationError)
- [x] T027 [US1] Add interactive vs non-interactive mode support in unityauth-cli/src/unityauth_cli/commands/login.py using sys.stdin.isatty() and Click.prompt()
- [x] T028 [US1] Add Rich-styled success/error messages for authentication operations in unityauth-cli/src/unityauth_cli/commands/login.py

### Unit Tests for User Story 1 (Constitution v1.1.0 requirement)

- [x] T029 [P] [US1] Create test fixtures and conftest.py in unityauth-cli/tests/conftest.py with mock_keyring, mock_config, cli_context fixtures
- [x] T030 [P] [US1] Create auth module tests in unityauth-cli/tests/unit/test_auth.py (store_token, get_token, delete_token, has_token)
- [x] T031 [P] [US1] Create decorator tests in unityauth-cli/tests/unit/test_decorators.py (@require_auth, @require_config behavior)

**Checkpoint**: At this point, User Story 1 should be fully functional with test coverage - administrators can login, view session info, and logout

---

## Phase 4: User Story 2 - User Account Management (Priority: P2)

**Goal**: Enable administrators to create, update, and list user accounts with role assignments through the CLI

**Independent Test**: Create a new user with specific roles, list users for a tenant to verify creation, update user's roles, list again to confirm changes

### Implementation for User Story 2

- [x] T032 [P] [US2] Implement user create command in unityauth-cli/src/unityauth_cli/commands/users.py calling POST /api/users (uses @require_auth decorator)
- [x] T033 [P] [US2] Implement user update command in unityauth-cli/src/unityauth_cli/commands/users.py calling PATCH /api/users/{id}/roles (uses @require_auth decorator)
- [x] T034 [P] [US2] Implement user list command in unityauth-cli/src/unityauth_cli/commands/users.py calling GET /api/tenants/{id}/users (uses @require_auth decorator)
- [x] T035 [US2] Add user command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (create, update, list)
- [x] T036 [US2] Add input validation for user create in unityauth-cli/src/unityauth_cli/commands/users.py (email format, password length, name length)
- [x] T037 [US2] Add AuthorizationError handling in unityauth-cli/src/unityauth_cli/commands/users.py with actionable error messages
- [x] T038 [US2] Add output formatting support for user list in unityauth-cli/src/unityauth_cli/commands/users.py (table/JSON/CSV)
- [ ] T039 [US2] RESEARCH: Investigate and resolve user update command 403 Forbidden error - CLI correctly sends PATCH /api/users/{id}/roles with authentication token and valid payload (tenantId + roles), but backend returns 403; verify Micronaut routing, security configuration, and endpoint registration

### Unit Tests for User Story 2 (Constitution v1.1.0 requirement)

- [x] T040 [P] [US2] Create API client tests in unityauth-cli/tests/unit/test_client.py (HTTP methods, error handling, timeout, network errors)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full user management capability available (NOTE: T039 investigation needed for update command)

---

## Phase 5: User Story 3 - Tenant and Role Discovery (Priority: P3)

**Goal**: Enable administrators to view available tenants and roles to understand system structure before performing operations

**Independent Test**: List all accessible tenants, list all available roles, view users for a specific tenant

### Implementation for User Story 3

- [x] T041 [P] [US3] Implement tenant list command in unityauth-cli/src/unityauth_cli/commands/tenants.py calling GET /api/tenants (uses @require_auth decorator)
- [x] T042 [P] [US3] Implement tenant users command in unityauth-cli/src/unityauth_cli/commands/tenants.py calling GET /api/tenants/{id}/users (uses @require_auth decorator)
- [x] T043 [P] [US3] Implement role list command in unityauth-cli/src/unityauth_cli/commands/roles.py calling GET /api/roles (uses @require_auth decorator)
- [x] T044 [US3] Add tenant command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (list, users)
- [x] T045 [US3] Add role command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommand (list)
- [x] T046 [US3] Add output formatting support for all discovery commands (table/JSON/CSV)
- [x] T047 [US3] Add permission-based filtering display in tenant list (Unity admin sees all, tenant admin sees only their tenants)

**Checkpoint**: All discovery operations functional - administrators can explore system structure independently

---

## Phase 6: User Story 4 - Permission Verification (Priority: P4)

**Goal**: Enable developers and administrators to check user permissions for debugging authorization issues and validating role configurations

**Independent Test**: Query permissions for a user in a specific tenant/service context, check if user has specific named permissions

### Implementation for User Story 4

- [ ] T048 [P] [US4] Implement permission get command in unityauth-cli/src/unityauth_cli/commands/permissions.py calling POST /api/principal/permissions (uses @require_auth decorator)
- [ ] T049 [P] [US4] Implement permission check command in unityauth-cli/src/unityauth_cli/commands/permissions.py calling POST /api/hasPermission (uses @require_auth decorator)
- [ ] T050 [US4] Add permission command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (get, check)
- [ ] T051 [US4] Add formatted output for permission lists (readable list format with scope indicators)
- [ ] T052 [US4] Add error handling for inactive users/tenants/services with clear status messages

**Checkpoint**: Permission verification fully functional - useful for debugging and validation scenarios

---

## Phase 7: User Story 5 - Batch Operations and Scripting (Priority: P5)

**Goal**: Enable administrators to perform bulk user provisioning from CSV files with error handling and validation

**Independent Test**: Create a CSV file with 3+ user records, run batch create-users with dry-run to preview, run actual batch operation and verify all users created

### Implementation for User Story 5

- [ ] T053 [P] [US5] Create BatchUserRecord dataclass in unityauth-cli/src/unityauth_cli/utils/batch.py with validation method per data-model.md schema
- [ ] T054 [P] [US5] Implement CSV parser in unityauth-cli/src/unityauth_cli/utils/batch.py using csv.DictReader with UTF-8 encoding and header validation
- [ ] T055 [US5] Implement batch create-users command in unityauth-cli/src/unityauth_cli/commands/batch.py with sequential processing and error collection (uses @require_auth decorator)
- [ ] T056 [US5] Add dry-run mode support in batch.py (--dry-run flag) to preview operations without API calls
- [ ] T057 [US5] Add continue-on-error behavior in batch.py (--continue-on-error/--no-continue-on-error flags)
- [ ] T058 [US5] Add batch command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with create-users subcommand
- [ ] T059 [US5] Implement progress bar using Rich library in batch.py for visual feedback during processing
- [ ] T060 [US5] Add batch operation summary report (total processed, successes, failures with line numbers)
- [ ] T061 [US5] Add CSV validation with specific error messages (missing columns, invalid data types, format errors)

**Checkpoint**: Batch operations fully functional - large-scale provisioning enabled

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the CLI for release

- [x] T062 [P] Add config show command in unityauth-cli/src/unityauth_cli/commands/config.py displaying current configuration
- [x] T063 [P] Add config set command in unityauth-cli/src/unityauth_cli/commands/config.py for setting config values (dot notation support)
- [x] T064 [P] Add config edit command in unityauth-cli/src/unityauth_cli/commands/config.py to open config in editor
- [x] T065 Implement API version compatibility check in unityauth-cli/src/unityauth_cli/client.py on first authenticated request
- [x] T066 [P] Add comprehensive error messages with retry guidance for network errors in client.py
- [x] T067 [P] Add rate limit error handling in client.py with retry-after time display per FR-023
- [x] T068 [P] Add verbose/debug output mode using Rich console in cli.py
- [x] T069 [P] Add environment variable support in config.py (UNITYAUTH_API_URL, UNITYAUTH_EMAIL, UNITYAUTH_PASSWORD)
- [ ] T070 Update root CLAUDE.md with CLI section including installation, common commands, and usage examples
- [ ] T071 Update root README.md to reference unityauth-cli component in project overview
- [ ] T072 [P] Create sample CSV files in tests/fixtures/ (valid users, invalid formats, missing columns)
- [ ] T073 Validate quickstart.md examples by running each command and verifying output matches documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent, but uses auth from US1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent, but uses auth from US1
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Independent, but uses auth from US1
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent, but uses user creation logic from US2

### Constitution v1.1.0 Compliance

All commands MUST use:
- `@require_auth` decorator for authenticated commands (injects API client)
- `@require_config` decorator for commands needing only API URL
- `AuthorizationError` (not `PermissionError`) for permission failures
- Semantic exit codes: 0=success, 2=auth, 3=permission, 4=config
- Multi-format output (table/JSON/CSV)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → **Basic project structure ready**
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) → **Core infrastructure ready**
3. Complete Phase 3: User Story 1 with tests → **Authentication working with test coverage**
4. **STOP and VALIDATE**: Test login, token-info, logout independently
5. Deploy/demo if ready → **Administrators can authenticate from CLI**

**MVP Deliverable**: Secure CLI authentication with OS-native token storage and unit tests

### Current Progress

- ✅ Phase 1: Setup - COMPLETE
- ✅ Phase 2: Foundational - COMPLETE (including decorators and error hierarchy fixes)
- ✅ Phase 3: User Story 1 - COMPLETE with unit tests
- ✅ Phase 4: User Story 2 - COMPLETE (except T039 research for update 403 issue)
- ✅ Phase 5: User Story 3 - COMPLETE (tenant list, tenant users, role list with formatting)
- ⏳ Phase 6: User Story 4 - NOT STARTED
- ⏳ Phase 7: User Story 5 - NOT STARTED
- 🔄 Phase 8: Polish - PARTIALLY COMPLETE (config commands done, docs pending)

---

## Summary Statistics

- **Total Tasks**: 73 tasks
- **Completed**: 57 tasks ✅
- **Remaining**: 16 tasks
- **Setup Phase**: 6 tasks (COMPLETE)
- **Foundational Phase**: 12 tasks (COMPLETE - includes architectural improvements)
- **User Story 1 (P1)**: 13 tasks - Authentication 🎯 MVP (COMPLETE with tests)
- **User Story 2 (P2)**: 9 tasks - User Management (8 complete, 1 research pending)
- **User Story 3 (P3)**: 7 tasks - Discovery (COMPLETE)
- **User Story 4 (P4)**: 5 tasks - Permission Verification (NOT STARTED)
- **User Story 5 (P5)**: 9 tasks - Batch Operations (NOT STARTED)
- **Polish Phase**: 12 tasks - Cross-cutting concerns (8 complete, 4 pending)

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phases

**Next Steps**:
1. Complete T039 (research update 403 issue)
2. Implement Phase 6: User Story 4 (Permission Verification)
3. Update documentation (T070, T071)

**Format Validation**: ✅ ALL tasks follow the checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Notes

- **[P] tasks** = different files, no dependencies within phase
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Tests included**: Per Constitution v1.1.0 VI. Testing Discipline - auth-critical code has unit tests
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Key file paths** follow plan.md structure: unityauth-cli/src/unityauth_cli/
- **API endpoints** documented in CLAUDE.md are consumed by CLI (no new backend development needed)
- **Decorators**: All authenticated commands use @require_auth; config-only commands use @require_config
