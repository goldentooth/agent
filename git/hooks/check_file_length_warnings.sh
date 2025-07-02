#!/bin/bash
# File length warning hook - provides early warnings for large files
# Enforces proactive refactoring guidance per project guidelines
# Always exits 0 (success) to show warnings without blocking commits

set -euo pipefail  # Strict error handling per project guidelines

WARN_THRESHOLD=${FILE_LENGTH_WARN_THRESHOLD:-800}
URGENT_THRESHOLD=${FILE_LENGTH_URGENT_THRESHOLD:-900}
EXCLUDE_PATTERNS=(
  "old/"
  "docs/_build/"
  "htmlcov/"
  "*.lock"
  "*.min.js"
  "*.min.css"
)

warnings=()
urgent_warnings=()

# Process git staged files or all files if not in git context
if git rev-parse --git-dir >/dev/null 2>&1; then
  files=$(git diff --cached --name-only --diff-filter=AM 2>/dev/null || echo "")
else
  files=$(find . -type f -not -path "./.git/*" 2>/dev/null || echo "")
fi

# Exit early if no files to check
if [[ -z "$files" ]]; then
  echo "✅ File length warnings: No files to check"
  exit 0
fi

for file in $files; do
  # Skip if file doesn't exist (deleted files)
  [[ ! -f "$file" ]] && continue

  # Apply exclusion patterns
  skip=false
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    if [[ "$file" == $pattern* ]]; then
      skip=true
      break
    fi
  done
  [[ "$skip" == true ]] && continue

  # Count lines and categorize warnings
  line_count=$(wc -l < "$file" 2>/dev/null || echo 0)

  if (( line_count >= URGENT_THRESHOLD )); then
    urgent_warnings+=("$file:$line_count")
  elif (( line_count >= WARN_THRESHOLD )); then
    warnings+=("$file:$line_count")
  fi
done

# Function to get file extension for specific guidance
get_file_extension() {
  echo "${1##*.}"
}

# Function to provide refactoring guidance based on file type
get_refactoring_guidance() {
  local file="$1"
  local ext=$(get_file_extension "$file")

  case "$ext" in
    "py")
      echo "  💡 Python refactoring strategies:"
      echo "     • Extract large functions/classes into separate modules"
      echo "     • Split into domain-specific files (models, utils, services)"
      echo "     • Move constants/config to dedicated files"
      echo "     • Consider using composition over inheritance"
      ;;
    "js"|"ts"|"jsx"|"tsx")
      echo "  💡 JavaScript/TypeScript refactoring strategies:"
      echo "     • Split components into smaller, focused files"
      echo "     • Extract utility functions and constants"
      echo "     • Separate business logic from UI components"
      echo "     • Use barrel exports for clean imports"
      ;;
    "test.py"|"spec.py"|"test_"*)
      echo "  💡 Test file refactoring strategies:"
      echo "     • Group related tests into separate test files"
      echo "     • Extract test fixtures and utilities to conftest.py"
      echo "     • Split integration and unit tests"
      echo "     • Use parameterized tests to reduce duplication"
      ;;
    *)
      echo "  💡 General refactoring strategies:"
      echo "     • Split into smaller, focused files by responsibility"
      echo "     • Extract common utilities and constants"
      echo "     • Consider modular architecture patterns"
      echo "     • Document refactoring decisions in commit messages"
      ;;
  esac
}

# Report warnings with detailed guidance
has_output=false

if [[ ${#urgent_warnings[@]} -gt 0 ]]; then
  echo "🔶 URGENT: Files approaching 1000-line limit (refactor before adding more code):"
  for warning in "${urgent_warnings[@]}"; do
    file="${warning%:*}"
    lines="${warning#*:}"
    # Clean up file path display (remove ./ prefix)
    display_file="${file#./}"
    echo "  $display_file ($lines lines - $(( 1000 - lines )) lines until violation)"
    get_refactoring_guidance "$file"
    echo
  done
  has_output=true
fi

if [[ ${#warnings[@]} -gt 0 ]]; then
  echo "⚠️  WARNING: Files growing large (consider refactoring soon):"
  for warning in "${warnings[@]}"; do
    file="${warning%:*}"
    lines="${warning#*:}"
    # Clean up file path display (remove ./ prefix)
    display_file="${file#./}"
    echo "  $display_file ($lines lines - $(( URGENT_THRESHOLD - lines )) lines until urgent)"
    get_refactoring_guidance "$file"
    echo
  done
  has_output=true
fi

if [[ "$has_output" == true ]]; then
  echo "📚 See .claude/guidelines/guidelines.txt commandment #4 for detailed requirements"
  echo "🎯 Goal: Keep files focused and maintainable through proactive refactoring"
else
  echo "✅ File length warnings: All files within healthy size limits"
fi

# Always exit 0 (success) to show warnings without blocking commits
exit 0
