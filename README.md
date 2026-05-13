# Fortran-C Cross-Language Interface Validator

A static analysis tool that automatically detects **ABI mismatches** between Fortran `BIND(C)` interfaces and their corresponding C header declarations. It catches bugs that compilers silently accept but cause crashes, data corruption, or silent wrong results at runtime.

## What It Does

The validator parses both Fortran source files and C headers, normalises their type systems to a common canonical form, and cross-validates every matched function signature for:

| Check                  | Example Bug Detected                                    |
|------------------------|---------------------------------------------------------|
| **Return type**        | Fortran returns `float`, C expects `double`             |
| **Parameter count**    | Fortran has 3 params, C has 2                           |
| **Parameter type**     | Fortran uses `int32_t`, C uses `int64_t`                |
| **Passing mode**       | Fortran passes by `VALUE`, C expects a pointer          |
| **Parameter order**    | Fortran says `(src, dst)`, C says `(dst, src)`          |

## Prerequisites

- **Python 3.7+** (no external dependencies — stdlib only)

## Project Structure

```
├── README.md              # This file
├── DESIGN.md              # Architecture & design decisions
├── IMPLEMENTATION.md      # LLVM-level details & internals
├── EVALUATION.md          # Metrics, comparisons & test cases
├── build.sh               # Environment check script
├── run.sh                 # Run script
├── src/
│   └── validator.py       # Core validator (743 lines)
└── testcases/
    ├── sample.f90         # Fortran test input (10 interfaces)
    └── sample.h           # C header test input (10 declarations)
```

## How to Run

### Quick Start

```bash
# 1. Verify the environment
./build.sh

# 2. Run the validator on the included test cases
./run.sh

# 3. Run a specific case folder
./build.sh testcases/1/sample.f90 testcases/1/sample.h
./run.sh testcases/1/sample.f90 testcases/1/sample.h
```

### Manual Usage

```bash
# Human-readable report
python3 src/validator.py testcases/sample.f90 testcases/sample.h

# Machine-readable JSON output
python3 src/validator.py testcases/sample.f90 testcases/sample.h --json

# Custom input files
python3 src/validator.py path/to/your_module.f90 path/to/your_header.h
```

### Sample Output

```
============================================================
  Fortran-C Interface Validation Report
============================================================
  Functions in Fortran : 10
  Functions in C       : 10
  Matched pairs        : 10
  Clean interfaces     : 5
  Errors               : 7
  Warnings             : 0

  ❌ [RETURN_TYPE] dot_product
     Return type mismatch for 'dot_product'
     Fortran: float  |  C: double

  ❌ [PARAM_COUNT] matrix_scale
     Parameter count mismatch: Fortran has 3, C has 3
     Fortran: 3  |  C: 3

  ❌ [PASSING_MODE] fill_array
     Passing mode mismatch at param 3 ...
     Fortran: value  |  C: pointer
============================================================
```

## License

This project was developed as part of the Compiler Design Lab (EL component).
