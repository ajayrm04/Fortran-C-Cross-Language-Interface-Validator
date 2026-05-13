#!/usr/bin/env bash
# build.sh — Set up and verify the Fortran-C Interface Validator environment
set -euo pipefail

echo "========================================"
echo "  Fortran-C Interface Validator — Build"
echo "========================================"

# 1. Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌  python3 not found. Please install Python 3.7+."
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅  Python $PY_VER detected"

# 2. Verify project structure
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ERRORS=0

for f in src/validator.py testcases/sample.f90 testcases/sample.h; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
        echo "✅  Found $f"
    else
        echo "❌  Missing $f"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "❌  Build check failed — $ERRORS file(s) missing."
    exit 1
fi

echo ""
echo "✅  Build check passed. Run ./run.sh to execute the validator."
echo "========================================"
