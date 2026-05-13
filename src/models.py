"""
Data models for the Fortran-C Interface Validator.
Defines the core data structures used across all modules.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class PassingMode(Enum):
    """How a parameter is passed across the language boundary."""
    VALUE = "value"
    REFERENCE = "reference"
    POINTER = "pointer"


@dataclass
class ParamInfo:
    """Describes a single function parameter."""
    name: str
    base_type: str          # normalised canonical type, e.g. "int32", "double", "void*"
    passing_mode: PassingMode
    is_array: bool = False
    intent: str = ""        # IN / OUT / INOUT / ""  (Fortran only)
    raw_fortran: str = ""
    raw_c: str = ""


@dataclass
class FunctionSig:
    """Describes a function/subroutine signature from either language."""
    name: str               # lower-case binding name
    return_type: str        # canonical return type
    params: list = field(default_factory=list)   # list[ParamInfo]
    source: str = ""
    line_no: int = 0


@dataclass
class Mismatch:
    """Describes a single detected mismatch between Fortran and C."""
    kind: str               # "return_type" | "param_count" | "param_type" | "passing_mode"
    function: str
    description: str
    fortran_value: str
    c_value: str
    param_index: Optional[int] = None
    param_name: str = ""
    severity: str = "ERROR"  # ERROR | WARNING
