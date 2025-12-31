# Tasks: Password Reset Workflow

**Input**: Design documents from `/specs/002-password-reset/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `UnityAuth/src/main/java/io/unityfoundation/auth/`
- **Resources**: `UnityAuth/src/main/resources/`
- **Tests**: `UnityAuth/src/test/java/io/unityfoundation/auth/`
- **Migrations**: `UnityAuth/src/main/resources/db/migration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project dependencies and build configuration

- [ ] T001 Add micronaut-email-javamail dependency to UnityAuth/build.gradle
- [ ] T002 [P] Add micronaut-ratelimiter dependency to UnityAuth/build.gradle
- [ ] T003 [P] Add password-reset configuration section to UnityAuth/src/main/resources/application.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Migration

- [ ] T004 Create database migration UnityAuth/src/main/resources/db/migration/V3__add_password_reset_tables.sql with token_version column, password_reset_token table, and password_reset_audit_log table

### Entity Classes

- [ ] T005 [P] Modify User entity to add tokenVersion field in UnityAuth/src/main/java/io/unityfoundation/auth/entities/User.java
- [ ] T006 [P] Create PasswordResetToken entity in UnityAuth/src/main/java/io/unityfoundation/auth/entities/PasswordResetToken.java
- [ ] T007 [P] Create PasswordResetAuditLog entity with EventType enum in UnityAuth/src/main/java/io/unityfoundation/auth/entities/PasswordResetAuditLog.java

### Repository Interfaces

- [ ] T008 [P] Create PasswordResetTokenRepository interface in UnityAuth/src/main/java/io/unityfoundation/auth/entities/PasswordResetTokenRepository.java
- [ ] T009 [P] Create PasswordResetAuditLogRepository interface in UnityAuth/src/main/java/io/unityfoundation/auth/entities/PasswordResetAuditLogRepository.java

### Custom Exceptions

- [ ] T010 [P] Create TokenExpiredException in UnityAuth/src/main/java/io/unityfoundation/auth/exceptions/TokenExpiredException.java
- [ ] T011 [P] Create TokenInvalidException in UnityAuth/src/main/java/io/unityfoundation/auth/exceptions/TokenInvalidException.java
- [ ] T012 [P] Create TokenAlreadyUsedException in UnityAuth/src/main/java/io/unityfoundation/auth/exceptions/TokenAlreadyUsedException.java
- [ ] T013 [P] Create SamePasswordException in UnityAuth/src/main/java/io/unityfoundation/auth/exceptions/SamePasswordException.java

### Password Validation

- [ ] T014 [P] Create @ValidPassword annotation in UnityAuth/src/main/java/io/unityfoundation/auth/ValidPassword.java
- [ ] T015 Create ValidPasswordValidator constraint validator in UnityAuth/src/main/java/io/unityfoundation/auth/ValidPasswordValidator.java (depends on T014)

### DTOs

- [ ] T016 [P] Create PasswordResetRequestDTO record in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetRequestDTO.java
- [ ] T017 [P] Create TokenVerifyRequestDTO record in UnityAuth/src/main/java/io/unityfoundation/auth/TokenVerifyRequestDTO.java
- [ ] T018 [P] Create PasswordResetConfirmDTO record in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetConfirmDTO.java
- [ ] T019 [P] Create TokenVerifyResponseDTO record in UnityAuth/src/main/java/io/unityfoundation/auth/TokenVerifyResponseDTO.java
- [ ] T020 [P] Create MessageResponseDTO record in UnityAuth/src/main/java/io/unityfoundation/auth/MessageResponseDTO.java

### Security Configuration

