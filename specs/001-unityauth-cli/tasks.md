# Tasks: UnityAuth Command Line Interface

**Input**: Design documents from `/specs/001-unityauth-cli/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Tests**: Tests are NOT explicitly requested in the specification. This task list focuses on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Python package structure

- [ ] T001 Create project directory structure: unityauth-cli/ with src/unityauth_cli/, tests/unit/, tests/integration/, tests/fixtures/
- [ ] T002 Initialize Python project with pyproject.toml including Click 8.1+, Requests 2.31+, Keyring 24.3+, PyYAML 6.0+, Tabulate 0.9+, Rich 13.7+
- [ ] T003 [P] Create requirements.txt and requirements-dev.txt with pinned dependencies from plan.md
- [ ] T004 [P] Create .gitignore for Python project (*.pyc, __pycache__, .pytest_cache, *.egg-info, dist/, build/)
- [ ] T005 [P] Create unityauth-cli/README.md with installation and basic usage instructions
- [ ] T006 [P] Create unityauth-cli/src/unityauth_cli/__init__.py with package version metadata

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Create Configuration class in unityauth-cli/src/unityauth_cli/config.py to load/save YAML config from ~/.config/unityauth-cli/config.yml
- [ ] T008 [P] Create custom exception hierarchy in unityauth-cli/src/unityauth_cli/utils/errors.py (AuthenticationError, PermissionError, ValidationError, NetworkError, ConfigurationError) with exit codes
- [ ] T009 [P] Create input validation utilities in unityauth-cli/src/unityauth_cli/utils/validation.py (email format, password length, tenant ID)
- [ ] T010 Create UnityAuthAPIClient in unityauth-cli/src/unityauth_cli/client.py with requests.Session, base URL, token header management, HTTP error mapping
- [ ] T011 [P] Create table formatter in unityauth-cli/src/unityauth_cli/formatters/table.py using tabulate library
- [ ] T012 [P] Create JSON formatter in unityauth-cli/src/unityauth_cli/formatters/json_fmt.py using stdlib json
- [ ] T013 [P] Create CSV formatter in unityauth-cli/src/unityauth_cli/formatters/csv_fmt.py using stdlib csv
- [ ] T014 Create main CLI group in unityauth-cli/src/unityauth_cli/cli.py with Click, global options (--api-url, --format, --verbose, --help, --version)
- [ ] T015 Create entry point in unityauth-cli/src/unityauth_cli/__main__.py to invoke cli() function

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - System Administrator Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable administrators to securely authenticate with UnityAuth and store session credentials for subsequent commands

**Independent Test**: Run login command with valid credentials, verify token stored in OS keyring, run token-info to confirm session, run logout to clear credentials

### Implementation for User Story 1

- [ ] T016 [P] [US1] Create authentication module in unityauth-cli/src/unityauth_cli/auth.py with keyring integration (store_token, get_token, delete_token functions)
- [ ] T017 [P] [US1] Implement login command in unityauth-cli/src/unityauth_cli/commands/login.py calling POST /api/login and storing JWT in keyring
- [ ] T018 [P] [US1] Implement logout command in unityauth-cli/src/unityauth_cli/commands/login.py deleting token from keyring
- [ ] T019 [P] [US1] Implement token-info command in unityauth-cli/src/unityauth_cli/commands/login.py calling GET /api/token_info and displaying session details
- [ ] T020 [US1] Add login command to CLI group in unityauth-cli/src/unityauth_cli/cli.py with Click command registration
- [ ] T021 [US1] Add logout command to CLI group in unityauth-cli/src/unityauth_cli/cli.py
- [ ] T022 [US1] Add token-info command to CLI group in unityauth-cli/src/unityauth_cli/cli.py
- [ ] T023 [US1] Implement token expiration detection in unityauth-cli/src/unityauth_cli/client.py (catch 401 errors, prompt for re-authentication)
- [ ] T024 [US1] Add interactive vs non-interactive mode support in unityauth-cli/src/unityauth_cli/commands/login.py using sys.stdin.isatty() and Click.prompt()
- [ ] T025 [US1] Add Rich-styled success/error messages for authentication operations in unityauth-cli/src/unityauth_cli/commands/login.py

**Checkpoint**: At this point, User Story 1 should be fully functional - administrators can login, view session info, and logout

---

## Phase 4: User Story 2 - User Account Management (Priority: P2)

**Goal**: Enable administrators to create, update, and list user accounts with role assignments through the CLI

**Independent Test**: Create a new user with specific roles, list users for a tenant to verify creation, update user's roles, list again to confirm changes

### Implementation for User Story 2

- [ ] T026 [P] [US2] Implement user create command in unityauth-cli/src/unityauth_cli/commands/users.py calling POST /api/users with validation
- [ ] T027 [P] [US2] Implement user update command in unityauth-cli/src/unityauth_cli/commands/users.py calling PUT /api/users/{id} for role updates
- [ ] T028 [P] [US2] Implement user list command in unityauth-cli/src/unityauth_cli/commands/users.py calling GET /api/users with tenant filter
- [ ] T029 [US2] Add user command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (create, update, list)
- [ ] T030 [US2] Add input validation for user create in unityauth-cli/src/unityauth_cli/commands/users.py (email format, password length, name length per data-model.md)
- [ ] T031 [US2] Add permission denied error handling in unityauth-cli/src/unityauth_cli/commands/users.py with actionable error messages
- [ ] T032 [US2] Add output formatting support for user list in unityauth-cli/src/unityauth_cli/commands/users.py (table/JSON/CSV)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full user management capability available

---

## Phase 5: User Story 3 - Tenant and Role Discovery (Priority: P3)

**Goal**: Enable administrators to view available tenants and roles to understand system structure before performing operations

**Independent Test**: List all accessible tenants, list all available roles, view users for a specific tenant

### Implementation for User Story 3

- [ ] T033 [P] [US3] Implement tenant list command in unityauth-cli/src/unityauth_cli/commands/tenants.py calling GET /api/tenants
- [ ] T034 [P] [US3] Implement tenant users command in unityauth-cli/src/unityauth_cli/commands/tenants.py calling GET /api/tenants/{id}/users
- [ ] T035 [P] [US3] Implement role list command in unityauth-cli/src/unityauth_cli/commands/roles.py calling GET /api/roles
- [ ] T036 [US3] Add tenant command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (list, users)
- [ ] T037 [US3] Add role command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommand (list)
- [ ] T038 [US3] Add output formatting support for all discovery commands in unityauth-cli/src/unityauth_cli/commands/tenants.py and roles.py (table/JSON/CSV)
- [ ] T039 [US3] Add permission-based filtering display in tenant list (Unity admin sees all, tenant admin sees only their tenants)

**Checkpoint**: All discovery operations functional - administrators can explore system structure independently

---

## Phase 6: User Story 4 - Permission Verification (Priority: P4)

**Goal**: Enable developers and administrators to check user permissions for debugging authorization issues and validating role configurations

**Independent Test**: Query permissions for a user in a specific tenant/service context, check if user has specific named permissions

### Implementation for User Story 4

- [ ] T040 [P] [US4] Implement permission get command in unityauth-cli/src/unityauth_cli/commands/permissions.py calling POST /api/principal/permissions
- [ ] T041 [P] [US4] Implement permission check command in unityauth-cli/src/unityauth_cli/commands/permissions.py calling POST /api/hasPermission
- [ ] T042 [US4] Add permission command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with subcommands (get, check)
- [ ] T043 [US4] Add formatted output for permission lists in unityauth-cli/src/unityauth_cli/commands/permissions.py (readable list format)
- [ ] T044 [US4] Add error handling for inactive users/tenants/services in unityauth-cli/src/unityauth_cli/commands/permissions.py with clear status messages

**Checkpoint**: Permission verification fully functional - useful for debugging and validation scenarios

---

## Phase 7: User Story 5 - Batch Operations and Scripting (Priority: P5)

**Goal**: Enable administrators to perform bulk user provisioning from CSV files with error handling and validation

**Independent Test**: Create a CSV file with 3+ user records, run batch create-users with dry-run to preview, run actual batch operation and verify all users created

### Implementation for User Story 5

- [ ] T045 [P] [US5] Create BatchUserRecord dataclass in unityauth-cli/src/unityauth_cli/utils/batch.py with validation method per data-model.md schema
- [ ] T046 [P] [US5] Implement CSV parser in unityauth-cli/src/unityauth_cli/utils/batch.py using csv.DictReader with UTF-8 encoding and header validation
- [ ] T047 [US5] Implement batch create-users command in unityauth-cli/src/unityauth_cli/commands/batch.py with sequential processing and error collection
- [ ] T048 [US5] Add dry-run mode support in unityauth-cli/src/unityauth_cli/commands/batch.py (--dry-run flag) to preview operations without API calls
- [ ] T049 [US5] Add continue-on-error behavior in unityauth-cli/src/unityauth_cli/commands/batch.py (--continue-on-error/--no-continue-on-error flags)
- [ ] T050 [US5] Add batch command group to CLI in unityauth-cli/src/unityauth_cli/cli.py with create-users subcommand
- [ ] T051 [US5] Implement progress bar using Rich library in unityauth-cli/src/unityauth_cli/commands/batch.py for visual feedback during processing
- [ ] T052 [US5] Add batch operation summary report in unityauth-cli/src/unityauth_cli/commands/batch.py (total processed, successes, failures with line numbers)
- [ ] T053 [US5] Add CSV validation with specific error messages in unityauth-cli/src/unityauth_cli/commands/batch.py (missing columns, invalid data types, format errors)

**Checkpoint**: Batch operations fully functional - large-scale provisioning enabled

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the CLI for release

- [ ] T054 [P] Add config command group in unityauth-cli/src/unityauth_cli/commands/config.py with subcommands (show, set, edit)
- [ ] T055 [P] Implement API version compatibility check in unityauth-cli/src/unityauth_cli/client.py on first authenticated request per research.md decision
- [ ] T056 [P] Add comprehensive error messages with retry guidance for network errors in unityauth-cli/src/unityauth_cli/client.py
- [ ] T057 [P] Add rate limit error handling in unityauth-cli/src/unityauth_cli/client.py with retry-after time display per FR-023
- [ ] T058 [P] Add verbose/debug output mode using Rich console in unityauth-cli/src/unityauth_cli/cli.py
- [ ] T059 [P] Add environment variable support in unityauth-cli/src/unityauth_cli/config.py (UNITYAUTH_API_URL, UNITYAUTH_EMAIL, UNITYAUTH_PASSWORD)
- [ ] T060 Update root CLAUDE.md with CLI section including installation, common commands, and usage examples
- [ ] T061 Update root README.md to reference unityauth-cli component in project overview
- [ ] T062 [P] Create sample CSV files in tests/fixtures/ (valid users, invalid formats, missing columns)
- [ ] T063 Validate quickstart.md examples by running each command and verifying output matches documentation

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

### Within Each User Story

- Models/utilities before commands
- Commands before CLI registration
- Core implementation before advanced features (error handling, formatting)
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T007, T008, T009 can run in parallel (different modules)
- T011, T012, T013 can run in parallel (different formatters)

**Phase 3 (User Story 1)**:
- T016, T017, T018, T019 can run in parallel (different command implementations)

**Phase 4 (User Story 2)**:
- T026, T027, T028 can run in parallel (different command implementations)

**Phase 5 (User Story 3)**:
- T033, T034, T035 can run in parallel (different command implementations)

**Phase 6 (User Story 4)**:
- T040, T041 can run in parallel (different command implementations)

**Phase 7 (User Story 5)**:
- T045, T046 can run in parallel (different utilities)

**Phase 8 (Polish)**:
- T054, T055, T056, T057, T058, T059, T062 can all run in parallel (different concerns)

**Cross-Story Parallelism**:
- Once Foundational (Phase 2) completes, User Stories 1, 2, 3, 4, 5 can all start in parallel if team has capacity
- Each story is independently implementable and testable

---

## Parallel Example: Foundational Phase

```bash
# Launch foundational infrastructure in parallel:
Task T007: "Create Configuration class in unityauth-cli/src/unityauth_cli/config.py"
Task T008: "Create custom exception hierarchy in unityauth-cli/src/unityauth_cli/utils/errors.py"
Task T009: "Create input validation utilities in unityauth-cli/src/unityauth_cli/utils/validation.py"
```

---

## Parallel Example: User Story 1

```bash
# Launch all authentication commands in parallel:
Task T016: "Create authentication module in unityauth-cli/src/unityauth_cli/auth.py"
Task T017: "Implement login command in unityauth-cli/src/unityauth_cli/commands/login.py"
Task T018: "Implement logout command in unityauth-cli/src/unityauth_cli/commands/login.py"
Task T019: "Implement token-info command in unityauth-cli/src/unityauth_cli/commands/login.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all user management commands in parallel:
Task T026: "Implement user create command in unityauth-cli/src/unityauth_cli/commands/users.py"
Task T027: "Implement user update command in unityauth-cli/src/unityauth_cli/commands/users.py"
Task T028: "Implement user list command in unityauth-cli/src/unityauth_cli/commands/users.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → **Basic project structure ready**
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories) → **Core infrastructure ready**
3. Complete Phase 3: User Story 1 → **Authentication working**
4. **STOP and VALIDATE**: Test login, token-info, logout independently
5. Deploy/demo if ready → **Administrators can authenticate from CLI**

