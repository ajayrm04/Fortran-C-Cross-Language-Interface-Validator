"""
CLI entry point for the Fortran-C Interface Validator.
Handles file I/O, report formatting, and command-line arguments.

Usage:
    python -m src <fortran_file> <c_header_file> [--json]
    python src/main.py <fortran_file> <c_header_file> [--json]
"""

import sys
import json
from .fortran_parser import FortranParser
from .c_parser import CHeaderParser
from .validator import Validator


def validate_files(fortran_path: str, c_header_path: str) -> dict:
    """Read files and run the full validation pipeline."""
    with open(fortran_path, 'r') as f:
        fortran_source = f.read()
    with open(c_header_path, 'r') as f:
        c_source = f.read()

    fp = FortranParser()
    cp = CHeaderParser()

    fortran_funcs = fp.parse(fortran_source)
    c_funcs = cp.parse(c_source)

    v = Validator()
    result = v.validate(fortran_funcs, c_funcs)

    # attach parsed function details for debugging / JSON output
    result['fortran_functions'] = [
        {
            'name': f.name,
            'return_type': f.return_type,
            'params': [
                {'name': p.name, 'type': p.base_type, 'mode': p.passing_mode.value}
                for p in f.params
            ],
            'line': f.line_no,
        }
        for f in fortran_funcs
    ]
    result['c_functions'] = [
        {
            'name': f.name,
            'return_type': f.return_type,
            'params': [
                {'name': p.name, 'type': p.base_type, 'mode': p.passing_mode.value}
                for p in f.params
            ],
            'line': f.line_no,
        }
        for f in c_funcs
    ]
    return result


def print_report(result: dict):
    """Print a human-readable validation report."""
    s = result['summary']
    print(f"\n{'='*60}")
    print(f"  Fortran-C Interface Validation Report")
    print(f"{'='*60}")
    print(f"  Functions in Fortran : {s['total_fortran']}")
    print(f"  Functions in C       : {s['total_c']}")
    print(f"  Matched pairs        : {s['matched']}")
    print(f"  Clean interfaces     : {s['clean']}")
    print(f"  Errors               : {s['errors']}")
    print(f"  Warnings             : {s['warnings']}")

    if result['unmatched_fortran']:
        print(f"\n  Unmatched Fortran (no C counterpart):")
        for n in result['unmatched_fortran']:
            print(f"    - {n}")

    if result['unmatched_c']:
        print(f"\n  Unmatched C (no Fortran counterpart):")
        for n in result['unmatched_c']:
            print(f"    - {n}")

    if result['mismatches']:
        print(f"\n  Mismatches:")
        for m in result['mismatches']:
            sev = '[ERROR]' if m['severity'] == 'ERROR' else '[WARN]'
            print(f"\n  {sev} [{m['kind'].upper()}] {m['function']}")
            print(f"     {m['description']}")
            print(f"     Fortran: {m['fortran_value']}  |  C: {m['c_value']}")
    else:
        print(f"\n  [OK] All matched interfaces are compatible!")

    print(f"{'='*60}\n")


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: python -m src <fortran_file> <c_header_file> [--json]")
        sys.exit(1)

    result = validate_files(sys.argv[1], sys.argv[2])

    if '--json' in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == '__main__':
    main()
