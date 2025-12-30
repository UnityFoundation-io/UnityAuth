# UnityAuth CLI Usability Recommendations

**Date**: 2025-12-30
**Status**: Draft - Pending spec update
**Sources**: [clig.dev](https://clig.dev/), [Lucas Costa UX Patterns](https://lucasfcosta.com/2022/06/01/ux-patterns-cli-tools.html), [Evil Martians](https://evilmartians.com/chronicles/cli-ux-best-practices-3-patterns-for-improving-progress-displays)

---

## Priority 1 (High Impact, Implement First)

### 1.1 Add Short Flag Aliases for Common Options

**Problem**: Users must type full flag names, slowing common workflows.

**Current**:
```bash
unityauth user list --tenant-id 1 --format json
```

**Proposed**:
```bash
unityauth user list -t 1 -o json
```

**Flag Mapping**:
| Long Flag | Short Flag | Commands |
|-----------|------------|----------|
| `--tenant-id` | `-t` | user list, user create, user update, tenant users, permissions list |
| `--format` | `-o` | All commands (global) |
| `--verbose` | `-v` | All commands (global) |
| `--email` | `-e` | user create, login |
| `--role-ids` | `-r` | user create, user update |
| `--first-name` | `-f` | user create, user update-profile |
| `--last-name` | `-l` | user create, user update-profile |
| `--password` | `-p` | user create, user update-profile |
| `--service-id` | `-s` | permissions list |

**Implementation**: Add `short_flag` parameter to Click options.

---

### 1.2 Interactive Mode for Complex Commands

**Problem**: `user create` requires 6 flags - easy to make mistakes.

**Current**:
```bash
unityauth user create --email user@example.com --first-name John \
  --last-name Doe --password MyP@ss123 --tenant-id 1 --role-ids "2"
```

**Proposed**: When run without required arguments AND stdin is a TTY, launch interactive wizard:
```bash
$ unityauth user create
Email: user@example.com
First name: John
Last name: Doe
Password: ********
Select tenant:
  [1] Production Tenant
  [2] Development Tenant
> 1
Select roles (space to toggle, enter to confirm):
  [ ] Unity Administrator
  [x] Tenant Administrator
  [x] Request Manager

✓ User created successfully (ID: 42)
```

**Behavior**:
- Interactive mode triggers when: no required args provided AND `sys.stdin.isatty()` is True
- Non-interactive fallback: fail with usage message showing required flags
- Password input uses `click.prompt(hide_input=True)`
- Tenant/role selection fetches options from API dynamically

**Commands to support**:
- `user create` - Full wizard
- `user update` - Role selection wizard
- `login` - Email/password prompts (already partially implemented)

---

### 1.3 Add `whoami` Command

**Problem**: `token-info` name is not intuitive for checking current identity.

**Proposed**: Add `whoami` as an alias or standalone command:
```bash
$ unityauth whoami
Logged in as: admin@example.com
User ID: 5
API: https://auth.example.com
Token expires: 2025-12-31 14:30:00
```

**Implementation Options**:
1. Add `whoami` as alias to `token-info`
2. Add `whoami` as separate command with simpler output
3. Keep both: `whoami` for quick check, `token-info` for full details

**Recommendation**: Option 3 - keep both commands.

---

### 1.4 Allow Empty Role IDs to Remove All Roles

**Problem**: The CLI prevents removing all roles from a user, but the backend supports it.

**Backend behavior**: `PATCH /api/users/{id}/roles` accepts an empty `roles` array. The `UpdateUserRolesRequest` has no `@NotEmpty` validation on roles (unlike `AddUserRequest` which requires at least one role for user creation).

**Current CLI validation** ([users.py:78-85](unityauth-cli/src/unityauth_cli/commands/users.py#L78-L85)):
```python
roles = [int(rid.strip()) for rid in role_ids.split(',')]
if not roles:
    raise ValidationError("At least one role ID must be provided")
```

**Proposed**: Allow empty value to remove all roles:
```bash
# Remove all roles from user 5 in tenant 1
unityauth user update 5 -t 1 -r ""
unityauth user update 5 -t 1 --role-ids ""

# Or with explicit "none" keyword
unityauth user update 5 -t 1 -r none
```

**Use case**: Soft-disable a user by removing all their roles in a tenant without deleting the user account. This preserves audit history and allows re-enabling later.

**Implementation**:
1. In `user update` command, check if `role_ids` is empty string or "none"
2. If so, send empty `roles: []` array to API
3. Add confirmation prompt: "This will remove all roles for user X in tenant Y. Continue? [y/N]"
4. Skip confirmation with `--yes` flag

**Files to modify**:
- `commands/users.py` - Update validation logic in `update` command

---

## Priority 2 (Medium Impact)

### 2.1 Add `--dry-run` Flag for Mutating Commands

**Problem**: Users cannot preview changes before execution.

**Proposed**:
```bash
$ unityauth user create --dry-run -e user@example.com -f John -l Doe \
    -p MyP@ss123 -t 1 -r "2,3"

[DRY RUN] Would create user:
  Email: user@example.com
  First Name: John
  Last Name: Doe
  Tenant ID: 1
  Role IDs: 2, 3

Run without --dry-run to execute.
```

**Commands to support**:
- `user create`
- `user update`
- `user update-profile`
- `batch create-users`

**Implementation**: Add `--dry-run` / `-n` flag; skip API call and display planned action.

---

### 2.2 Add Typo Suggestions (Did You Mean?)

**Problem**: Typos result in unhelpful "No such command" errors.

**Current**:
```bash
$ unityauth usr list
Error: No such command 'usr'.
```

**Proposed**:
```bash
$ unityauth usr list
Error: No such command 'usr'.

Did you mean one of these?
  user
```

**Implementation**: Use `click-didyoumean` package or implement Levenshtein distance matching.

---

### 2.3 Add `unityauth init` Setup Wizard

**Problem**: New users must manually figure out configuration.

**Proposed**:
```bash
$ unityauth init
Welcome to UnityAuth CLI!

API URL: https://auth.example.com
✓ Connection successful (API v1.0)
✓ Configuration saved to ~/.config/unityauth-cli/config.yml

Would you like to log in now? [Y/n]: y
Email: admin@example.com
Password: ********
✓ Logged in as admin@example.com

Setup complete! Try these commands:
  unityauth tenant list          # List your tenants
  unityauth user list -t 1       # List users in tenant 1
  unityauth --help               # See all commands
```

**Behavior**:
1. Prompt for API URL
2. Test connection to API
3. Save configuration
4. Optionally trigger login flow
5. Display next steps

---

### 2.4 Improve Empty State Messages

**Problem**: Empty results don't guide users on next steps.

**Current**:
```
⚠ No users found
```

**Proposed**:
```
No users found in tenant 1.

To create a user:
  unityauth user create -t 1 -e user@example.com ...

To list users in a different tenant:
  unityauth tenant list          # See available tenants
  unityauth user list -t <ID>    # List users in that tenant
```

**Commands to update**:
- `user list` - Suggest user create
- `tenant list` - Explain permissions
- `role list` - Explain what roles are for
- `permissions list` - Explain permission model

---

## Priority 3 (Nice to Have)

### 3.1 Support Name-Based Lookups

**Problem**: Users must look up IDs before running commands.

**Current workflow**:
```bash
unityauth tenant list              # Find tenant ID = 1
unityauth role list                # Find role ID = 2
unityauth user create --tenant-id 1 --role-ids "2" ...
```

**Proposed**: Allow names as alternative to IDs:
```bash
unityauth user create --tenant "Production" --roles "Admin,Manager" ...
```

**Implementation**:
- Accept both ID (integer) and name (string) for tenant/role parameters
- Perform API lookup to resolve name to ID
- Cache results for session to avoid repeated lookups
- Error if name is ambiguous or not found

---

### 3.2 Add Command Aliases

**Problem**: Common operations require typing full command paths.

**Proposed Aliases**:
| Full Command | Alias |
|--------------|-------|
| `unityauth user list` | `unityauth users` |
| `unityauth tenant list` | `unityauth tenants` |
| `unityauth role list` | `unityauth roles` |
| `unityauth permissions list` | `unityauth perms` |
| `unityauth token-info` | `unityauth whoami` |

**Implementation**: Register additional commands that delegate to originals.

---

### 3.3 Add `--quiet` / `-q` Flag for Scripting

**Problem**: Success messages interfere with output parsing in scripts.

**Current**:
```bash
$ unityauth user create ...
✓ User created successfully (ID: 42)
```

**Proposed with `--quiet`**:
```bash
$ unityauth user create --quiet ...
42
```

**Behavior**:
- Suppress all non-error output
- Return only essential data (IDs, counts)
- Useful for scripting: `USER_ID=$(unityauth user create -q ...)`

**Implementation**: Add global `--quiet` / `-q` flag; check before printing success/info messages.

---

### 3.4 Group Commands in Help Output

**Problem**: Help shows commands alphabetically, not by function.

**Current**:
```
Commands:
  config      Configuration management commands.
  login       Authenticate with UnityAuth API.
  logout      Clear stored authentication token.
  permissions Permission discovery and verification...
  role        Role discovery commands.
  tenant      Tenant discovery and management commands.
  token-info  Display information about current...
  user        User account management commands.
```

**Proposed**:
```
Authentication:
  login       Authenticate with UnityAuth API
  logout      Clear stored authentication token
  whoami      Display current user info

User Management:
  user        User account management commands

Discovery:
  tenant      Tenant discovery commands
  role        Role discovery commands
  permissions Permission verification commands

Configuration:
  config      Configuration management commands

Run 'unityauth COMMAND --help' for more information.
```

**Implementation**: Use Click's command grouping or custom help formatter.

---

### 3.5 Add Confirmation for Destructive Actions

**Problem**: Role updates execute immediately without confirmation.

**Proposed**:
```bash
$ unityauth user update 5 -t 1 -r "1"
This will replace all roles for user john@example.com in tenant Production.

Current roles: Admin, Manager, Viewer
New roles: Admin

Continue? [y/N]: y
✓ User 5 roles updated successfully
```

**Behavior**:
- Fetch current state before modification
- Show diff of changes
- Require explicit confirmation
- Add `--yes` / `-y` flag to skip confirmation for automation

**Commands to add confirmation**:
- `user update` (role changes)
- `batch create-users` (bulk operations)

---

### 3.6 Better Progress Feedback for Batch Operations

**Problem**: Long batch operations appear to hang.

**Proposed**: Use Rich progress bars:
```bash
$ unityauth batch create-users users.csv
Validating CSV... ✓ 100 records found

Creating users ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45/100 • 00:23 remaining

Summary:
  ✓ 98 users created successfully
  ✗ 2 users failed (see errors below)

Errors:
  Row 23: duplicate@example.com - User already exists
  Row 67: invalid email format
```

**Implementation**: Use `rich.progress.Progress` for batch operations.

---

## Implementation Checklist

### Phase 1: Quick Wins (P1)
- [ ] Add short flags to all commands
- [ ] Add `whoami` command
- [ ] Add interactive mode detection (`sys.stdin.isatty()`)
- [ ] Implement interactive wizard for `user create`
- [ ] Allow empty `--role-ids` to remove all roles from user

### Phase 2: Enhanced UX (P2)
- [ ] Add `--dry-run` flag to mutating commands
- [ ] Add typo suggestions with `click-didyoumean`
- [x] Create `unityauth init` setup wizard
- [ ] Improve empty state messages with next steps

### Phase 3: Polish (P3)
- [ ] Support name-based tenant/role lookups
- [ ] Add command aliases
- [ ] Add `--quiet` flag for scripting
- [ ] Reorganize help output by category
- [ ] Add confirmation prompts for destructive actions
- [ ] Add Rich progress bars for batch operations

---

## Files to Modify

| File | Changes |
|------|---------|
| `cli.py` | Add `-v` short flag, `--quiet` global flag, help formatting |
| `commands/login.py` | Add `-e` short flag, `whoami` command |
| `commands/users.py` | Add short flags, interactive mode, `--dry-run`, confirmation |
| `commands/tenants.py` | Add short flags, name-based lookup |
| `commands/roles.py` | Add short flags |
| `commands/permissions.py` | Add `-t`, `-s` short flags |
| `commands/config.py` | Add `init` command |
| `commands/batch.py` | Add `--dry-run`, Rich progress bars |
| `utils/interactive.py` | New file for interactive prompts |
| `pyproject.toml` | Add `click-didyoumean` dependency |

---

## Dependencies to Add

```toml
[project.dependencies]
click-didyoumean = "^0.3.0"  # Typo suggestions
```

Note: `rich` is already included for styled output.
