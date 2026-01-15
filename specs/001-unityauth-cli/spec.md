# Feature Specification: UnityAuth Command Line Interface

**Feature Branch**: `001-unityauth-cli`
**Created**: 2025-12-26
**Status**: Draft
**Input**: User description: "You are an expert command line interface designer and developer. You are to create a coherent and simple command line interface for leveraging the capabilities provided by UnityAuth. You are to examine all of the APIs for UnityAuth and identify how to enable command line access to these services."

## Clarifications

### Session 2025-12-26

- Q: How should authentication tokens be securely stored? → A: Tokens must be encrypted using OS-native secure storage (macOS Keychain, Windows Credential Manager, Linux Secret Service API)
- Q: What data format should batch operations accept? → A: CSV with header row required; mandatory columns: email, firstName, lastName, password, tenantId; optional: roleIds (pipe-separated), status
- Q: How should CLI behave when API rate limits are encountered? → A: Immediately fail with error message instructing user to retry manually after specified wait time
- Q: How should CLI handle network failures during operations? → A: Fail immediately with network error; user must manually retry the entire operation
- Q: How should CLI handle API version compatibility? → A: CLI version is locked to specific API version; fail with clear error if API version mismatch detected

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Administrator Authentication (Priority: P1)

A system administrator needs to authenticate with UnityAuth from the command line to perform administrative tasks without using a web browser. They want to securely store their session credentials to avoid re-authenticating for every command.

**Why this priority**: Authentication is the foundation for all other operations. Without the ability to authenticate, no other CLI features can function. This is the critical first step that enables all subsequent administrative workflows.

**Independent Test**: Can be fully tested by running the login command, verifying token storage, and confirming that subsequent commands use the stored token. Delivers immediate value by enabling scriptable authentication.

**Acceptance Scenarios**:

1. **Given** UnityAuth CLI is installed and configured with the API endpoint, **When** administrator runs login command with valid credentials, **Then** CLI authenticates successfully and stores the session token securely
2. **Given** administrator is authenticated, **When** administrator runs a command that requires authentication, **Then** CLI automatically uses the stored token without prompting for credentials again
3. **Given** administrator is authenticated, **When** administrator runs logout command, **Then** CLI removes stored credentials and subsequent commands require re-authentication
4. **Given** administrator provides invalid credentials, **When** administrator attempts to login, **Then** CLI displays clear error message and does not store invalid credentials
5. **Given** stored token has expired, **When** administrator runs an authenticated command, **Then** CLI detects expiration and prompts for re-authentication

---

### User Story 2 - User Account Management (Priority: P2)

A tenant administrator needs to create and manage user accounts from the command line, including setting initial passwords and assigning roles. They want to perform bulk operations efficiently and integrate user provisioning into automated workflows.

**Why this priority**: User management is a core administrative task that benefits significantly from CLI automation. After authentication (P1), this is the most frequently needed operation for day-to-day administration.

**Independent Test**: Can be tested by creating users with various role combinations, updating user profiles, and listing users for a tenant. Delivers value by enabling user provisioning scripts and bulk operations.

**Acceptance Scenarios**:

1. **Given** administrator is authenticated with appropriate permissions, **When** administrator runs create user command with email, name, password, tenant, and roles, **Then** new user account is created with specified attributes
2. **Given** user account exists, **When** administrator runs update roles command with new role assignments for a tenant, **Then** user's roles are updated for that tenant only
3. **Given** administrator is authenticated, **When** administrator runs list users command for a tenant, **Then** CLI displays all users associated with that tenant including their roles
4. **Given** administrator lacks required permissions, **When** administrator attempts to create or modify users, **Then** CLI displays permission denied error with explanation
5. **Given** administrator provides invalid data (duplicate email, non-existent role, etc.), **When** administrator attempts user operation, **Then** CLI displays validation error with specific details

---

### User Story 3 - Tenant and Role Discovery (Priority: P3)

An administrator needs to view available tenants and roles to understand the system structure before performing administrative operations. They want to quickly reference what tenants they can manage and what roles they can assign.

**Why this priority**: Discovery operations provide necessary context for other administrative tasks but are less critical than core CRUD operations. Administrators can often work with known tenant/role IDs, making this supportive rather than essential.

**Independent Test**: Can be tested by listing all accessible tenants and all available roles. Delivers value by providing system visibility and reference information for other commands.

**Acceptance Scenarios**:

1. **Given** administrator is authenticated, **When** administrator runs list tenants command, **Then** CLI displays all tenants the administrator can access based on their permissions
2. **Given** administrator is authenticated, **When** administrator runs list roles command, **Then** CLI displays all available roles in the system with descriptions
3. **Given** administrator is authenticated, **When** administrator runs view tenant users command with a tenant ID, **Then** CLI displays all users associated with that specific tenant
4. **Given** Unity administrator is authenticated, **When** Unity administrator lists tenants, **Then** CLI displays all tenants in the system
5. **Given** tenant administrator is authenticated, **When** tenant administrator lists tenants, **Then** CLI displays only tenants they administer

