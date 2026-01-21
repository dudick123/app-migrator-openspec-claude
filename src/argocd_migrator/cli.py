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
    input_path: Annotated[
        Path,
        typer.Option(
            "--input-path",
            "-i",
            help="Input directory containing ArgoCD Application YAML files",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output-file",
            "-o",
            help="Output file path for aggregated config.json",
        ),
    ] = Path("config.json"),
    no_validate: Annotated[
        bool,
        typer.Option(
            "--no-validate",
            help="Skip aggregated config validation",
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
    Migrate ArgoCD Application YAML files to aggregated ApplicationSet generator config.

    Scans the input directory for YAML files, parses them as ArgoCD Applications,
    transforms them to ApplicationSet generator config format, and aggregates all
    configurations into a single config.json file.
    """
    setup_logging(verbose, quiet)

    try:
        typer.echo(f"Migrating ArgoCD Applications from {input_path} to {output_file}")

        result = run_pipeline(
            source_dir=input_path,
            output_file=output_file,
            validate=not no_validate,
        )

        # Display summary
        if not quiet:
            typer.echo("\nMigration Summary:")
            typer.echo(f"  Total applications: {result.total}")
            typer.echo(f"  Successfully transformed: {result.successful}")
            typer.echo(f"  Failed: {result.failed}")
            if result.total > 0:
                typer.echo(f"  Success rate: {result.success_rate:.1f}%")

        # Display failures
        if result.failed > 0 and not quiet:
            typer.echo("\nFailed transformations:")
            for r in result.results:
                if not r.success:
                    typer.echo(f"  ✗ {r.source_file}: {r.error}")

        # Exit with appropriate code
        if result.failed > 0 or not result.output_file:
            raise typer.Exit(code=1)
        else:
            typer.echo(f"\n✓ Successfully generated {output_file}")
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
