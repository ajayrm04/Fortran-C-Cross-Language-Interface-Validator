#!/usr/bin/env bash
# run.sh — Run the Fortran-C Interface Validator on the sample test cases
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	echo "Usage: ./run.sh [fortran_file] [c_header] [--json]"
	echo ""
	echo "Defaults:"
	echo "  testcases/sample.f90"
	echo "  testcases/sample.h"
	exit 0
fi

FORTRAN_FILE="${1:-$SCRIPT_DIR/testcases/sample.f90}"
C_HEADER="${2:-$SCRIPT_DIR/testcases/sample.h}"

# Pass any extra flags (e.g. --json) through to the validator
shift 2 2>/dev/null || true

echo "Running: python -m src $FORTRAN_FILE $C_HEADER $@"
echo ""

cd "$SCRIPT_DIR"
python -m src "$FORTRAN_FILE" "$C_HEADER" "$@"