---

### User Story 4 - Permission Verification (Priority: P4)

A service integration developer needs to check what permissions a user has for a specific tenant and service, and verify if a user has specific required permissions. This helps debug authorization issues and validate role configurations.

**Why this priority**: Permission checking is primarily a debugging and verification tool rather than a day-to-day administrative operation. While useful, it's less frequently needed than user management or discovery operations.

**Independent Test**: Can be tested by querying user permissions for various tenant/service combinations and checking specific permission strings. Delivers value for troubleshooting and validation scenarios.

**Acceptance Scenarios**:

1. **Given** administrator is authenticated, **When** administrator runs get permissions command for a user, tenant, and service, **Then** CLI displays all permissions the user has in that context
2. **Given** administrator is authenticated, **When** administrator runs check permission command with specific permission strings, **Then** CLI indicates whether user has those permissions
3. **Given** user is inactive or tenant is inactive, **When** administrator checks permissions, **Then** CLI displays error indicating the status issue
4. **Given** service is not available to the tenant, **When** administrator checks permissions for that service, **Then** CLI displays error indicating service unavailability

---

### User Story 5 - Batch Operations and Scripting (Priority: P5)

A system administrator needs to perform bulk user provisioning or updates as part of automated deployment scripts. They want to process lists of users from CSV files or other data sources without manual intervention.

**Why this priority**: Batch operations build on core functionality and represent an optimization rather than essential capability. Administrators can achieve the same results by scripting individual commands, making this a convenience feature.

**Independent Test**: Can be tested by providing a data file with multiple user records and verifying all operations complete successfully. Delivers value for large-scale provisioning and migrations.

**Acceptance Scenarios**:

1. **Given** administrator has a data file with user records, **When** administrator runs batch create users command, **Then** CLI processes all records and reports success/failure for each
2. **Given** batch operation encounters an error, **When** processing continues, **Then** CLI completes remaining operations and provides summary of failures
3. **Given** administrator wants to preview changes, **When** administrator runs batch command with dry-run flag, **Then** CLI shows what would happen without making actual changes
4. **Given** administrator provides malformed data file, **When** administrator attempts batch operation, **Then** CLI validates file format and reports specific errors before processing

---

### Edge Cases

- What happens when network connection to UnityAuth API is lost during operation? → CLI fails immediately with clear network error message; no automatic retry; user must manually retry operation
- How does CLI handle API version mismatches or unsupported endpoints? → CLI version locked to specific API version; fails with clear error if version mismatch detected
- What happens when token expires in the middle of a long-running batch operation?
- How does CLI behave when terminal output is redirected to a file or pipe?
- What happens when user attempts to assign Unity Administrator role as a tenant administrator?
- How does CLI handle concurrent modifications (two administrators updating same user simultaneously)?
- What happens when required configuration (API endpoint) is missing or invalid?
- How does CLI handle special characters in passwords or names during user creation?
- What happens when user attempts operations requiring permissions they don't have?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST authenticate users against UnityAuth API using email and password credentials
- **FR-002**: CLI MUST securely store authentication tokens using OS-native secure storage (macOS Keychain, Windows Credential Manager, Linux Secret Service API) after successful login for subsequent command execution
- **FR-003**: CLI MUST automatically detect expired tokens and prompt for re-authentication when necessary
- **FR-004**: CLI MUST allow users to create new user accounts with email, first name, last name, password, tenant assignment, and role assignments
- **FR-005**: CLI MUST allow administrators to update user role assignments for specific tenants
- **FR-006**: CLI MUST allow users to update their own profile information (first name, last name, password)
- **FR-007**: CLI MUST display lists of accessible tenants based on authenticated user's permissions
- **FR-008**: CLI MUST display all users associated with a specific tenant
- **FR-009**: CLI MUST display all available roles in the system
- **FR-010**: CLI MUST allow querying all permissions for a user in a specific tenant and service context
- **FR-011**: CLI MUST allow checking if a user has specific named permissions
- **FR-012**: CLI MUST enforce permission-based access control for administrative operations
- **FR-013**: CLI MUST display clear error messages when operations fail due to permissions, validation, or network issues
- **FR-014**: CLI MUST support batch operations for creating multiple users from CSV files with mandatory header row and columns (email, firstName, lastName, password, tenantId) and optional columns (roleIds as pipe-separated values, status)
- **FR-015**: CLI MUST provide configurable output formats (human-readable tables, JSON, CSV) for query results
- **FR-016**: CLI MUST accept API endpoint configuration to support different UnityAuth environments (development, staging, production)
- **FR-017**: CLI MUST validate user input before sending requests to the API
- **FR-018**: CLI MUST handle both interactive mode (prompting for sensitive data) and non-interactive mode (accepting all parameters as arguments) for automation
- **FR-019**: CLI MUST support dry-run mode for batch operations to preview changes without executing them
- **FR-020**: CLI MUST provide verbose output mode for debugging and troubleshooting
- **FR-021**: CLI MUST allow users to view information about their current authentication session (token info)
- **FR-022**: CLI MUST support logout operation that removes stored credentials
- **FR-023**: CLI MUST display clear error messages with retry-after time when API rate limits are encountered
- **FR-024**: CLI MUST verify API version compatibility on first request and fail with clear error if version mismatch is detected

