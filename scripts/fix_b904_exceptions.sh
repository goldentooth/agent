#!/bin/bash
# Script to fix B904 exception chaining errors
set -e

echo "🔧 Fixing B904 exception chaining errors..."

# Get B904 errors from ruff
poetry run ruff check src/ 2>&1 | grep "B904" | while IFS=: read -r file line_num rest; do
    if [[ -f "$file" && "$line_num" =~ ^[0-9]+$ ]]; then
        echo "  Fixing B904 in $file at line $line_num"

        # Get the line content
        line_content=$(sed -n "${line_num}p" "$file")

        # If it's a raise typer.Exit(1), add from None since we don't want to chain CLI exits
        if [[ "$line_content" =~ "raise typer.Exit" ]]; then
            sed -i'' -e "${line_num}s/raise typer\.Exit(\([^)]*\))/raise typer.Exit(\1) from None/" "$file"
        # For other exceptions, add from err or from None as appropriate
        elif [[ "$line_content" =~ "raise.*Error" ]]; then
            # If there's an exception variable in scope, chain it
            if grep -B5 "^.*${line_num}:" "$file" | grep -q "except.*as [a-zA-Z_]"; then
                # Extract the exception variable name
                exc_var=$(grep -B5 "^.*${line_num}:" "$file" | grep "except.*as" | tail -1 | sed 's/.*as \([a-zA-Z_][a-zA-Z0-9_]*\).*/\1/')
                sed -i'' -e "${line_num}s/raise \(.*\)$/raise \1 from ${exc_var}/" "$file"
            else
                sed -i'' -e "${line_num}s/raise \(.*\)$/raise \1 from None/" "$file"
            fi
        else
            # Generic case - add from None for CLI commands
            sed -i'' -e "${line_num}s/raise \(.*\)$/raise \1 from None/" "$file"
        fi
    fi
done

echo "✅ B904 exception chaining fixes complete!"
echo "💡 Run 'poetry run ruff check src/' to verify the fixes."
