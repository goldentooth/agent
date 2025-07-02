#!/bin/bash
# Module size validation hook - fails when modules exceed 5000 lines
# Enforces project guideline #5: Do not add anything to a module with more than 5000 lines

set -euo pipefail  # Strict error handling per project guidelines

MAX_LINES=${MODULE_SIZE_LIMIT:-5000}
EXCLUDE_PATTERNS=(
  "old/"
  "docs/"
  "tests/"
  "htmlcov/"
  "__pycache__/"
  ".git/"
  ".pytest_cache/"
  "build/"
  "dist/"
)

exit_code=0
violations=()

# Function to count Python lines in a directory
count_python_lines_in_dir() {
  local dir="$1"
  local total_lines=0

  # Find all .py files in directory (not recursive) and count lines
  while IFS= read -r -d '' file; do
    if [[ -f "$file" ]]; then
      local file_lines=$(wc -l < "$file" 2>/dev/null || echo 0)
      total_lines=$((total_lines + file_lines))
    fi
  done < <(find "$dir" -maxdepth 1 -name "*.py" -type f -print0 2>/dev/null || true)

  echo "$total_lines"
}

# Function to check if directory should be excluded
should_exclude_dir() {
  local dir="$1"
  for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    if [[ "$dir" == $pattern* ]] || [[ "$dir" == *"/$pattern"* ]]; then
      return 0  # true - should exclude
    fi
  done
  return 1  # false - should not exclude
}

# Function to find modules (directories containing .py files)
find_modules() {
  # Look for directories containing .py files
  find . -type f -name "*.py" -not -path "./.git/*" | while read -r file; do
    dirname "$file"
  done | sort -u | while read -r dir; do
    # Skip if directory should be excluded
    if should_exclude_dir "$dir"; then
      continue
    fi

    # Only consider directories with multiple .py files or significant structure
    local py_count=$(find "$dir" -maxdepth 1 -name "*.py" -type f | wc -l)
    if (( py_count > 0 )); then
      echo "$dir"
    fi
  done
}

# Check each module
while IFS= read -r module_dir; do
  [[ -z "$module_dir" ]] && continue

  # Count total lines in module
  total_lines=$(count_python_lines_in_dir "$module_dir")

  # Skip modules with no Python code
  if (( total_lines == 0 )); then
    continue
  fi

  # Check if module exceeds limit
  if (( total_lines > MAX_LINES )); then
    violations+=("$module_dir:$total_lines")
    exit_code=1
  fi
done < <(find_modules)

# Report violations with detailed output
if [[ ${#violations[@]} -gt 0 ]]; then
  echo "❌ Module size violations found (limit: $MAX_LINES lines):"
  for violation in "${violations[@]}"; do
    module_dir="${violation%:*}"
    lines="${violation#*:}"
    # Clean up module path display (remove ./ prefix)
    display_module="${module_dir#./}"
    echo "  $display_module: $lines lines"
  done
  echo
  echo "Please refactor large modules into smaller, focused sub-modules."
  echo "See .claude/guidelines/guidelines.txt commandment #5"
  echo
  echo "💡 Module refactoring strategies:"
  echo "   • Split into smaller, domain-focused sub-modules"
  echo "   • Extract common utilities into separate utility modules"
  echo "   • Move models/schemas to dedicated modules"
  echo "   • Separate interface definitions from implementations"
  echo "   • Consider creating sub-packages for complex domains"
fi

exit $exit_code
