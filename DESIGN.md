# Design Document — Fortran-C Interface Validator

## 1. Problem Statement

When Fortran code uses `BIND(C)` to interface with C libraries, the programmer manually declares function signatures on both sides. The compiler trusts these declarations — there is **no automatic cross-language type checking**. Mismatches (wrong types, wrong parameter counts, wrong passing conventions) compile cleanly but produce:

- **Segmentation faults** at runtime
- **Silent data corruption** (e.g., float↔double truncation)
- **Stack corruption** from mismatched calling conventions

This tool detects such mismatches statically, before linking or execution.

## 2. Architecture Overview

The validator follows a three-stage **Parse → Normalise → Compare** pipeline:

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Fortran .f90 │────▶│  FortranParser   │────▶│             │
│   source     │     │  (regex-based)   │     │  Canonical  │
└──────────────┘     └──────────────────┘     │  FunctionSig│
                                               │  (unified)  │──▶ Validator ──▶ Report
┌──────────────┐     ┌──────────────────┐     │             │
│  C .h header │────▶│  CHeaderParser   │────▶│             │
│   source     │     │  (regex-based)   │     └─────────────┘
└──────────────┘     └──────────────────┘
```

### Stage 1: Parsing

- **FortranParser** — Handles free-form Fortran with `&` continuation lines, extracts `BIND(C)` subroutines/functions, resolves parameter declarations from the function body.
- **CHeaderParser** — Strips comments (`//`, `/* */`) and preprocessor directives, then extracts function prototypes, handling pointer params, array params, and function pointer params.

### Stage 2: Normalisation

Both parsers normalise their language-specific types to a **canonical type system**:

| Fortran Type                | C Type          | Canonical Form    |
|-----------------------------|-----------------|-------------------|
| `integer(c_int)`            | `int`           | `int32`           |
| `real(c_double)`            | `double`        | `double`          |
| `real(c_float)`             | `float`         | `float`           |
| `integer(c_int64_t)`        | `int64_t`       | `int64`           |
| `logical(c_bool)`           | `bool`          | `bool`            |
| `type(c_ptr)`               | `void*`         | `void*`           |
| `character(kind=c_char)`    | `char`          | `char`            |
| `complex(c_double_complex)` | `double _Complex` | `double_complex` |

### Stage 3: Validation

The `Validator` class matches functions by their **binding name** (the `name=` in `BIND(C, name="...")`), then checks:

1. **Return type compatibility** — canonical types must match
2. **Parameter count** — must be equal
3. **Parameter type** — per-position canonical type match
4. **Passing mode** — Fortran `VALUE` ↔ C by-value; Fortran ref/array ↔ C pointer

## 3. Key Design Decisions

### 3.1 Regex-Based Parsing (vs. AST-Based)

**Chosen:** Regular expressions for both Fortran and C parsing.

**Rationale:**
- Zero external dependencies (no LLVM, no Clang, no `gfortran`)
- Portable — runs anywhere with Python 3.7+
- Sufficient for `BIND(C)` interfaces, which follow constrained syntactic patterns
- The subset of Fortran/C we need to parse is regular enough for regexes

**Trade-off:** Cannot handle arbitrary preprocessor macros, complex typedefs, or template-heavy C++ headers. This is acceptable because `BIND(C)` interfaces are intentionally simple.

### 3.2 Canonical Type System

Rather than comparing raw strings, we map both languages to a shared canonical type set. This:
- Eliminates superficial string differences (`integer(c_int)` vs `int`)
- Makes the comparison logic clean and extensible
- Allows future additions (e.g., `unsigned` types, complex variants)

### 3.3 Binding Name Matching

Functions are matched by their C-side name (from `BIND(C, name="...")` in Fortran). This is the actual linker symbol, making it the most reliable matching key.

## 4. Alternative Approaches Considered

### 4.1 LLVM/Clang-Based Validation

**Approach:** Use Clang's AST to parse C headers and `flang` (LLVM's Fortran frontend) to parse Fortran, then compare the generated LLVM IR.

**Pros:** Handles all C constructs (macros, typedefs, complex types); semantically precise.  
**Cons:** Requires LLVM/Clang/Flang toolchain installed; much more complex setup; overkill for `BIND(C)` which is syntactically constrained.

### 4.2 `f2py`-Based Approach

**Approach:** Use NumPy's `f2py` tool which already parses Fortran interfaces for Python wrapping.

**Pros:** Battle-tested Fortran parser.  
**Cons:** Designed for Python↔Fortran, not C↔Fortran. Would need significant adaptation; adds NumPy as a dependency.

### 4.3 Manual Inspection / Code Review

**Approach:** Developers manually ensure declarations match.

**Pros:** No tooling needed.  
**Cons:** Error-prone, does not scale, the exact problem this tool solves.

### 4.4 ISO C Binding Compiler Warnings

**Approach:** Rely on `gfortran -Wc-binding-type` or similar compiler flags.

**Pros:** Built into the compiler.  
**Cons:** Only checks Fortran-side consistency with `iso_c_binding` — does **not** cross-check against the actual C header. Mismatches between the two files remain undetected.

## 5. Limitations

- Does not handle C preprocessor macros (`#define`-based type aliases)
- Does not resolve C `typedef` chains
- Assumes one-to-one function matching by binding name
- Does not validate struct/derived-type field layouts
- Fortran `INTERFACE` blocks (without `BIND(C)`) are ignored
