"""Custom exceptions for the ArgoCD migrator."""


class MigratorError(Exception):
    """Base exception for all migrator errors."""

    pass


class ScannerError(MigratorError):
    """Exception raised during file scanning."""

    pass


class ParserError(MigratorError):
    """Exception raised during YAML parsing."""

    pass


class MigrationError(MigratorError):
    """Exception raised during YAML to JSON migration."""

    pass


class ValidationError(MigratorError):
    """Exception raised during JSON Schema validation."""

    pass
