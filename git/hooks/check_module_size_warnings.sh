#!/bin/bash
# Module size warning hook - provides early warnings for large modules
# Enforces proactive refactoring guidance per project guidelines
# Always exits 0 (success) to show warnings without blocking commits

set -euo pipefail  # Strict error handling per project guidelines

WARN_THRESHOLD=${MODULE_SIZE_WARN_THRESHOLD:-4000}
URGENT_THRESHOLD=${MODULE_SIZE_URGENT_THRESHOLD:-4500}
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

warnings=()
urgent_warnings=()

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

  # Categorize warnings
  if (( total_lines >= URGENT_THRESHOLD )); then
    urgent_warnings+=("$module_dir:$total_lines")
  elif (( total_lines >= WARN_THRESHOLD )); then
    warnings+=("$module_dir:$total_lines")
  fi
done < <(find_modules)

# Function to provide module refactoring guidance
get_module_refactoring_guidance() {
  local module_dir="$1"
  local lines="$2"

  echo "  💡 Module refactoring strategies:"
  echo "     • Split into smaller, focused sub-modules by domain/responsibility"
  echo "     • Extract common utilities into separate utility modules"
  echo "     • Move models/schemas to dedicated modules (models.py, schemas.py)"
  echo "     • Separate interface definitions from implementations"
  echo "     • Consider creating sub-packages for complex domains"
  echo "     • Use __init__.py files to create clean public interfaces"
  echo "     • Move constants and configuration to dedicated config modules"
}

# Report warnings with detailed guidance
has_output=false

if [[ ${#urgent_warnings[@]} -gt 0 ]]; then
  echo "🔶 URGENT: Modules approaching 5000-line limit (refactor before adding more code):"
  for warning in "${urgent_warnings[@]}"; do
    module_dir="${warning%:*}"
    lines="${warning#*:}"
    # Clean up module path display (remove ./ prefix)
    display_module="${module_dir#./}"
    echo "  $display_module ($lines lines - $(( 5000 - lines )) lines until violation)"
    get_module_refactoring_guidance "$module_dir" "$lines"
    echo
  done
  has_output=true
fi

if [[ ${#warnings[@]} -gt 0 ]]; then
  echo "⚠️  WARNING: Modules growing large (consider refactoring soon):"
  for warning in "${warnings[@]}"; do
    module_dir="${warning%:*}"
    lines="${warning#*:}"
    # Clean up module path display (remove ./ prefix)
    display_module="${module_dir#./}"
    echo "  $display_module ($lines lines - $(( URGENT_THRESHOLD - lines )) lines until urgent)"
    get_module_refactoring_guidance "$module_dir" "$lines"
    echo
  done
  has_output=true
fi

if [[ "$has_output" == true ]]; then
  echo "📚 See .claude/guidelines/guidelines.txt commandment #5 for detailed requirements"
  echo "🎯 Goal: Keep modules focused and maintainable through proactive refactoring"
else
  echo "✅ Module size warnings: All modules within healthy size limits"
fi

# Always exit 0 (success) to show warnings without blocking commits
exit 0
