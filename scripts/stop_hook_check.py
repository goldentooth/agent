#!/usr/bin/env python3
"""
Stop hook script that runs pre-commit hooks and conditionally commits changes.
Only commits if there are actual changes in the repository.
"""

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path


def log_message(message: str, level: str = "INFO"):
    """Log a message with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] STOP_HOOK: {message}", flush=True)


def run_command(
    cmd: list[str], capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    cmd_str = " ".join(cmd)
    log_message(f"Running command: {cmd_str}")

    result = subprocess.run(
        cmd, capture_output=capture_output, text=True, cwd=Path(__file__).parent.parent
    )

    log_message(f"Command '{cmd_str}' finished with exit code: {result.returncode}")
    if result.stdout:
        log_message(f"STDOUT: {result.stdout[:500]}...")
    if result.stderr:
        log_message(f"STDERR: {result.stderr[:500]}...")

    return result


def has_git_changes() -> bool:
    """Check if there are any changes in the git repository."""
    log_message("Checking for git changes...")

    # Check for staged changes
    log_message("Checking for staged changes...")
    result = run_command(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        log_message("Found staged changes")
        return True
    log_message("No staged changes found")

    # Check for unstaged changes
    log_message("Checking for unstaged changes...")
    result = run_command(["git", "diff", "--quiet"])
    if result.returncode != 0:
        log_message("Found unstaged changes")
        return True
    log_message("No unstaged changes found")

    # Check for untracked files
    log_message("Checking for untracked files...")
    result = run_command(["git", "status", "--porcelain"])
    if result.stdout.strip():
        log_message(f"Found untracked files: {result.stdout.strip()}")
        return True
    log_message("No untracked files found")

    log_message("No git changes detected")
    return False


def run_precommit_hooks() -> tuple[bool, str]:
    """Run pre-commit hooks and return success status and output."""
    log_message("🔍 Running pre-commit hooks...")

    result = run_command(["poetry", "run", "pre-commit", "run", "--all-files"])

    if result.returncode == 0:
        log_message("✅ All pre-commit hooks passed!")
        return True, result.stdout
    else:
        log_message("❌ Pre-commit hooks failed!")
        return False, result.stdout + "\n" + result.stderr


def stage_and_commit_changes() -> tuple[bool, str]:
    """Stage all changes and commit them."""
    log_message("📝 Staging all changes...")

    # Stage all changes
    stage_result = run_command(["git", "add", "."])
    if stage_result.returncode != 0:
        log_message(f"Failed to stage changes: {stage_result.stderr}", "ERROR")
        return False, f"Failed to stage changes: {stage_result.stderr}"
    log_message("Successfully staged all changes")

    # Create commit with Claude Code attribution
    commit_msg = """Apply code changes and formatting

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    log_message("💾 Committing changes...")
    commit_result = run_command(["git", "commit", "-m", commit_msg])

    if commit_result.returncode == 0:
        log_message("✅ Changes committed successfully!")
        return True, "Changes committed successfully"
    else:
        log_message(f"Failed to commit: {commit_result.stderr}", "ERROR")
        return False, f"Failed to commit: {commit_result.stderr}"


def main():
    """Main hook logic."""
    log_message("🚀 STOP HOOK STARTED")
    log_message(f"Python executable: {sys.executable}")
    log_message(f"Working directory: {os.getcwd()}")
    log_message(f"Script location: {Path(__file__).absolute()}")
    log_message(f"Project root: {Path(__file__).parent.parent}")

    try:
        # Try to read hook input
        log_message("Attempting to read hook input from stdin...")
        try:
            hook_input = json.load(sys.stdin)
            log_message(f"Hook input received: {json.dumps(hook_input, indent=2)}")
        except Exception as stdin_error:
            log_message(
                f"Failed to read stdin (this might be normal): {stdin_error}", "WARN"
            )
            hook_input = {}

        log_message("🚀 Stop hook: Checking repository status...")

        # Check if there are any changes
        if not has_git_changes():
            log_message(
                "ℹ️  No changes detected in repository - skipping pre-commit and commit"
            )
            return

        log_message("📂 Changes detected in repository")

        # Run pre-commit hooks
        hooks_passed, hooks_output = run_precommit_hooks()

        if not hooks_passed:
            # Block Claude from stopping and provide feedback
            response = {
                "decision": "block",
                "reason": f"Pre-commit hooks failed. Please fix the following issues:\n\n{hooks_output}\n\nRun the pre-commit hooks again or fix the issues manually.",
            }
            log_message(f"Blocking Claude due to hook failures: {response}", "ERROR")
            print(json.dumps(response))
            return

        # Pre-commit hooks passed, now commit the changes
        commit_success, commit_message = stage_and_commit_changes()

        if not commit_success:
            # Block Claude and report commit failure
            response = {
                "decision": "block",
                "reason": f"Pre-commit hooks passed but commit failed: {commit_message}",
            }
            log_message(f"Blocking Claude due to commit failure: {response}", "ERROR")
            print(json.dumps(response))
            return

        # Everything succeeded
        log_message("🎉 All checks passed and changes committed!")

    except Exception as e:
        # Block Claude and report the error
        log_message(f"Stop hook failed with exception: {str(e)}", "ERROR")
        import traceback

        log_message(f"Traceback: {traceback.format_exc()}", "ERROR")

        response = {
            "decision": "block",
            "reason": f"Stop hook failed with error: {str(e)}",
        }
        log_message(f"Blocking Claude due to exception: {response}", "ERROR")
        print(json.dumps(response))

    log_message("🏁 STOP HOOK FINISHED")


if __name__ == "__main__":
    main()
