#!/bin/bash
# File length validation hook - fails when files exceed 1000 lines
# Enforces project guideline #4: Do not add anything to a file with more than 500 lines
# (Relaxed to 1000 lines as per user request)

set -euo pipefail  # Strict error handling per project guidelines

MAX_LINES=${FILE_LENGTH_LIMIT:-1000}
EXCLUDE_PATTERNS=(
  "old/"
  "docs/_build/"
  "htmlcov/"
  "*.lock"
  "*.min.js"
  "*.min.css"
)

exit_code=0
violations=()

# Process git staged files or all files if not in git context
if git rev-parse --git-dir >/dev/null 2>&1; then
  files=$(git diff --cached --name-only --diff-filter=AM)
else
  files=$(find . -type f -not -path "./.git/*")
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

  # Count lines and check limit
  line_count=$(wc -l < "$file" 2>/dev/null || echo 0)
  if (( line_count > MAX_LINES )); then
    violations+=("$file:$line_count")
    exit_code=1
  fi
done

# Report violations with detailed output
if [[ ${#violations[@]} -gt 0 ]]; then
  echo "❌ File length violations found (limit: $MAX_LINES lines):"
  for violation in "${violations[@]}"; do
    echo "  $violation lines"
  done
  echo
  echo "Please refactor large files into smaller, focused modules."
  echo "See .claude/guidelines/guidelines.txt commandment #4"
fi

exit $exit_code
