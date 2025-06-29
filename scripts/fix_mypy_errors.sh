#!/bin/bash
# Auto-fix script for common MyPy errors
set -e

echo "🔧 Fixing MyPy errors automatically..."

# 1. Remove unused type: ignore comments
echo "📝 Removing unused type: ignore comments..."
poetry run mypy src/goldentooth_agent --strict --show-error-codes --no-pretty 2>&1 | \
    grep "unused-ignore" | \
    while IFS=: read file line_num rest; do
        if [[ -f "$file" ]]; then
            echo "  Fixing $file:$line_num"
            # Remove type: ignore comments from the specific line
            sed -i "${line_num}s/[[:space:]]*#[[:space:]]*type:[[:space:]]*ignore[^[:space:]]*.*$//" "$file"
        fi
    done

# 2. Fix YamlStore type parameters
echo "📝 Adding type parameters to YamlStore..."
find src/ -name "*.py" -exec grep -l "YamlStore\b" {} \; | while read file; do
    if grep -q "YamlStore[^[]" "$file"; then
        echo "  Fixing $file"
        # Add [Any] to YamlStore declarations
        sed -i 's/YamlStore\b\([^[]\)/YamlStore[Any]\1/g' "$file"
        
        # Add Any import if not present
        if ! grep -q "from typing import.*Any" "$file" && ! grep -q "^from typing import Any" "$file"; then
            # Check if there's already a typing import to extend
            if grep -q "^from typing import" "$file"; then
                sed -i '/^from typing import/ s/$/, Any/' "$file"
            else
                # Add new import after existing imports
                sed -i '/^from typing import/a from typing import Any' "$file" || \
                sed -i '/^import /a from typing import Any' "$file" || \
                sed -i '1i from typing import Any' "$file"
            fi
        fi
    fi
done

# 3. Fix missing return type annotations for simple cases
echo "📝 Adding -> None return type annotations..."
find src/ -name "*.py" -exec grep -l "def.*):$" {} \; | while read file; do
    # Only fix functions that clearly don't return anything (have print, assignments, etc.)
    # This is conservative to avoid changing functions that should return something
    python3 -c "
import re
import sys

file = sys.argv[1]
with open(file, 'r') as f:
    content = f.read()

lines = content.split('\n')
modified = False

for i, line in enumerate(lines):
    # Match function definitions without return type
    if re.match(r'^[[:space:]]*def [^(]+\([^)]*\):[[:space:]]*$', line):
        # Look ahead to see if function body suggests no return value
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].startswith(' ') or lines[j].startswith('\t')):
            if any(keyword in lines[j] for keyword in ['print(', 'console.print', 'raise ', 'return$', 'return None']):
                # This looks like a function that doesn't return a value
                lines[i] = re.sub(r':[[:space:]]*$', ' -> None:', line)
                modified = True
                break
            elif 'return ' in lines[j] and 'return None' not in lines[j]:
                # This function returns something, skip it
                break
            j += 1

if modified:
    with open(file, 'w') as f:
        f.write('\n'.join(lines))
    print(f'Fixed return types in {file}')
" "$file"
done

# 4. Fix specific Callable type parameters 
echo "📝 Adding type parameters to Callable..."
find src/ -name "*.py" -exec grep -l "Callable\b" {} \; | while read file; do
    if grep -q "Callable\[" "$file"; then
        echo "  Fixing $file"
        # Fix Callable without parameters -> Callable[..., Any]
        sed -i 's/Callable\b\([^[]\)/Callable[..., Any]\1/g' "$file"
    fi
done

echo "✅ Auto-fix complete! Run 'poetry run mypy src/' to see remaining errors."
echo "💡 Remaining errors will likely need manual fixes."