#!/bin/bash
# Script to fix missing return type annotations in CLI commands
set -e

echo "🔧 Fixing CLI command return type annotations..."

# Get all CLI command files with no-untyped-def errors
poetry run mypy src/goldentooth_agent --strict --show-error-codes --no-pretty 2>&1 | \
    grep "no-untyped-def" | \
    grep "cli/commands" | \
    while IFS=: read -r file line_num rest; do
        if [[ -f "$file" ]]; then
            echo "  Fixing CLI function in $file at line $line_num"

            # Get the function definition line
            func_line=$(sed -n "${line_num}p" "$file")

            # Add -> None to function definitions that don't have return annotations
            if [[ "$func_line" =~ def.*\):[[:space:]]*$ ]]; then
                # Replace ): with ) -> None:
                sed -i'' -e "${line_num}s/):$/) -> None:/" "$file"
            elif [[ "$func_line" =~ def.*\),[[:space:]]*$ ]]; then
                # Handle multiline function definitions
                sed -i'' -e "${line_num}s/),$/) -> None,/" "$file"
            fi
        fi
    done

echo "✅ CLI return type fixes complete!"
echo "💡 Run 'poetry run mypy src/' to verify the fixes."
