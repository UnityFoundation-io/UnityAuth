"""Custom exception hierarchy for UnityAuth CLI.

All CLI-specific exceptions with associated exit codes.
"""


class UnityAuthCLIError(Exception):
    """Base exception for all CLI errors.

    All custom exceptions should inherit from this base class.
    """
    exit_code = 1

    def __init__(self, message: str, details: str = "") -> None:
        """Initialize error with message and optional details.

        Args:
            message: Primary error message
            details: Additional context or guidance for the user
        """
        self.message = message
        self.details = details
        super().__init__(message)


class AuthenticationError(UnityAuthCLIError):
    """Authentication failed (invalid credentials, expired token).

    Exit code 2 indicates the user needs to run 'unityauth login'.
    """
    exit_code = 2


class PermissionError(UnityAuthCLIError):
    """Insufficient permissions for operation.

    Exit code 3 indicates the user lacks required permissions.
    """
    exit_code = 3


class ConfigurationError(UnityAuthCLIError):
    """Invalid configuration (missing API endpoint, invalid config).

    Exit code 4 indicates configuration problems.
    """
    exit_code = 4


class ValidationError(UnityAuthCLIError):
    """Input validation failed.

    Exit code 1 for general validation errors.
    """
    exit_code = 1


class NetworkError(UnityAuthCLIError):
    """Network connectivity issue.

    Exit code 1 for network-related errors.
    """
    exit_code = 1


class RateLimitError(UnityAuthCLIError):
    """API rate limit exceeded.

    Exit code 1 with retry guidance.
    """
    exit_code = 1

    def __init__(self, message: str, retry_after: int = 60) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(
            message,
            f"Wait {retry_after} seconds and try again"
        )


class NotFoundError(UnityAuthCLIError):
    """Resource not found.

    Exit code 1 for missing resources.
    """
    exit_code = 1


class ServerError(UnityAuthCLIError):
    """Server-side error (5xx responses).

    Exit code 1 with guidance to contact administrator.
    """
    exit_code = 1

    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize server error.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.status_code = status_code
        super().__init__(
            message,
            "Contact administrator if this error persists"
        )


class VersionMismatchError(UnityAuthCLIError):
    """CLI version incompatible with API version.

    Exit code 4 indicates version compatibility issue.
    """
    exit_code = 4