**MVP Deliverable**: Secure CLI authentication with OS-native token storage

### Incremental Delivery

1. Complete Setup + Foundational → **Foundation ready**
2. Add User Story 1 → Test independently → **MVP: Authentication works!**
3. Add User Story 2 → Test independently → **User management works!**
4. Add User Story 3 → Test independently → **Discovery works!**
5. Add User Story 4 → Test independently → **Permission verification works!**
6. Add User Story 5 → Test independently → **Batch operations work!**
7. Add Polish → Final release-ready CLI

**Each story adds value without breaking previous stories**

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (blocking work)
2. Once Foundational is done, split work:
   - **Developer A**: User Story 1 (P1) - Authentication
   - **Developer B**: User Story 2 (P2) - User Management
   - **Developer C**: User Story 3 (P3) - Discovery
3. Stories complete and integrate independently
4. Continue with P4, P5 as capacity allows

---

## Summary Statistics

- **Total Tasks**: 63 tasks
- **Setup Phase**: 6 tasks
- **Foundational Phase**: 9 tasks (CRITICAL - blocks all user stories)
- **User Story 1 (P1)**: 10 tasks - Authentication 🎯 MVP
- **User Story 2 (P2)**: 7 tasks - User Management
- **User Story 3 (P3)**: 7 tasks - Discovery
- **User Story 4 (P4)**: 5 tasks - Permission Verification
- **User Story 5 (P5)**: 9 tasks - Batch Operations
- **Polish Phase**: 10 tasks - Cross-cutting concerns

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phases

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = **25 tasks**

**Format Validation**: ✅ ALL tasks follow the checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Notes

- **[P] tasks** = different files, no dependencies within phase
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **Tests not included**: Spec does not explicitly request test implementation; focus is on CLI functionality
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Key file paths** follow plan.md structure: unityauth-cli/src/unityauth_cli/
- **API endpoints** documented in CLAUDE.md are consumed by CLI (no new backend development needed)
