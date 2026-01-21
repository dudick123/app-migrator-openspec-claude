"""CLI interface for ArgoCD migrator."""

import logging
from pathlib import Path
from typing import Annotated

import typer

from argocd_migrator.exceptions import MigratorError
from argocd_migrator.pipeline import run_pipeline

app = typer.Typer(
    name="argocd-migrator",
    help="Migrate ArgoCD Application manifests from YAML to JSON",
    add_completion=False,
)


def setup_logging(verbose: bool, quiet: bool) -> None:
    """
    Configure logging based on verbosity flags.

    Args:
        verbose: Enable verbose (DEBUG) logging
        quiet: Suppress all output except errors
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


@app.command()
def migrate(
    source: Annotated[
        Path,
        typer.Argument(
            help="Source directory containing YAML files",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for JSON files",
        ),
    ] = Path("./output"),
    no_validate: Annotated[
        bool,
        typer.Option(
            "--no-validate",
            help="Skip JSON Schema validation",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose output",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress all output except errors",
        ),
    ] = False,
) -> None:
    """
    Migrate ArgoCD Application YAML files to JSON format.

    Scans the source directory for YAML files, parses them as ArgoCD Applications,
    converts them to JSON, and optionally validates against JSON Schema.
    """
    setup_logging(verbose, quiet)

    try:
        typer.echo(f"Migrating ArgoCD Applications from {source} to {output}")

        result = run_pipeline(
            source_dir=source,
            output_dir=output,
            validate=not no_validate,
        )

        # Display summary
        if not quiet:
            typer.echo("\nMigration Summary:")
            typer.echo(f"  Total files: {result.total}")
            typer.echo(f"  Successful: {result.successful}")
            typer.echo(f"  Failed: {result.failed}")
            typer.echo(f"  Success rate: {result.success_rate:.1f}%")

        # Display failures
        if result.failed > 0 and not quiet:
            typer.echo("\nFailed migrations:")
            for r in result.results:
                if not r.success:
                    typer.echo(f"  ✗ {r.source_file}: {r.error}")

        # Exit with appropriate code
        if result.failed > 0:
            raise typer.Exit(code=1)
        else:
            typer.echo("\n✓ All migrations completed successfully")
            raise typer.Exit(code=0)

    except typer.Exit:
        raise
    except MigratorError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(code=2)


@app.command()
def version() -> None:
    """Display version information."""
    from argocd_migrator import __version__

    typer.echo(f"argocd-migrator version {__version__}")


def main() -> None:
    """Main entry point for CLI."""
    app()
