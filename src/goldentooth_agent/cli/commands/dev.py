"""Development commands for maintaining the Goldentooth Agent codebase."""

from pathlib import Path
from typing import Annotated

import typer
from antidote import inject

from goldentooth_agent.core.dev.metadata_generator import ModuleMetadataGenerator

app = typer.Typer(help="Development utilities for maintaining the codebase.")

module_app = typer.Typer(help="Module management commands.")
app.add_typer(module_app, name="module")


@module_app.command("update")
def update_module_metadata(
    module_path: Annotated[
        str, typer.Argument(help="Path to the module directory to update")
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force update even if no changes detected"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-n", help="Show what would be updated without making changes"
        ),
    ] = False,
) -> None:
    """Update README.meta.yaml for a specific module."""

    @inject
    def handle() -> None:
        """Handle the metadata update command."""
        generator = ModuleMetadataGenerator()

        path = Path(module_path).resolve()
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        if not path.is_dir():
            typer.echo(f"Error: Path {path} is not a directory", err=True)
            raise typer.Exit(1)

        try:
            result = generator.update_module_metadata(
                path, force=force, dry_run=dry_run
            )

            if dry_run:
                if result.would_update:
                    typer.echo(f"Would update {path / 'README.meta.yaml'}")
                    typer.echo("Changes:")
                    for change in result.changes:
                        typer.echo(f"  - {change}")
                else:
                    typer.echo(f"No updates needed for {path}")
            else:
                if result.updated:
                    typer.echo(f"✓ Updated {path / 'README.meta.yaml'}")
                    if result.changes:
                        typer.echo("Changes made:")
                        for change in result.changes:
                            typer.echo(f"  - {change}")
                else:
                    typer.echo(f"✓ No updates needed for {path}")

        except Exception as e:
            typer.echo(f"Error updating metadata: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("update-all")
def update_all_modules(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force update even if no changes detected"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-n", help="Show what would be updated without making changes"
        ),
    ] = False,
) -> None:
    """Update README.meta.yaml for all modules in the project."""

    @inject
    def handle() -> None:
        """Handle the update-all command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            results = generator.update_all_modules(root, force=force, dry_run=dry_run)

            updated_count = sum(1 for r in results if r.updated or r.would_update)
            total_count = len(results)

            if dry_run:
                typer.echo(f"Would update {updated_count} of {total_count} modules")
                for result in results:
                    if result.would_update:
                        typer.echo(f"  - {result.module_path}")
            else:
                typer.echo(f"✓ Updated {updated_count} of {total_count} modules")
                for result in results:
                    if result.updated:
                        typer.echo(f"  ✓ {result.module_path}")

        except Exception as e:
            typer.echo(f"Error updating modules: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("update-changed")
def update_changed_modules(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
    since_commit: Annotated[
        str,
        typer.Option(
            "--since", "-s", help="Compare against this commit (default: HEAD)"
        ),
    ] = "HEAD",
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force update even if no changes detected"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run", "-n", help="Show what would be updated without making changes"
        ),
    ] = False,
) -> None:
    """Update README.meta.yaml for modules that have changed since the specified commit."""

    @inject
    def handle() -> None:
        """Handle the update-changed command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            results = generator.update_changed_modules(
                root, since_commit=since_commit, force=force, dry_run=dry_run
            )

            if not results:
                typer.echo(f"No Python modules have changed since {since_commit}")
                return

            updated_count = sum(1 for r in results if r.updated or r.would_update)
            total_count = len(results)

            if dry_run:
                typer.echo(
                    f"Would update {updated_count} of {total_count} changed modules"
                )
                for result in results:
                    if result.would_update:
                        typer.echo(f"  - {result.module_path}")
                        for change in result.changes:
                            typer.echo(f"    • {change}")
            else:
                typer.echo(
                    f"✓ Updated {updated_count} of {total_count} changed modules"
                )
                for result in results:
                    if result.updated:
                        typer.echo(f"  ✓ {result.module_path}")
                        for change in result.changes:
                            typer.echo(f"    • {change}")

        except Exception as e:
            typer.echo(f"Error updating changed modules: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("pre-commit-update")
def pre_commit_update(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Update metadata for modules with staged changes (optimized for pre-commit)."""

    @inject
    def handle() -> None:
        """Handle the pre-commit update command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            results = generator.update_for_pre_commit(root)

            if not results:
                # No staged modules, exit silently
                return

            updated_count = sum(1 for r in results if r.updated)

            if updated_count > 0:
                typer.echo(
                    f"Updated metadata for {updated_count} modules with staged changes"
                )
                for result in results:
                    if result.updated:
                        typer.echo(f"  ✓ {result.module_path.name}")

        except Exception as e:
            typer.echo(f"Error updating metadata for pre-commit: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("validate-for-commit")
def validate_for_commit(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Validate metadata for modules that will be committed."""

    @inject
    def handle() -> None:
        """Handle the validate-for-commit command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            errors = generator.validate_for_commit(root)

            if errors:
                typer.echo("Metadata validation errors found:")
                for error in errors:
                    typer.echo(f"  ✗ {error}")
                typer.echo("\nPlease fix these errors before committing.")
                raise typer.Exit(1)
            else:
                typer.echo("✓ All staged module metadata is valid")

        except Exception as e:
            typer.echo(f"Error validating metadata for commit: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("check-freshness")
def check_metadata_freshness(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
    staged_only: Annotated[
        bool,
        typer.Option(
            "--staged-only", "-s", help="Only check modules with staged changes"
        ),
    ] = False,
) -> None:
    """Check that README.meta.yaml files are newer than their Python files."""

    @inject
    def handle() -> None:
        """Handle the freshness check command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            if staged_only:
                stale_modules = generator.check_staged_metadata_freshness(root)
                scope = "staged modules"
            else:
                stale_modules = generator.check_metadata_freshness(root)
                scope = "all modules"

            if stale_modules:
                typer.echo(f"Stale metadata detected in {scope}:")
                for stale_info in stale_modules:
                    typer.echo(f"  ✗ {stale_info}")
                typer.echo(
                    "\nRun 'goldentooth-agent dev module update-all' to refresh metadata."
                )
                raise typer.Exit(1)
            else:
                typer.echo(f"✓ All metadata files are up-to-date for {scope}")

        except Exception as e:
            typer.echo(f"Error checking metadata freshness: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("check-freshness-for-commit")
def check_freshness_for_commit(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Check metadata freshness for modules that will be committed (pre-commit hook)."""

    @inject
    def handle() -> None:
        """Handle the commit freshness check command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            stale_modules = generator.check_staged_metadata_freshness(root)

            if stale_modules:
                typer.echo("Stale metadata detected for staged modules:")
                for stale_info in stale_modules:
                    typer.echo(f"  ✗ {stale_info}")
                typer.echo(
                    "\nMetadata files must be newer than Python files before committing."
                )
                typer.echo(
                    "Run the pre-commit metadata update to fix this automatically."
                )
                raise typer.Exit(1)

            # Exit silently if all metadata is fresh

        except Exception as e:
            typer.echo(f"Error checking metadata freshness for commit: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("commit-message-info")
def commit_message_info(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Generate commit message information about metadata changes."""

    @inject
    def handle() -> None:
        """Handle the commit message info command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            return  # Exit silently if root doesn't exist

        try:
            message_info = generator.generate_commit_message_info(root)
            if message_info:
                typer.echo(message_info)
        except Exception:
            # Exit silently on any errors for commit message generation
            pass

    handle()


@module_app.command("validate")
def validate_metadata(
    module_path: Annotated[
        str | None,
        typer.Argument(help="Path to module to validate (or all if not specified)"),
    ] = None,
    project_root: Annotated[
        str | None, typer.Option("--root", "-r", help="Project root directory")
    ] = None,
) -> None:
    """Validate README.meta.yaml files against actual module content."""

    generator = ModuleMetadataGenerator()

    if module_path:
        # Validate single module
        path = Path(module_path).resolve()
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        try:
            errors = generator.validate_module_metadata(path)
            if errors:
                typer.echo(f"Validation errors for {path}:")
                for error in errors:
                    typer.echo(f"  ✗ {error}")
                raise typer.Exit(1)
            else:
                typer.echo(f"✓ {path} metadata is valid")
        except Exception as e:
            typer.echo(f"Error validating {path}: {e}", err=True)
            raise typer.Exit(1)
    else:
        # Validate all modules
        root = Path(project_root or ".").resolve()
        try:
            all_errors = generator.validate_all_metadata(root)

            if all_errors:
                typer.echo("Validation errors found:")
                for module_path_item, errors in all_errors.items():
                    typer.echo(f"\n{module_path_item}:")
                    for error in errors:
                        typer.echo(f"  ✗ {error}")
                raise typer.Exit(1)
            else:
                typer.echo("✓ All module metadata is valid")

        except Exception as e:
            typer.echo(f"Error during validation: {e}", err=True)
            raise typer.Exit(1)


@module_app.command("generate-readme")
def generate_readme(
    module_path: Annotated[
        str | None,
        typer.Argument(
            help="Path to the module directory (optional - generates all if not provided)"
        ),
    ] = None,
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root",
            "-r",
            help="Project root directory (defaults to current, used when generating all)",
        ),
    ] = None,
) -> None:
    """Generate README.md from README.meta.yaml for a specific module or all modules."""

    @inject
    def handle() -> None:
        """Handle the README generation command."""
        generator = ModuleMetadataGenerator()

        if module_path:
            # Generate for specific module
            path = Path(module_path).resolve()
            if not path.exists():
                typer.echo(f"Error: Path {path} does not exist", err=True)
                raise typer.Exit(1)

            if not path.is_dir():
                typer.echo(f"Error: Path {path} is not a directory", err=True)
                raise typer.Exit(1)

            try:
                if generator.write_readme_from_metadata(path):
                    typer.echo(f"✓ Generated {path / 'README.md'}")
                else:
                    typer.echo(
                        f"Error: Could not generate README.md for {path}", err=True
                    )
                    raise typer.Exit(1)

            except Exception as e:
                typer.echo(f"Error generating README: {e}", err=True)
                raise typer.Exit(1)
        else:
            # Generate for all modules
            root = Path(project_root or ".").resolve()
            if not root.exists():
                typer.echo(f"Error: Project root {root} does not exist", err=True)
                raise typer.Exit(1)

            try:
                updated_readmes = generator.update_all_readmes(root)

                if updated_readmes:
                    typer.echo(f"✓ Generated {len(updated_readmes)} README.md files")
                    for readme_file in updated_readmes:
                        typer.echo(f"  ✓ {readme_file}")
                else:
                    typer.echo("No README.md files generated")

            except Exception as e:
                typer.echo(f"Error generating README files: {e}", err=True)
                raise typer.Exit(1)

    handle()


@module_app.command("generate-readme-for-commit")
def generate_readme_for_commit(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Generate README.md files for modules with staged changes (pre-commit hook)."""

    @inject
    def handle() -> None:
        """Handle the commit README generation command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            # Get modules with staged changes
            staged_modules = generator._get_staged_python_modules(root)

            updated_readmes = []
            for module_dir in staged_modules:
                # Check if module has metadata file
                meta_file = module_dir / "README.meta.yaml"
                if meta_file.exists():
                    if generator.write_readme_from_metadata(module_dir):
                        readme_file = module_dir / "README.md"
                        # Stage the updated README file
                        generator._stage_file(readme_file)
                        updated_readmes.append(readme_file)

            if updated_readmes:
                typer.echo(
                    f"Generated and staged {len(updated_readmes)} README.md files for staged modules"
                )
                for readme_file in updated_readmes:
                    typer.echo(f"  ✓ {readme_file.parent.name}/README.md")

            # Exit silently if no README files needed updating

        except Exception as e:
            typer.echo(f"Error generating README files for commit: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("check-readme-freshness")
def check_readme_freshness(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
    staged_only: Annotated[
        bool,
        typer.Option(
            "--staged-only", "-s", help="Only check modules with staged changes"
        ),
    ] = False,
) -> None:
    """Check that README.md files are newer than their README.meta.yaml files."""

    @inject
    def handle() -> None:
        """Handle the README freshness check command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            if staged_only:
                stale_readmes = generator.check_staged_readme_freshness(root)
                scope = "staged modules"
            else:
                stale_readmes = generator.check_readme_freshness(root)
                scope = "all modules"

            if stale_readmes:
                typer.echo(f"Stale README.md files detected in {scope}:")
                for stale_info in stale_readmes:
                    typer.echo(f"  ✗ {stale_info}")
                typer.echo(
                    "\nRun 'goldentooth-agent dev module generate-readme' to refresh README files."
                )
                raise typer.Exit(1)
            else:
                typer.echo(f"✓ All README.md files are up-to-date for {scope}")

        except Exception as e:
            typer.echo(f"Error checking README freshness: {e}", err=True)
            raise typer.Exit(1)

    handle()


@module_app.command("check-readme-freshness-for-commit")
def check_readme_freshness_for_commit(
    project_root: Annotated[
        str | None,
        typer.Option(
            "--root", "-r", help="Project root directory (defaults to current)"
        ),
    ] = None,
) -> None:
    """Check README freshness for modules that will be committed (pre-commit hook)."""

    @inject
    def handle() -> None:
        """Handle the commit README freshness check command."""
        generator = ModuleMetadataGenerator()

        root = Path(project_root or ".").resolve()
        if not root.exists():
            typer.echo(f"Error: Project root {root} does not exist", err=True)
            raise typer.Exit(1)

        try:
            stale_readmes = generator.check_staged_readme_freshness(root)

            if stale_readmes:
                typer.echo("Stale README.md files detected for staged modules:")
                for stale_info in stale_readmes:
                    typer.echo(f"  ✗ {stale_info}")
                typer.echo(
                    "\nREADME.md files must be newer than README.meta.yaml files before committing."
                )
                typer.echo(
                    "Run 'goldentooth-agent dev module generate-readme' to fix this automatically."
                )
                raise typer.Exit(1)

            # Exit silently if all README files are fresh

        except Exception as e:
            typer.echo(f"Error checking README freshness for commit: {e}", err=True)
            raise typer.Exit(1)

    handle()
