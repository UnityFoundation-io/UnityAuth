# DTO Contracts: Password Reset Workflow

**Feature**: 002-password-reset
**Date**: 2025-12-31

## Request/Response DTOs

All DTOs use Java `record` classes with `@Serdeable` annotation following existing UnityAuth patterns.

---

### Request DTOs

#### PasswordResetRequestDTO

```java
@Serdeable
public record PasswordResetRequestDTO(
    @NotNull
    @Email
    String email
) {}
```

**Usage**: `POST /api/password-reset/request`

---

#### TokenVerifyRequestDTO

```java
@Serdeable
public record TokenVerifyRequestDTO(
    @NotNull
    @Size(min = 43, max = 43)
    String token
) {}
```

**Usage**: `POST /api/password-reset/verify`

---

#### PasswordResetConfirmDTO

```java
@Serdeable
public record PasswordResetConfirmDTO(
    @NotNull
    @Size(min = 43, max = 43)
    String token,

    @NotNull
    @ValidPassword  // Custom annotation
    String newPassword
) {}
```

**Usage**: `POST /api/password-reset/confirm`

---

### Response DTOs

#### MessageResponseDTO

Generic success response used across multiple endpoints.

```java
@Serdeable
public record MessageResponseDTO(
    String message
) {}
```

---

#### TokenVerifyResponseDTO

```java
@Serdeable
public record TokenVerifyResponseDTO(
    boolean valid,
    String email,      // Masked for privacy: "u***r@example.com"
    Instant expiresAt
) {}
```

---

#### ValidationErrorDTO

```java
@Serdeable
public record ValidationErrorDTO(
    String error,
    List<FieldViolation> violations
) {
    @Serdeable
    public record FieldViolation(
        String field,
        String message
    ) {}
}
```

---

### Custom Validation Annotation

#### @ValidPassword

```java
@Documented
@Constraint(validatedBy = ValidPasswordValidator.class)
@Target({ElementType.FIELD, ElementType.PARAMETER})
@Retention(RetentionPolicy.RUNTIME)
public @interface ValidPassword {
    String message() default "Password does not meet security requirements";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

#### ValidPasswordValidator

```java
public class ValidPasswordValidator implements ConstraintValidator<ValidPassword, String> {

    private static final int MIN_LENGTH = 8;
    private static final Pattern UPPERCASE = Pattern.compile("[A-Z]");
    private static final Pattern LOWERCASE = Pattern.compile("[a-z]");
    private static final Pattern DIGIT = Pattern.compile("[0-9]");

    @Override
    public boolean isValid(String password, ConstraintValidatorContext context) {
        if (password == null) {
            return false;
        }

        List<String> violations = new ArrayList<>();

        if (password.length() < MIN_LENGTH) {
            violations.add("Password must be at least 8 characters");
        }
        if (!UPPERCASE.matcher(password).find()) {
            violations.add("Password must contain at least one uppercase letter");
        }
        if (!LOWERCASE.matcher(password).find()) {
            violations.add("Password must contain at least one lowercase letter");
        }
        if (!DIGIT.matcher(password).find()) {
            violations.add("Password must contain at least one number");
        }

        if (!violations.isEmpty()) {
            context.disableDefaultConstraintViolation();
            for (String violation : violations) {
                context.buildConstraintViolationWithTemplate(violation)
                    .addConstraintViolation();
            }
            return false;
        }

        return true;
    }
}
```

---

## Service Interface Contracts

### PasswordResetService

```java
@Singleton
public interface PasswordResetService {

    /**
     * Initiates password reset for given email.
     * Returns success even if email not found (security).
     *
     * @param email User's email address
     * @param ipAddress Client IP for audit
     * @param userAgent Client user agent for audit
     */
    void requestPasswordReset(String email, String ipAddress, String userAgent);

    /**
     * Verifies if a reset token is valid.
     *
     * @param token The reset token
     * @return Token details if valid
     * @throws TokenExpiredException if token expired
     * @throws TokenInvalidException if token invalid or used
     */
    TokenVerifyResponseDTO verifyToken(String token);

    /**
     * Completes password reset with new password.
     *
     * @param token The reset token
     * @param newPassword The new password (already validated)
     * @param ipAddress Client IP for audit
     * @param userAgent Client user agent for audit
     * @throws TokenExpiredException if token expired
     * @throws TokenInvalidException if token invalid or used
     * @throws SamePasswordException if new password matches current
     * @throws UserDisabledException if user account disabled
     */
    void confirmPasswordReset(String token, String newPassword, String ipAddress, String userAgent);
}
```

---

### EmailService

```java
@Singleton
public interface EmailService {

    /**
     * Sends password reset email with reset link.
     *
     * @param to Recipient email
     * @param resetLink Full URL to password reset page with token
     * @param expirationMinutes Minutes until link expires
     */
    void sendPasswordResetEmail(String to, String resetLink, int expirationMinutes);

    /**
     * Sends password change confirmation email.
     *
     * @param to Recipient email
     * @param changedAt Timestamp when password was changed
     */
    void sendPasswordChangedEmail(String to, Instant changedAt);
}
```

---

## Exception Contracts

### Custom Exceptions

```java
public class TokenExpiredException extends RuntimeException {
    public TokenExpiredException() {
        super("This password reset link has expired. Please request a new one.");
    }
}

public class TokenInvalidException extends RuntimeException {
    public TokenInvalidException() {
        super("This password reset link is invalid.");
    }
}

public class TokenAlreadyUsedException extends RuntimeException {
    public TokenAlreadyUsedException() {
        super("This password reset link has already been used.");
    }
}

public class SamePasswordException extends RuntimeException {
    public SamePasswordException() {
        super("New password must be different from your current password.");
    }
}
```

### Exception Handler Mappings

| Exception | HTTP Status | Error Code |
|-----------|-------------|------------|
| TokenExpiredException | 400 | Token expired |
| TokenInvalidException | 400 | Invalid token |
| TokenAlreadyUsedException | 400 | Token already used |
| SamePasswordException | 400 | Validation failed |
| UserDisabledException | 403 | Account disabled |
| RateLimitException | 429 | Too many requests |
| EmailServiceException | 503 | Service unavailable |
