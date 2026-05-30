#!/bin/bash
# Run all code quality checks

set -e

echo "=== Running Ruff (linting) ==="
ruff check familyplanner tests --show-fixes --exit-zero

echo ""
echo "=== Checking code format with Black ==="
black --check familyplanner tests --diff --quiet || true

echo ""
echo "=== Running Bandit (security checks) ==="
bandit -r familyplanner -ll --exit-zero

echo ""
echo "=== Running pytest ==="
pytest tests/ -q

echo ""
echo "✓ All checks complete"
