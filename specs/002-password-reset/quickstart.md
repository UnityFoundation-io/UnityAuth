# Quickstart: Password Reset Workflow

**Feature**: 002-password-reset
**Date**: 2025-12-31

## Prerequisites

Before implementing this feature, ensure:

1. UnityAuth backend is running (`./gradlew run` or Docker)
2. MySQL database is accessible
3. Email service credentials are available (SMTP or SendGrid)

## Implementation Order

Follow this order to ensure dependencies are met:

```
1. Database Migration (V3)
   ↓
2. Entity Classes + Repositories
   ↓
3. Custom Exceptions
   ↓
4. Password Validation Annotation
   ↓
5. Email Service
   ↓
6. Password Reset Service
   ↓
7. Rate Limiting Configuration
   ↓
8. Controller + Security Config
   ↓
9. Token Cleanup Scheduler
   ↓
10. Integration Tests
```

---

## Quick Implementation Steps

### Step 1: Add Dependencies

**build.gradle**:
```gradle
// Email support
implementation("io.micronaut.email:micronaut-email-javamail")

// Rate limiting
implementation("io.micronaut.ratelimiter:micronaut-ratelimiter")
```

### Step 2: Run Database Migration

Create `V3__add_password_reset_tables.sql` in `src/main/resources/db/migration/`

```bash
./gradlew flywayMigrate
```

### Step 3: Configure Email

**application-local.yml**:
```yaml
email:
  from:
    email: noreply@unityauth.local
    name: UnityAuth
  # For development, use MailHog or similar
  smtp:
    host: localhost
    port: 1025
```

**application-docker.yml**:
```yaml
email:
  from:
    email: ${EMAIL_FROM:noreply@unityauth.io}
    name: UnityAuth
  smtp:
    host: ${SMTP_HOST:mailhog}
    port: ${SMTP_PORT:1025}
```

### Step 4: Configure Rate Limiting

**application.yml**:
```yaml
ratelimiter:
  password-reset:
    capacity: 3
    refill-tokens: 3
    refill-period: 1h
```

### Step 5: Configure Security

**application.yml** (add to existing security section):
```yaml
micronaut:
  security:
    intercept-url-map:
      # Existing entries...
      - pattern: /api/password-reset/**
        http-method: POST
        access:
          - isAnonymous()
```

### Step 6: Environment Variables

Add to `setenv.sh` or Docker environment:

```bash
# Email configuration
export SMTP_HOST=localhost
export SMTP_PORT=1025
export EMAIL_FROM=noreply@unityauth.io

# Password reset settings
export PASSWORD_RESET_TOKEN_EXPIRY_MINUTES=30
export PASSWORD_RESET_BASE_URL=http://localhost:3001/reset-password
```

---

## Testing the Feature

### Manual Testing

1. **Request Reset**:
```bash
curl -X POST http://localhost:8081/api/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{"email": "unity_admin@example.com"}'
```

2. **Verify Token** (use token from email):
```bash
curl -X POST http://localhost:8081/api/password-reset/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE"}'
```

3. **Reset Password**:
```bash
curl -X POST http://localhost:8081/api/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN_HERE", "newPassword": "NewPass123"}'
```

### Run Integration Tests

```bash
./gradlew test --tests "*PasswordReset*"
```

---

## File Locations

| Component | Location |
|-----------|----------|
| Migration | `src/main/resources/db/migration/V3__add_password_reset_tables.sql` |
| Entities | `src/main/java/io/unityfoundation/auth/entities/` |
| Repositories | `src/main/java/io/unityfoundation/auth/entities/` |
| Service | `src/main/java/io/unityfoundation/auth/PasswordResetService.java` |
| Controller | `src/main/java/io/unityfoundation/auth/PasswordResetController.java` |
| Email Service | `src/main/java/io/unityfoundation/auth/EmailService.java` |
| Validation | `src/main/java/io/unityfoundation/auth/ValidPassword.java` |
| Exceptions | `src/main/java/io/unityfoundation/auth/exceptions/` |
| Scheduler | `src/main/java/io/unityfoundation/auth/TokenCleanupService.java` |
| Tests | `src/test/java/io/unityfoundation/auth/PasswordResetTest.java` |

---

## Common Issues

### Email Not Sending

1. Check SMTP configuration in application-{env}.yml
2. Verify email service is running (MailHog for local dev)
3. Check logs for email service errors

### Rate Limiting Not Working

1. Ensure `micronaut-ratelimiter` dependency is added
2. Check rate limiter configuration in application.yml
3. Verify `@RateLimiter` annotation is on controller method

### Token Validation Failing

1. Check token format (should be 43 chars, URL-safe Base64)
2. Verify token hasn't expired (30 min default)
3. Check token hasn't been used already
4. Verify migration ran successfully

### Session Not Invalidating

1. Verify `token_version` column exists in user table
2. Check JWT includes `token_version` claim
3. Verify authentication provider validates token version

---

## Verification Checklist

After implementation, verify:

- [ ] Database migration applies cleanly
- [ ] Password reset request returns 200 (even for non-existent emails)
- [ ] Email is sent for valid accounts
- [ ] Token verification works within 30 minutes
- [ ] Token verification fails after 30 minutes
- [ ] Password reset updates password and invalidates sessions
- [ ] Rate limiting kicks in after 3 requests
- [ ] Disabled accounts cannot reset password
- [ ] Same password is rejected
- [ ] Confirmation email is sent after reset
- [ ] All events are logged to audit table
