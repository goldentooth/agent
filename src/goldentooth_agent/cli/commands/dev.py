"""Development commands for maintaining the Goldentooth Agent codebase."""

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from antidote import inject

from goldentooth_agent.core.dev.metadata_generator import ModuleMetadataGenerator

app = typer.Typer(help="Development utilities for maintaining the codebase.")

module_app = typer.Typer(help="Module management commands.")
app.add_typer(module_app, name="module")


@app.command("quick-check")
def quick_check_command(
    file_path: Annotated[str, typer.Argument(help="Path to the file to check")]
) -> None:
    """Provide quick development feedback without blocking."""
    from goldentooth_agent.dev.quick_check import quick_check

    quick_check(file_path)


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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e
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
            raise typer.Exit(1) from e


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
                raise typer.Exit(1) from e
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
                raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

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
            raise typer.Exit(1) from e

    handle()


@module_app.command("check-background")
def check_background_files(
    project_root: Annotated[
        str,
        typer.Option(
            "--project-root",
            "-p",
            help="Project root directory (defaults to current directory)",
        ),
    ] = ".",
) -> None:
    """Check for missing README.bg.md files in modules."""

    @inject
    def handle() -> None:
        """Handle the background file check command."""
        generator = ModuleMetadataGenerator()

        root_path = Path(project_root).resolve()
        if not root_path.exists():
            typer.echo(f"Error: Project root {root_path} does not exist", err=True)
            raise typer.Exit(1)

        try:
            missing_files = generator.check_background_files(root_path)

            if missing_files:
                typer.echo("Missing README.bg.md files in modules:")
                for missing_info in missing_files:
                    typer.echo(f"  ✗ {missing_info}")
                typer.echo(
                    "\nConsider adding README.bg.md files to provide background and motivation for these modules."
                )
                typer.echo(
                    "Use 'goldentooth-agent dev module generate-background <module>' to create them."
                )
            else:
                typer.echo("✓ All modules have README.bg.md files")

        except Exception as e:
            typer.echo(f"Error checking background files: {e}", err=True)
            raise typer.Exit(1) from e

    handle()


@module_app.command("check-background-for-commit")
def check_background_files_for_commit(
    project_root: Annotated[
        str,
        typer.Option(
            "--project-root",
            "-p",
            help="Project root directory (defaults to current directory)",
        ),
    ] = ".",
) -> None:
    """Check for missing README.bg.md files in modules with staged changes (pre-commit hook)."""

    @inject
    def handle() -> None:
        """Handle the background file check for commit command."""
        generator = ModuleMetadataGenerator()

        root_path = Path(project_root).resolve()
        if not root_path.exists():
            typer.echo(f"Error: Project root {root_path} does not exist", err=True)
            raise typer.Exit(1)

        try:
            missing_files = generator.check_staged_background_files(root_path)

            if missing_files:
                typer.echo("Missing README.bg.md files for staged modules:")
                for missing_info in missing_files:
                    typer.echo(f"  ✗ {missing_info}")
                typer.echo(
                    "\nModules with changes should have README.bg.md files before committing."
                )
                typer.echo(
                    "Use 'goldentooth-agent dev module generate-background <module>' to create them."
                )
                raise typer.Exit(1)

            # Exit silently if all background files are present

        except Exception as e:
            typer.echo(f"Error checking background files for commit: {e}", err=True)
            raise typer.Exit(1) from e

    handle()


