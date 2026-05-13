"""
Fortran-C Cross-Language Interface Validator

A static analysis tool that detects ABI mismatches between
Fortran BIND(C) interfaces and C header declarations.
"""

from .models import PassingMode, ParamInfo, FunctionSig, Mismatch
from .type_mapping import normalise_fortran_type, normalise_c_type
from .fortran_parser import FortranParser
from .c_parser import CHeaderParser
from .validator import Validator

__all__ = [
    "PassingMode", "ParamInfo", "FunctionSig", "Mismatch",
    "normalise_fortran_type", "normalise_c_type",
    "FortranParser", "CHeaderParser", "Validator",
]