### Key Entities

- **User**: Represents a person who can authenticate and perform actions; has email, first name, last name, password, and status; associated with tenants through role assignments
- **Tenant**: Represents an organization or customer using UnityAuth; has name and status; contains users and provides context for role assignments
- **Role**: Represents a collection of permissions; has name and description; can be assigned to users within tenant context; examples include Unity Administrator, Tenant Administrator, service-specific roles
- **Permission**: Represents a specific capability or access right; has scope level (SYSTEM, TENANT, SUBTENANT); format like "AUTH_SERVICE_VIEW-SYSTEM" or "AUTH_SERVICE_EDIT-TENANT"
- **Service**: Represents an external application authenticating against UnityAuth; tenants must have access to services for permission checks to succeed
- **Session Token**: JWT bearer token issued upon successful authentication; contains user identity and permissions; has expiration time; used for all authenticated API requests

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators can authenticate and perform basic user management operations (create user, list users) within 30 seconds of first using the CLI
- **SC-002**: Batch user creation processes at least 100 user records per minute including validation and error reporting
- **SC-003**: CLI commands complete with clear success or failure indication within 5 seconds for single-record operations under normal network conditions
- **SC-004**: CLI reduces time required for common user provisioning tasks by 60% compared to web UI workflow
- **SC-005**: Error messages include sufficient context that administrators can resolve 80% of issues without consulting documentation
- **SC-006**: CLI enables fully automated user provisioning workflows that can run unattended in deployment scripts
- **SC-007**: Configuration setup (API endpoint, initial authentication) takes less than 2 minutes for new users
- **SC-008**: CLI output is readable in standard terminal widths (80+ characters) without horizontal scrolling for common operations

## Assumptions

- UnityAuth API endpoints are accessible over HTTPS with valid SSL certificates
- Administrators using the CLI have basic familiarity with command line interfaces
- The JWT tokens issued by UnityAuth API have reasonable expiration times (hours, not minutes)
- API responses follow consistent JSON structure as documented in current UnityAuth implementation
- Network latency between CLI and API is generally under 200ms for typical deployments
- Administrators have already obtained their account credentials through existing provisioning processes
- Configuration files can be stored in user's home directory with appropriate file system permissions
- Target platforms support standard terminal capabilities (ANSI colors, cursor control)
- Batch CSV files use UTF-8 encoding, comma delimiters, and quote-escaped values for fields containing special characters

## Dependencies

- **External**: UnityAuth backend API must be deployed and accessible at a known endpoint
- **External**: API version must match CLI's supported version (version-locked compatibility)
- **External**: API must support all documented endpoints (authentication, user management, tenant management, role management, permission checking)
- **External**: Network connectivity between CLI execution environment and UnityAuth API
- **External**: Valid user accounts with appropriate permissions must exist for CLI users to authenticate

## Constraints

- CLI must not store passwords in plain text; only JWT tokens should be persisted
- Token storage must use OS-native encrypted secure storage (macOS Keychain, Windows Credential Manager, Linux Secret Service API); fallback to encrypted file storage only if OS service unavailable
- When API rate limits are encountered, CLI must fail immediately with clear error message indicating wait time before retry
- All API communications must use HTTPS; plain HTTP should be rejected
- CLI must not implement its own authentication logic; all authentication must go through UnityAuth API
- Batch operations must have reasonable limits to prevent API overload (configurable maximum)
- CLI must be compatible with standard terminal environments (bash, zsh, PowerShell)

## Out of Scope

- Graphical user interface or web-based interface for the CLI
- Direct database access or manipulation (all operations through API only)
- Offline operation queue or automatic network retry logic (CLI requires active network connection)
- Service management operations (creating/modifying services in UnityAuth)
- Tenant creation or modification (read-only access to tenant list)
- Role or permission definition/modification (read-only access to role list)
- Token refresh or rotation logic (relies on UnityAuth API token expiration)
- Multi-factor authentication support beyond what UnityAuth API provides
- Internationalization or localization of CLI output
- Shell completion scripts or command shortcuts (future enhancement)
- Migration tools for importing users from external systems
- Audit logging of CLI operations (relies on UnityAuth API audit logs)