@module_app.command("generate-background")
def generate_background_file(
    module_path: Annotated[
        str | None,
        typer.Argument(
            help="Path to the module directory (optional - generates for all modules if not provided)"
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
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing README.bg.md files"),
    ] = False,
    ai_powered: Annotated[
        bool,
        typer.Option(
            "--ai",
            help="Use AI to analyze modules and generate comprehensive backgrounds",
        ),
    ] = False,
    template_only: Annotated[
        bool,
        typer.Option("--template-only", help="Generate templates without AI analysis"),
    ] = False,
) -> None:
    """Generate README.bg.md files for a specific module or all modules with optional AI assistance."""

    @inject
    def handle() -> None:
        """Handle the background generation command."""
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

            _generate_single_background(
                generator, path, force, ai_powered, template_only
            )
        else:
            # Generate for all significant modules
            root = Path(project_root or ".").resolve()
            if not root.exists():
                typer.echo(f"Error: Project root {root} does not exist", err=True)
                raise typer.Exit(1)

            _generate_all_backgrounds(generator, root, force, ai_powered, template_only)

    handle()


def _generate_single_background(
    generator: "ModuleMetadataGenerator",
    path: Path,
    force: bool,
    ai_powered: bool,
    template_only: bool,
) -> None:
    """Generate background file for a single module."""
    bg_file = path / "README.bg.md"
    if bg_file.exists() and not force:
        typer.echo(
            f"README.bg.md already exists in {path.name}. Use --force to overwrite."
        )
        raise typer.Exit(1)

    try:
        # Determine if we should use AI generation or template
        should_use_template = template_only or not ai_powered

        if ai_powered and not template_only:
            # Use AI-powered generation
            typer.echo(
                f"🔍 Analyzing {path.name} module for AI-powered background generation..."
            )

            analysis_data = generator.analyze_module_for_background(path)

            if "error" in analysis_data:
                typer.echo(f"⚠️  Error analyzing module: {analysis_data['error']}")
                typer.echo("Falling back to template generation...")
                should_use_template = True
            else:
                # Generate AI prompt and create background content
                ai_content = _generate_ai_background_content(analysis_data)
                if ai_content:
                    with open(bg_file, "w", encoding="utf-8") as f:
                        f.write(ai_content)

                    typer.echo(f"🤖 Generated AI-powered README.bg.md for {path.name}")
                    typer.echo(
                        "✨ Review and customize the generated content as needed."
                    )
                    return
                else:
                    typer.echo("⚠️  AI generation failed, falling back to template...")
                    should_use_template = True

        if should_use_template:
            # Load template from YAML file
            try:
                from pathlib import Path as PathLib

                import yaml

                template_file = (
                    PathLib(__file__).parent.parent.parent
                    / "data"
                    / "background_template.yaml"
                )
                with open(template_file, encoding="utf-8") as f:
                    template_data = yaml.safe_load(f)

                template_content = template_data["background_template"].format(
                    module_name=path.name
                )
            except Exception as e:
                # If template loading fails, show error and exit
                typer.echo(f"Error loading template file: {e}", err=True)
                typer.echo(
                    "Template file should be at: src/goldentooth_agent/data/background_template.yaml",
                    err=True,
                )
                raise typer.Exit(1) from e

            with open(bg_file, "w", encoding="utf-8") as f:
                f.write(template_content)

            typer.echo(f"📝 Created README.bg.md template in {path.name}")
            typer.echo(
                "Please customize the template with specific details about your module."
            )
            typer.echo("💡 Tip: Use --ai flag for AI-powered background generation.")

    except Exception as e:
        typer.echo(f"Error generating background file: {e}", err=True)
        raise typer.Exit(1) from e


def _generate_all_backgrounds(
    generator: "ModuleMetadataGenerator",
    root: Path,
    force: bool,
    ai_powered: bool,
    template_only: bool,
) -> None:
    """Generate background files for all significant modules."""
    try:
        # Get all modules that should have background files
        missing_files = generator.check_background_files(root)

        if not missing_files and not force:
            # Count existing background files to show what could be regenerated
            existing_bg_files = list(root.rglob("README.bg.md"))
            existing_count = len(
                [f for f in existing_bg_files if generator._is_python_module(f.parent)]
            )

            typer.echo("✓ All modules already have README.bg.md files")
            typer.echo(f"📄 Found {existing_count} existing background files")
            typer.echo("")
            typer.echo("💡 To regenerate all background files:")
            typer.echo(
                "   goldentooth-agent dev module generate-background --force --ai"
            )
            typer.echo("")
            typer.echo("💡 To regenerate with templates:")
            typer.echo(
                "   goldentooth-agent dev module generate-background --force --template-only"
            )
            return

        # Find all significant modules (both missing and existing if force is used)
        significant_modules = []

        if force:
            # Find all Python modules in the project (exclude external dependencies)
            for python_file in root.rglob("*.py"):
                module_dir = python_file.parent

                # Skip excluded directories
                if any(
                    excluded in str(module_dir)
                    for excluded in [
                        "/old/",
                        "/.venv/",
                        "/venv/",
                        "__pycache__",
                        "/site-packages/",
                    ]
                ):
                    continue

                if generator._is_python_module(module_dir):
                    if module_dir not in significant_modules:
                        significant_modules.append(module_dir)
        else:
            # Only process modules that don't have background files
            for missing_info in missing_files:
                # Extract module name from the missing info string
                # Format is: "module_name: Missing README.bg.md file (significant module)"
                module_name = missing_info.split(":")[0].strip()

                # Search for the module directory
                found_modules = []
                for python_file in root.rglob("*.py"):
                    module_dir = python_file.parent
                    if module_dir.name == module_name and generator._is_python_module(
                        module_dir
                    ):
                        if module_dir not in found_modules:
                            found_modules.append(module_dir)

                # Add the first match found (there should typically be only one)
                if found_modules:
                    significant_modules.append(found_modules[0])

        if not significant_modules:
            typer.echo("No modules found that need background files")
            return

        typer.echo(
            f"🚀 Generating background files for {len(significant_modules)} modules..."
        )
        if ai_powered:
            typer.echo("🤖 Using AI-powered generation")
        else:
            typer.echo("📝 Using template generation")
            typer.echo(
                "💡 Add --ai flag for smarter, module-specific background generation"
            )

        generated_count = 0
        skipped_count = 0
        error_count = 0

        for module_path in significant_modules:
            bg_file = module_path / "README.bg.md"

            # Skip if file exists and force is not used
            if bg_file.exists() and not force:
                skipped_count += 1
                continue

            try:
                typer.echo(f"  📁 Processing {module_path.name}...")
                _generate_single_background(
                    generator, module_path, force, ai_powered, template_only
                )
                generated_count += 1
            except Exception as e:
                typer.echo(
                    f"  ❌ Failed to generate background for {module_path.name}: {e}"
                )
                error_count += 1

        # Summary
        typer.echo("\n✅ Background generation complete:")
        typer.echo(f"  📝 Generated: {generated_count} files")
        if skipped_count > 0:
            typer.echo(f"  ⏭️  Skipped: {skipped_count} files (already exist)")
        if error_count > 0:
            typer.echo(f"  ❌ Errors: {error_count} files")

    except Exception as e:
        typer.echo(f"Error generating background files: {e}", err=True)
        raise typer.Exit(1) from e


def _generate_ai_background_content(analysis_data: dict[str, Any]) -> str:
    """Generate AI-powered background content based on module analysis.

    Args:
        analysis_data: Analysis results from analyze_module_for_background

    Returns:
        Generated background content as markdown string
    """
    # TODO: Implement actual AI-powered analysis here
    # For now, fall back to template-based generation
    # This is where we would integrate with Claude API or similar
    # to generate intelligent background content based on analysis_data

    # Extract module name for template
    module_name = analysis_data.get("module_name", "Unknown")

    # Load template from external YAML file
    template_file = (
        Path(__file__).parent.parent.parent / "data" / "background_template.yaml"
    )
    with open(template_file, encoding="utf-8") as f:
        template_data = yaml.safe_load(f)

    # Generate content using template
    template_content = str(template_data["background_template"]).format(
        module_name=module_name
    )

    return template_content
