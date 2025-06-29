#!/bin/bash
# Script to fix missing type parameters for generic types
set -e

echo "🔧 Fixing missing type parameters..."

# Get current MyPy output to analyze type-arg errors
MYPY_OUTPUT=$(poetry run mypy src/goldentooth_agent --strict --show-error-codes --no-pretty 2>&1 || true)

# 1. Fix YamlStore type parameters
echo "📝 Adding type parameters to YamlStore..."
echo "$MYPY_OUTPUT" | grep "YamlStore.*type-arg" | while IFS=: read -r file line_num rest; do
    if [[ -f "$file" ]]; then
        echo "  Fixing YamlStore in $file"
        # Add [Any] to YamlStore declarations, but be careful not to double-add
        sed -i'' -e 's/YamlStore\b\([^[]\)/YamlStore[Any]\1/g' "$file"

        # Add Any import if not present
        if ! grep -q "from typing import.*Any" "$file" && ! grep -q "^[[:space:]]*Any[[:space:]]*," "$file"; then
            # Check if there's already a typing import to extend
            if grep -q "^from typing import" "$file"; then
                # Extend existing import - simpler approach
                sed -i'' -e '/^from typing import/s/$/, Any/' "$file"
            else
                # Add new import - find a good place after other imports
                if grep -q "^from \.\." "$file"; then
                    sed -i'' -e '/^from \.\./a\
from typing import Any' "$file"
                elif grep -q "^from antidote" "$file"; then
                    sed -i'' -e '/^from antidote/a\
from typing import Any' "$file"
                else
                    sed -i'' -e '1i\
from typing import Any\
' "$file"
                fi
            fi
        fi
    fi
done

# 2. Fix Callable type parameters
echo "📝 Adding type parameters to Callable..."
echo "$MYPY_OUTPUT" | grep "Callable.*type-arg" | while IFS=: read -r file line_num rest; do
    if [[ -f "$file" ]]; then
        echo "  Fixing Callable in $file"
        # Add [..., Any] to Callable declarations
        sed -i'' -e 's/Callable\b\([^[]\)/Callable[..., Any]\1/g' "$file"
    fi
done

# 3. Fix other common generic types
echo "📝 Adding type parameters to other generic types..."
echo "$MYPY_OUTPUT" | grep -E "(List|Dict|Set|Tuple).*type-arg" | while IFS=: read -r file line_num rest; do
    if [[ -f "$file" ]]; then
        echo "  Fixing generic types in $file"
        # Fix common cases - be conservative
        sed -i'' -e 's/\bList\b\([^[]\)/List[Any]\1/g' "$file"
        sed -i'' -e 's/\bDict\b\([^[]\)/Dict[str, Any]\1/g' "$file"
        sed -i'' -e 's/\bSet\b\([^[]\)/Set[Any]\1/g' "$file"
    fi
done

echo "✅ Type parameter fixes complete!"
echo "💡 Run 'poetry run mypy src/' to see remaining errors."
