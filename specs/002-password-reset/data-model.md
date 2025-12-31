# Data Model: Password Reset Workflow

**Feature**: 002-password-reset
**Date**: 2025-12-31
**Status**: Complete

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              User (existing)                             │
├─────────────────────────────────────────────────────────────────────────┤
│ id: BIGINT (PK)                                                         │
│ email: VARCHAR(255) NOT NULL UNIQUE                                     │
│ password: VARCHAR(255)                                                  │
│ first_name: VARCHAR(255)                                                │
│ last_name: VARCHAR(255)                                                 │
│ status: ENUM('ENABLED', 'DISABLED')                                     │
│ token_version: INT DEFAULT 1  ← NEW FIELD                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1
                                    │
                                    ▼ *
┌─────────────────────────────────────────────────────────────────────────┐
│                         PasswordResetToken (new)                         │
├─────────────────────────────────────────────────────────────────────────┤
│ id: BIGINT (PK, AUTO_INCREMENT)                                         │
│ user_id: BIGINT (FK → user.id) NOT NULL                                 │
│ token: VARCHAR(64) NOT NULL UNIQUE                                      │
│ created_at: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP                │
│ expires_at: TIMESTAMP NOT NULL                                          │
│ used: BOOLEAN NOT NULL DEFAULT FALSE                                    │
│ used_at: TIMESTAMP NULL                                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1
                                    │
                                    ▼ *
┌─────────────────────────────────────────────────────────────────────────┐
│                      PasswordResetAuditLog (new)                         │
├─────────────────────────────────────────────────────────────────────────┤
│ id: BIGINT (PK, AUTO_INCREMENT)                                         │
│ user_id: BIGINT (FK → user.id) NULL                                     │
│ email: VARCHAR(255) NOT NULL                                            │
│ event_type: ENUM('REQUEST', 'VERIFY', 'RESET_SUCCESS',                  │
│                  'RESET_FAILED', 'TOKEN_EXPIRED', 'TOKEN_INVALID')      │
│ ip_address: VARCHAR(45) NULL                                            │
│ user_agent: VARCHAR(512) NULL                                           │
│ created_at: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP                │
│ details: TEXT NULL                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### User (Modified)

**Changes**: Add `token_version` field for JWT session invalidation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| token_version | INT | NOT NULL DEFAULT 1 | Incremented on password reset to invalidate existing sessions |

**Behavior**:
- Increment `token_version` when password is successfully reset (FR-016)
- Include `token_version` in JWT claims at login
- Validate JWT `token_version` matches user's current version

---

### PasswordResetToken (New)

**Purpose**: Stores single-use tokens for password reset requests.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGINT | PK, AUTO_INCREMENT | Unique identifier |
| user_id | BIGINT | FK(user.id), NOT NULL | Reference to user requesting reset |
| token | VARCHAR(64) | NOT NULL, UNIQUE, INDEX | Cryptographically secure token (URL-safe Base64) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | When token was generated |
| expires_at | TIMESTAMP | NOT NULL | Expiration time (created_at + 30 minutes) |
| used | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether token has been consumed |
| used_at | TIMESTAMP | NULL | When token was used (for audit) |

**Validation Rules**:
- Token is valid if: `used = FALSE` AND `expires_at > NOW()`
- Token length: 43 characters (32 bytes URL-safe Base64)
- One active token per user (previous tokens invalidated on new request)

**State Transitions**:
```
[CREATED] ──(30 min)──> [EXPIRED]
    │
    │ (user submits valid password)
    ▼
 [USED]
```

**Indexes**:
- `idx_password_reset_token_token` on `token` (unique, for lookups)
- `idx_password_reset_token_user_id` on `user_id` (for invalidation queries)
- `idx_password_reset_token_expires_at` on `expires_at` (for cleanup queries)

---

### PasswordResetAuditLog (New)

**Purpose**: Immutable audit trail of all password reset activities.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | BIGINT | PK, AUTO_INCREMENT | Unique identifier |
| user_id | BIGINT | FK(user.id), NULL | User reference (NULL if email not found) |
| email | VARCHAR(255) | NOT NULL | Email address used in request |
| event_type | ENUM | NOT NULL | Type of event (see below) |
| ip_address | VARCHAR(45) | NULL | Client IP (supports IPv6) |
| user_agent | VARCHAR(512) | NULL | Client user agent string |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | When event occurred |
| details | TEXT | NULL | Additional context (JSON format) |

**Event Types**:
| Value | Description |
|-------|-------------|
| REQUEST | Password reset requested |
| VERIFY | Token validation attempted |
| RESET_SUCCESS | Password successfully changed |
| RESET_FAILED | Password change failed (validation error) |
| TOKEN_EXPIRED | Token was expired when used |
| TOKEN_INVALID | Token was invalid or tampered |

**Retention**: Records retained for 90 days per FR-019.