- [ ] T021 Add security intercept-url-map for /api/password-reset/** endpoints (isAnonymous) in UnityAuth/src/main/resources/application.yml

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Request Password Reset (Priority: P1)

**Goal**: User can request a password reset by entering their email address; system sends reset email

**Independent Test**: Submit a password reset request with a valid email and verify an email is sent with a valid reset link

**Acceptance Criteria**:
- Registered user email triggers reset email within 30 seconds
- Unregistered email returns same success message (no enumeration)
- New request invalidates previous tokens

### Email Infrastructure

- [ ] T022 [P] [US1] Create password reset email template in UnityAuth/src/main/resources/email-templates/password-reset.html
- [ ] T023 [US1] Configure email settings in UnityAuth/src/main/resources/application-local.yml (SMTP host/port, from address)
- [ ] T024 [P] [US1] Configure email settings in UnityAuth/src/main/resources/application-docker.yml (environment variables)
- [ ] T025 [US1] Create EmailService interface in UnityAuth/src/main/java/io/unityfoundation/auth/EmailService.java
- [ ] T026 [US1] Implement EmailServiceImpl with Micronaut Email in UnityAuth/src/main/java/io/unityfoundation/auth/EmailServiceImpl.java (depends on T022, T023, T025)

### Password Reset Service - Request Flow

- [ ] T027 [US1] Create PasswordResetService with requestPasswordReset method in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetService.java (depends on T006, T007, T008, T009, T026)

### Controller - Request Endpoint

- [ ] T028 [US1] Create PasswordResetController with POST /api/password-reset/request endpoint in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetController.java (depends on T016, T020, T027)
- [ ] T029 [US1] Add @RateLimiter annotation to request endpoint (3 requests/email/hour) in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetController.java (depends on T028)
- [ ] T030 [US1] Configure rate limiter settings in UnityAuth/src/main/resources/application.yml

**Checkpoint**: User Story 1 complete - password reset requests can be submitted and emails are sent

---

## Phase 4: User Story 2 - Reset Password via Token Link (Priority: P1)

**Goal**: User can click reset link, verify token, and set a new password

**Independent Test**: Use a valid reset token to set a new password and then log in with the new credentials

**Acceptance Criteria**:
- Valid token + valid password = password updated with confirmation
- Valid token + invalid password = clear error messages
- Used token = rejection error

### Password Reset Service - Verify and Confirm

- [ ] T031 [US2] Add verifyToken method to PasswordResetService in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetService.java (depends on T027)
- [ ] T032 [US2] Add confirmPasswordReset method to PasswordResetService with session invalidation in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetService.java (depends on T031)

### Controller - Verify and Confirm Endpoints

- [ ] T033 [US2] Add POST /api/password-reset/verify endpoint to PasswordResetController in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetController.java (depends on T017, T019, T031)
- [ ] T034 [US2] Add POST /api/password-reset/confirm endpoint to PasswordResetController in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetController.java (depends on T018, T032)

### Session Invalidation

- [ ] T035 [US2] Update JWT token generation to include tokenVersion claim in existing authentication logic
- [ ] T036 [US2] Update JWT validation to check tokenVersion matches user's current version

**Checkpoint**: User Story 2 complete - users can reset their password using the token link

---

## Phase 5: User Story 3 - Token Expiration and Security (Priority: P2)

**Goal**: Ensure tokens expire after 30 minutes and security measures are enforced

**Independent Test**: Attempt to use an expired token and verify it is rejected with appropriate message

**Acceptance Criteria**:
- Token older than 30 minutes = expired error
- User prompted to request new link
- Invalid/tampered token = generic rejection

### Token Cleanup

- [ ] T037 [P] [US3] Create TokenCleanupService with @Scheduled daily cleanup in UnityAuth/src/main/java/io/unityfoundation/auth/TokenCleanupService.java
- [ ] T038 [US3] Add audit log cleanup (90-day retention) to TokenCleanupService in UnityAuth/src/main/java/io/unityfoundation/auth/TokenCleanupService.java (depends on T037)

### Exception Handlers

- [ ] T039 [US3] Create exception handler for password reset exceptions in UnityAuth/src/main/java/io/unityfoundation/auth/PasswordResetExceptionHandler.java

**Checkpoint**: User Story 3 complete - token expiration and security measures are enforced

---

## Phase 6: User Story 4 - Email Notification on Successful Reset (Priority: P3)

**Goal**: User receives confirmation email after successful password reset

**Independent Test**: Complete a password reset and verify a confirmation email is sent

**Acceptance Criteria**:
- Successful reset triggers confirmation email with timestamp
- Email includes security instructions for unauthorized changes

### Confirmation Email

- [ ] T040 [P] [US4] Create password changed email template in UnityAuth/src/main/resources/email-templates/password-changed.html
- [ ] T041 [US4] Add sendPasswordChangedEmail method to EmailService in UnityAuth/src/main/java/io/unityfoundation/auth/EmailService.java (depends on T040)
- [ ] T042 [US4] Call sendPasswordChangedEmail from confirmPasswordReset in PasswordResetService (depends on T041)

**Checkpoint**: User Story 4 complete - confirmation emails are sent after password reset

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, verification, and final cleanup

### Integration Tests

- [ ] T043 [P] Create PasswordResetRequestTest for request endpoint scenarios in UnityAuth/src/test/java/io/unityfoundation/auth/PasswordResetRequestTest.java
- [ ] T044 [P] Create PasswordResetVerifyTest for token verification scenarios in UnityAuth/src/test/java/io/unityfoundation/auth/PasswordResetVerifyTest.java
- [ ] T045 [P] Create PasswordResetConfirmTest for password reset scenarios in UnityAuth/src/test/java/io/unityfoundation/auth/PasswordResetConfirmTest.java
- [ ] T046 Create PasswordResetSecurityTest for security scenarios (expiration, rate limiting, enumeration prevention) in UnityAuth/src/test/java/io/unityfoundation/auth/PasswordResetSecurityTest.java

### Verification

- [ ] T047 Run quickstart.md manual testing checklist
- [ ] T048 Verify all acceptance scenarios from spec.md pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion; can run in parallel with US1 but confirm endpoint uses email service from US1
- **User Story 3 (Phase 5)**: Depends on US1 and US2 completion (cleanup operates on created tokens)
- **User Story 4 (Phase 6)**: Depends on US2 completion (confirmation email sent after confirm)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - Integrates with US1's EmailService
- **User Story 3 (P2)**: Requires US1 and US2 (cleanup needs tokens and audit logs)
- **User Story 4 (P3)**: Requires US2 (confirmation email triggered by confirm endpoint)

### Within Each User Story

- Infrastructure/config before service logic
- Services before controllers
- Core implementation before integrations
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
```
T005, T006, T007 (entities) → run in parallel
T008, T009 (repositories) → run in parallel
T010, T011, T012, T013 (exceptions) → run in parallel
T014, T016-T020 (annotation + DTOs) → run in parallel
```

**Phase 3 (US1)**:
```
T022, T024 (email templates + docker config) → run in parallel
```

**Phase 7 (Tests)**:
```
T043, T044, T045 (test classes) → run in parallel
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Request Reset)
4. Complete Phase 4: User Story 2 (Reset Password)
5. **STOP and VALIDATE**: Test core password reset flow end-to-end
6. Deploy/demo if ready - users can now reset passwords

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test request flow → Users can request resets
3. Add User Story 2 → Test full flow → Users can complete resets (MVP!)
4. Add User Story 3 → Test security → Cleanup and hardening
5. Add User Story 4 → Test notifications → Confirmation emails
6. Each story adds value without breaking previous stories

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 48 |
| Phase 1 (Setup) | 3 |
| Phase 2 (Foundational) | 18 |
| Phase 3 (US1 - Request) | 9 |
| Phase 4 (US2 - Reset) | 6 |
| Phase 5 (US3 - Security) | 3 |
| Phase 6 (US4 - Notification) | 3 |
| Phase 7 (Polish) | 6 |
| Parallel Opportunities | 25 tasks marked [P] |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
