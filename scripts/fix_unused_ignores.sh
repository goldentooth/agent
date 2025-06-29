#!/bin/bash
# Simple script to remove unused type: ignore comments
set -e

echo "🔧 Removing unused type: ignore comments..."

# Get the list of files and line numbers with unused ignores
poetry run mypy src/goldentooth_agent --strict --show-error-codes --no-pretty 2>&1 | \
    grep "Unused.*type: ignore" | \
    while IFS=: read -r file line_num rest; do
        if [[ -f "$file" && "$line_num" =~ ^[0-9]+$ ]]; then
            echo "  Removing unused ignore from $file:$line_num"
            # Use sed to remove the type: ignore comment from the specific line
            # This handles various formats: # type: ignore, # type: ignore[error], etc.
            sed -i "${line_num}s/[[:space:]]*#[[:space:]]*type:[[:space:]]*ignore[^[:space:]]*.*$//" "$file"
        fi
    done

echo "✅ Removed all unused type: ignore comments!"
echo "💡 Run 'poetry run mypy src/' to verify the fixes."