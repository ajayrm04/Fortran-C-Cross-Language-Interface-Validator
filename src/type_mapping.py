"""
Type mapping and normalisation for Fortran and C types.
Maps language-specific types to a shared canonical form for comparison.
"""

import re


# ─────────────────────── Fortran → Canonical ─────────────────────────────────

FORTRAN_TO_CANONICAL = {
    # integers
    "integer(c_int)": "int32",
    "integer(c_int8_t)": "int8",
    "integer(c_int16_t)": "int16",
    "integer(c_int32_t)": "int32",
    "integer(c_int64_t)": "int64",
    "integer(c_long)": "long",
    "integer(c_long_long)": "int64",
    "integer(c_short)": "int16",
    "integer(c_size_t)": "size_t",
    "integer(c_intptr_t)": "intptr_t",
    "integer": "int32",
    # reals
    "real(c_float)": "float",
    "real(c_double)": "double",
    "real(c_long_double)": "long_double",
    "real": "float",
    "double precision": "double",
    # complex
    "complex(c_float_complex)": "float_complex",
    "complex(c_double_complex)": "double_complex",
    # logical
    "logical(c_bool)": "bool",
    "logical": "int32",   # Fortran logical is typically 4-byte
    # character
    "character(kind=c_char)": "char",
    "character(len=1,kind=c_char)": "char",
    "character(c_char)": "char",
    "character": "char",
    # void / subroutine
    "void": "void",
    # pointer types
    "type(c_ptr)": "void*",
    "type(c_funptr)": "void(*)()",
}


# ─────────────────────── C → Canonical ───────────────────────────────────────

C_TO_CANONICAL = {
    "int": "int32",
    "int8_t": "int8",
    "int16_t": "int16",
    "int32_t": "int32",
    "int64_t": "int64",
    "long": "long",
    "long long": "int64",
    "short": "int16",
    "size_t": "size_t",
    "intptr_t": "intptr_t",
    "float": "float",
    "double": "double",
    "double _Complex": "double_complex",
    "float _Complex": "float_complex",
    "long double": "long_double",
    "bool": "bool",
    "_Bool": "bool",
    "char": "char",
    "void": "void",
    "unsigned int": "uint32",
    "unsigned long": "ulong",
    "unsigned long long": "uint64",
    "unsigned short": "uint16",
    "unsigned char": "uint8",
}


POINTER_CANONICAL = {
    "char*": "char*",
    "void*": "void*",
    "int*": "int32*",
    "float*": "float*",
    "double*": "double*",
    "int32_t*": "int32*",
    "int64_t*": "int64*",
}


# ─────────────────────── Normalisation Functions ─────────────────────────────

def normalise_fortran_type(raw: str) -> str:
    """Normalise a Fortran type string to canonical form."""
    key = raw.strip().lower()
    key = re.sub(r'\s+', ' ', key)
    # exact match first
    if key in FORTRAN_TO_CANONICAL:
        return FORTRAN_TO_CANONICAL[key]
    # strip trailing dimension specs like (*)
    key2 = re.sub(r'\([\*\d,]+\)$', '', key).strip()
    if key2 in FORTRAN_TO_CANONICAL:
        return FORTRAN_TO_CANONICAL[key2]
    # partial match
    for k, v in FORTRAN_TO_CANONICAL.items():
        if key.startswith(k):
            return v
    return key  # unknown - return as-is


def normalise_c_type(raw: str) -> str:
    """Normalise a C type string to canonical form."""
    t = raw.strip()
    # strip qualifiers that don't affect ABI
    for q in ('const ', 'volatile ', 'restrict ', '__restrict__ ', '__restrict '):
        t = t.replace(q, '')
    t = re.sub(r'\s+', ' ', t).strip()

    is_ptr = t.endswith('*')
    base = t.rstrip('* ').strip()

    if base in C_TO_CANONICAL:
        canon_base = C_TO_CANONICAL[base]
    else:
        canon_base = base  # struct / typedef / unknown

    if is_ptr:
        stars = t.count('*')
        return canon_base + '*' * stars
    return canon_base
