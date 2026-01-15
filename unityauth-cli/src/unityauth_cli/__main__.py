"""Entry point for UnityAuth CLI.

This module is executed when running: python -m unityauth_cli
"""

import sys

from unityauth_cli.cli import cli, handle_error, register_commands


def main() -> None:
    """Main entry point for CLI execution."""
    # Register all commands
    register_commands()

    # Run CLI
    try:
        cli(prog_name='unityauth')
    except Exception as e:
        handle_error(e)


if __name__ == '__main__':
    main()
