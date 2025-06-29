#!/usr/bin/env python3
"""
Check if modules are ready for extraction by verifying tests pass.
This implements the "tests passing = ready to split" philosophy.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_module_tests(module_name: str) -> dict[str, any]:
    """Check if tests pass for a specific module."""

    print(f"\n🔍 Checking {module_name} module...")

    results = {
        "module": module_name,
        "tests_pass": False,
        "type_check_pass": False,
        "has_readme": False,
        "test_output": "",
        "type_output": "",
        "ready_for_extraction": False,
    }

    # Check if README exists
    readme_path = Path(f"src/goldentooth_agent/core/{module_name}/README.md")
    results["has_readme"] = readme_path.exists()

    # Run tests for this module
    test_path = f"tests/core/{module_name}/"
    if Path(test_path).exists():
        print(f"  📋 Running tests for {module_name}...")
        success, output = run_command(
            ["poetry", "run", "pytest", test_path, "-v", "--tb=short"]
        )
        results["tests_pass"] = success
        results["test_output"] = output

        if success:
            print(f"  ✅ Tests pass for {module_name}")
        else:
            print(f"  ❌ Tests fail for {module_name}")
    else:
        print(f"  ⚠️  No test directory found for {module_name}")
        results["tests_pass"] = True  # Assume OK if no tests

    # Run type checking for this module
    print(f"  🔍 Type checking {module_name}...")
    success, output = run_command(
        [
            "poetry",
            "run",
            "mypy",
            f"src/goldentooth_agent/core/{module_name}/",
            "--strict",
        ]
    )
    results["type_check_pass"] = success
    results["type_output"] = output

    if success:
        print(f"  ✅ Type checking passes for {module_name}")
    else:
        print(f"  ⚠️  Type checking issues for {module_name}")

    # Determine if ready for extraction
    results["ready_for_extraction"] = (
        results["tests_pass"]
        and results["has_readme"]
        # Note: We don't require perfect type checking to proceed
    )

    if results["ready_for_extraction"]:
        print(f"  🎯 {module_name} is READY for extraction")
    else:
        print(f"  🔧 {module_name} needs work before extraction")

    return results


def main():
    """Check extraction readiness for all major modules."""

    print("🚀 Checking Module Extraction Readiness")
    print("=" * 50)

    modules_to_check = [
        "flow",
        "rag",
        "embeddings",
        "context",
        "flow_agent",
        "llm",
        "document_store",
        "background_loop",
        "util",
        "paths",
    ]

    results = []

    for module in modules_to_check:
        module_result = check_module_tests(module)
        results.append(module_result)

    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)

    ready_count = sum(1 for r in results if r["ready_for_extraction"])
    total_count = len(results)

    print(f"Ready for extraction: {ready_count}/{total_count}")
    print()

    for result in results:
        status = "🎯 READY" if result["ready_for_extraction"] else "🔧 NEEDS WORK"
        tests = "✅" if result["tests_pass"] else "❌"
        types = "✅" if result["type_check_pass"] else "⚠️ "
        readme = "✅" if result["has_readme"] else "❌"

        print(
            f"{status:12} {result['module']:15} Tests:{tests} Types:{types} README:{readme}"
        )

    # Next steps
    print("\n🎯 NEXT STEPS")
    print("-" * 20)

    ready_modules = [r["module"] for r in results if r["ready_for_extraction"]]
    needs_work = [r["module"] for r in results if not r["ready_for_extraction"]]

    if ready_modules:
        print(f"✅ Ready to extract: {', '.join(ready_modules)}")
        print(f"   Suggested order: {ready_modules[0]} (start with this one)")

    if needs_work:
        print(f"🔧 Need attention: {', '.join(needs_work)}")
        for result in results:
            if not result["ready_for_extraction"]:
                issues = []
                if not result["tests_pass"]:
                    issues.append("fix failing tests")
                if not result["has_readme"]:
                    issues.append("create README.md")
                print(f"   {result['module']}: {', '.join(issues)}")

    return 0 if ready_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
