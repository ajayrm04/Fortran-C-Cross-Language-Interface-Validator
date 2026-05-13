#!/usr/bin/env bash
# build.sh — Set up and verify the Fortran-C Interface Validator environment
set -euo pipefail

echo "========================================"
echo "  Fortran-C Interface Validator — Build"
echo "========================================"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    echo ""
    echo "Usage: ./build.sh [fortran_file] [c_header]"
    echo ""
    echo "Defaults:"
    echo "  testcases/sample.f90"
    echo "  testcases/sample.h"
    exit 0
fi

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

FORTRAN_FILE="${1:-$SCRIPT_DIR/testcases/sample.f90}"
C_HEADER="${2:-$SCRIPT_DIR/testcases/sample.h}"

for f in src/validator.py; do
    if [ -f "$SCRIPT_DIR/$f" ]; then
        echo "✅  Found $f"
    else
        echo "❌  Missing $f"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ -f "$FORTRAN_FILE" ]; then
    echo "✅  Found $FORTRAN_FILE"
else
    echo "❌  Missing $FORTRAN_FILE"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "$C_HEADER" ]; then
    echo "✅  Found $C_HEADER"
else
    echo "❌  Missing $C_HEADER"
    ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "❌  Build check failed — $ERRORS file(s) missing."
    exit 1
fi

echo ""
echo "✅  Build check passed. Run ./run.sh to execute the validator."
echo "========================================"