**Indexes**:
- `idx_audit_user_id` on `user_id` (for user history queries)
- `idx_audit_email` on `email` (for security investigations)
- `idx_audit_created_at` on `created_at` (for retention cleanup)

---

## Database Migration

**File**: `V3__add_password_reset_tables.sql`

```sql
-- Add token_version to user table for session invalidation
ALTER TABLE user ADD COLUMN token_version INT NOT NULL DEFAULT 1;

-- Password reset tokens table
CREATE TABLE password_reset_token (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP NULL,
    CONSTRAINT fk_reset_token_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT uk_reset_token UNIQUE (token),
    INDEX idx_reset_token_user_id (user_id),
    INDEX idx_reset_token_expires_at (expires_at)
);

-- Password reset audit log table
CREATE TABLE password_reset_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NULL,
    email VARCHAR(255) NOT NULL,
    event_type ENUM('REQUEST', 'VERIFY', 'RESET_SUCCESS', 'RESET_FAILED', 'TOKEN_EXPIRED', 'TOKEN_INVALID') NOT NULL,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(512) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details TEXT NULL,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL,
    INDEX idx_audit_user_id (user_id),
    INDEX idx_audit_email (email),
    INDEX idx_audit_created_at (created_at)
);
```

---

## Java Entity Mappings

### PasswordResetToken Entity

```java
@MappedEntity("password_reset_token")
public class PasswordResetToken {
    @Id
    @GeneratedValue
    private Long id;

    @Relation(value = Relation.Kind.MANY_TO_ONE)
    private User user;

    @NotNull
    private String token;

    @NotNull
    private Instant createdAt;

    @NotNull
    private Instant expiresAt;

    @NotNull
    private Boolean used = false;

    private Instant usedAt;

    // Convenience methods
    public boolean isValid() {
        return !used && Instant.now().isBefore(expiresAt);
    }

    public boolean isExpired() {
        return Instant.now().isAfter(expiresAt);
    }
}
```

### PasswordResetAuditLog Entity

```java
@MappedEntity("password_reset_audit_log")
public class PasswordResetAuditLog {
    @Id
    @GeneratedValue
    private Long id;

    private Long userId;

    @NotNull
    private String email;

    @NotNull
    @Enumerated(EnumType.STRING)
    private EventType eventType;

    private String ipAddress;

    private String userAgent;

    @NotNull
    private Instant createdAt;

    private String details;

    public enum EventType {
        REQUEST, VERIFY, RESET_SUCCESS, RESET_FAILED, TOKEN_EXPIRED, TOKEN_INVALID
    }
}
```

---

## Repository Interfaces

### PasswordResetTokenRepository

```java
@JdbcRepository(dialect = Dialect.MYSQL)
public interface PasswordResetTokenRepository extends CrudRepository<PasswordResetToken, Long> {

    Optional<PasswordResetToken> findByToken(String token);

    List<PasswordResetToken> findByUserIdAndUsedFalse(Long userId);

    @Query("UPDATE password_reset_token SET used = true WHERE user_id = :userId AND used = false")
    void invalidateAllForUser(Long userId);

    @Query("DELETE FROM password_reset_token WHERE expires_at < :cutoff OR (used = true AND used_at < :cutoff)")
    int deleteExpiredTokens(Instant cutoff);
}
```

### PasswordResetAuditLogRepository

```java
@JdbcRepository(dialect = Dialect.MYSQL)
public interface PasswordResetAuditLogRepository extends CrudRepository<PasswordResetAuditLog, Long> {

    List<PasswordResetAuditLog> findByUserIdOrderByCreatedAtDesc(Long userId);

    List<PasswordResetAuditLog> findByEmailOrderByCreatedAtDesc(String email);

    @Query("DELETE FROM password_reset_audit_log WHERE created_at < :cutoff")
    int deleteOlderThan(Instant cutoff);
}
```

---

## Data Validation Rules

| Entity | Field | Rule | Error Message |
|--------|-------|------|---------------|
| User | token_version | >= 1 | N/A (internal) |
| PasswordResetToken | token | 43 chars, URL-safe Base64 | Invalid token format |
| PasswordResetToken | expires_at | > created_at | N/A (computed) |
| PasswordResetAuditLog | email | Valid email format | Invalid email |
| PasswordResetAuditLog | ip_address | Valid IPv4/IPv6 | N/A (nullable) |

---

## Data Lifecycle

### Token Lifecycle

1. **Creation**: Token created with 30-minute expiration
2. **Invalidation**: Previous tokens for user marked invalid on new request
3. **Usage**: Token marked used with timestamp on successful reset
4. **Cleanup**: Expired/used tokens deleted after 90 days

### Audit Log Lifecycle

1. **Creation**: Log entry created for each event
2. **Retention**: Entries retained for 90 days
3. **Cleanup**: Daily scheduled job deletes entries older than 90 days
