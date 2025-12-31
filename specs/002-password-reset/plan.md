# Implementation Plan: Password Reset Workflow

**Branch**: `002-password-reset` | **Date**: 2025-12-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-password-reset/spec.md`

## Summary

Implement a secure password reset workflow for UnityAuth that allows users to request a password reset via email and complete the reset using a time-limited, single-use token. The implementation adds three new API endpoints, two database tables, email integration, rate limiting, and session invalidation on password change.

**Key Technical Decisions** (from [research.md](research.md)):
- Email: Micronaut Email with configurable SMTP/SendGrid transport
- Session invalidation: `token_version` field in User entity (increment to invalidate JWTs)
- Rate limiting: Bucket4j via micronaut-ratelimiter (3 requests/email/hour)
- Token generation: SecureRandom with URL-safe Base64 encoding (43 chars)
- Cleanup: @Scheduled daily job for 90-day retention

## Technical Context

**Language/Version**: Java 21 (backend)
**Primary Dependencies**: Micronaut Framework, micronaut-email-javamail, micronaut-ratelimiter
**Storage**: MySQL 8.0 with Flyway migrations
**Testing**: Micronaut Test + TestContainers
**Target Platform**: Docker containers (dev/prod), JVM runtime (local development)
**Project Type**: Backend API extension (no frontend/CLI changes in this feature)
**Performance Goals**: Sub-200ms API response times, 100+ concurrent reset requests
**Constraints**: OWASP Top 10 compliance, email enumeration prevention, rate limiting

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Reference**: `.specify/memory/constitution.md` (v1.1.0)

Verify compliance with UnityAuth core principles:

- [x] **API-First Design**: Three new REST endpoints defined in OpenAPI spec before implementation
- [x] **Security by Default**: Email enumeration prevention, rate limiting, BCrypt for passwords, secure token generation, audit logging
- [x] **Multi-Tenancy Isolation**: N/A - Password reset operates at user level, not tenant-scoped
- [x] **Database Schema Versioning**: New tables via Flyway migration V3__add_password_reset_tables.sql
- [x] **Environment-Aware Configuration**: Email/rate-limit config via application-{env}.yml
- [x] **Testing Discipline**: Integration tests planned for all endpoints and security scenarios
- [x] **Service Independence**: Backend-only changes, frontend consumes existing API patterns
- [ ] **CLI Design Standards**: N/A - No CLI changes in this feature

**Violations Requiring Justification**: None - all principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/002-password-reset/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical research and decisions
├── data-model.md        # Entity definitions and migrations
├── quickstart.md        # Implementation guide
├── contracts/           # API contracts
│   ├── password-reset-api.yaml  # OpenAPI specification
│   └── dto-contracts.md         # Java DTO definitions
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code Changes

```text
UnityAuth/src/main/java/io/unityfoundation/auth/
├── PasswordResetController.java      # NEW: REST endpoints
├── PasswordResetService.java         # NEW: Business logic
├── EmailService.java                 # NEW: Email sending
├── TokenCleanupService.java          # NEW: Scheduled cleanup
├── ValidPassword.java                # NEW: Validation annotation
├── ValidPasswordValidator.java       # NEW: Validation logic
├── entities/
│   ├── User.java                     # MODIFIED: Add tokenVersion
│   ├── PasswordResetToken.java       # NEW: Entity
│   ├── PasswordResetTokenRepository.java  # NEW: Repository
│   ├── PasswordResetAuditLog.java    # NEW: Entity
│   └── PasswordResetAuditLogRepository.java  # NEW: Repository
└── exceptions/
    ├── TokenExpiredException.java    # NEW
    ├── TokenInvalidException.java    # NEW
    ├── TokenAlreadyUsedException.java # NEW
    └── SamePasswordException.java    # NEW

UnityAuth/src/main/resources/
├── application.yml                   # MODIFIED: Add security config
├── application-local.yml             # MODIFIED: Add email config
├── application-docker.yml            # MODIFIED: Add email config
├── db/migration/
│   └── V3__add_password_reset_tables.sql  # NEW: Migration
└── email-templates/                  # NEW: Directory
    ├── password-reset.html           # NEW: Reset email
    └── password-changed.html         # NEW: Confirmation email

UnityAuth/src/test/java/io/unityfoundation/auth/
└── PasswordResetTest.java            # NEW: Integration tests
```

## Complexity Tracking

No constitution violations. Complexity is appropriate for the security-critical nature of password reset functionality.

## Generated Artifacts

| Artifact | Path | Status |
|----------|------|--------|
| Research | [research.md](research.md) | Complete |
| Data Model | [data-model.md](data-model.md) | Complete |
| OpenAPI Spec | [contracts/password-reset-api.yaml](contracts/password-reset-api.yaml) | Complete |
| DTO Contracts | [contracts/dto-contracts.md](contracts/dto-contracts.md) | Complete |
| Quickstart | [quickstart.md](quickstart.md) | Complete |

## Next Steps

Run `/speckit.tasks` to generate the implementation task breakdown.
