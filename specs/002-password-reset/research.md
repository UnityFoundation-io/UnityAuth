# Research: Password Reset Workflow

**Feature**: 002-password-reset
**Date**: 2025-12-31
**Status**: Complete

## Executive Summary

This document captures research findings and technical decisions for implementing the password reset feature in UnityAuth. All major unknowns have been resolved with decisions that align with existing codebase patterns and the project constitution.

---

## Research Areas

### 1. Email Service Integration

**Question**: How to send emails from Micronaut?

**Decision**: Use `micronaut-email` with configurable transport (SMTP or SendGrid)

**Rationale**:
- Official Micronaut library with first-class support
- Supports multiple transports: SMTP, SendGrid, SES, Postmark
- Configuration-driven transport selection per environment
- Template support for HTML emails

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Jakarta Mail directly | More boilerplate, no environment abstraction |
| SendGrid SDK only | Locks to single provider, less flexible |
| Custom HTTP client | Reinventing wheel, maintenance burden |

**Implementation Notes**:
- Add `micronaut-email-sendgrid` or `micronaut-email-javamail` dependency
- Configure in `application-{env}.yml` per environment
- Create `EmailService` abstraction for testability
- Use templated emails with token placeholder

---

### 2. JWT Session Invalidation

**Question**: How to invalidate JWT sessions after password reset? (JWTs are stateless)

**Decision**: Add `tokenVersion` field to User entity; increment on password reset

**Rationale**:
- Minimal database schema change (single column)
- JWT validation can check version matches
- Immediate invalidation without token blacklist table
- Follows existing Micronaut Security patterns

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Token blacklist table | Requires checking every request, grows unbounded |
| Short token expiry only | Doesn't provide immediate invalidation |
| Redis session store | Adds infrastructure complexity |

**Implementation Notes**:
- Add `token_version INT DEFAULT 1` to user table via Flyway migration
- Include `token_version` claim in JWT at login
- Validate `token_version` matches current user record
- Increment `token_version` on password reset

---

### 3. Rate Limiting

**Question**: How to rate-limit password reset requests?

**Decision**: Use `micronaut-ratelimiter` with Bucket4j for in-memory rate limiting

**Rationale**:
- Official Micronaut extension
- Per-key (email) limiting without database writes
- Configurable limits via application.yml
- Works with existing interceptor patterns

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Database counter table | Adds write load, cleanup complexity |
| Custom AOP interceptor | Reinvents existing solution |
| Redis rate limiter | Overkill for single-instance, adds dependency |

**Implementation Notes**:
- Add `micronaut-ratelimiter` dependency
- Configure: 3 requests per email per hour
- Apply `@RateLimiter` annotation to request endpoint
- Return 429 Too Many Requests on limit exceeded

---

### 4. Secure Token Generation

**Question**: How to generate cryptographically secure reset tokens?

**Decision**: Use `java.security.SecureRandom` with URL-safe Base64 encoding

**Rationale**:
- Standard Java library, no additional dependencies
- Cryptographically secure random number generator
- URL-safe encoding for embedding in links
- 32-byte tokens provide 256 bits of entropy

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| UUID.randomUUID() | Only 122 bits of randomness |
| JWT as reset token | Overcomplicated, not needed for short-lived single-use |
| External library | Unnecessary dependency |

**Implementation Notes**:
```java
SecureRandom random = new SecureRandom();
byte[] bytes = new byte[32];
random.nextBytes(bytes);
String token = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
```

---

### 5. Token Cleanup Scheduling

**Question**: How to clean up expired tokens after 90 days?

**Decision**: Use Micronaut `@Scheduled` annotation with daily cleanup job

**Rationale**:
- Built into Micronaut, no additional dependencies
- Cron-style scheduling supported
- Runs in application process (no external scheduler)
- Simple DELETE query for expired tokens

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Check at request time only | Leaves stale data in database |
| External cron job | Separate deployment, less portable |
| Database triggers | Platform-specific, harder to test |

**Implementation Notes**:
- Create `TokenCleanupService` with `@Scheduled(cron = "0 0 3 * * ?")`
- Run daily at 3 AM
- Delete tokens older than 90 days
- Log cleanup count for audit

---

### 6. Unauthenticated Endpoint Access

**Question**: How to expose password reset endpoints without authentication?

**Decision**: Use `isAnonymous()` in security intercept-url-map (existing pattern)

**Rationale**:
- Follows existing pattern used for `/api/login`
- Centralized security configuration
- No changes to controller annotations needed
- Clear separation of public vs protected endpoints

**Implementation Notes**:
```yaml
security:
  intercept-url-map:
    - pattern: /api/password-reset/**
      http-method: POST
      access:
        - isAnonymous()
```

---

### 7. Password Validation

**Question**: How to validate password complexity requirements?

**Decision**: Create custom `@ValidPassword` annotation with Jakarta Validation

**Rationale**:
- Follows existing validation annotation pattern (@NullOrNotBlank)
- Reusable across endpoints
- Clear error messages per violation
- Testable validation logic

**Requirements** (from spec FR-005):
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Implementation Notes**:
- Create `ValidPasswordValidator` implementing `ConstraintValidator`
- Return specific error message for each failed rule
- Apply to `newPassword` field in reset request DTO

---

### 8. Email Templates

**Question**: What should password reset emails contain?

**Decision**: HTML email with plain text fallback

**Reset Request Email**:
- Subject: "Reset your UnityAuth password"
- Body: Greeting, reset link, expiration warning, security note
- Link format: `{BASE_URL}/reset-password?token={TOKEN}`

**Reset Confirmation Email**:
- Subject: "Your UnityAuth password was changed"
- Body: Confirmation, timestamp, security instructions if not initiated

**Implementation Notes**:
- Store templates in `src/main/resources/email-templates/`
- Use Micronaut email templating or simple string replacement
- Configure `BASE_URL` per environment

---

## Dependencies to Add

| Dependency | Purpose |
|------------|---------|
| `micronaut-email-javamail` | Email sending via SMTP |
| `micronaut-ratelimiter` | Request rate limiting |
| `micronaut-management` | @Scheduled support (if not present) |

## Database Changes

New migration: `V3__add_password_reset_tables.sql`

1. `password_reset_token` table
2. `password_reset_audit_log` table
3. `token_version` column on `user` table

## Configuration Changes

New configuration sections:
- `email.*` - SMTP/transport configuration
- `password-reset.*` - Token expiration, rate limits
- Security intercept-url-map additions

---

## Conclusion

All technical unknowns have been resolved with decisions that:
- Follow existing UnityAuth patterns (DTOs, services, repositories)
- Comply with constitution principles (security, migrations, testing)
- Minimize new dependencies (prefer Micronaut ecosystem)
- Support multi-environment deployment (configuration-driven)

**Next Step**: Proceed to Phase 1 (data-model.md, contracts/)
