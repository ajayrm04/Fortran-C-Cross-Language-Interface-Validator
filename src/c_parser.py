"""
C header parser.
Extracts function declarations from C header files.
"""

import re
from .models import ParamInfo, PassingMode
from .type_mapping import normalise_c_type
from .models import FunctionSig


class CHeaderParser:
    """Parse C header files for function declarations."""

    def parse(self, source: str) -> list:
        """Parse C header source and return list of FunctionSig."""
        functions = []

        # strip comments and preprocessor directives
        source = re.sub(r'//[^\n]*', '', source)
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
        source = re.sub(r'#[^\n]*', '', source)

        # find function declarations: return_type func_name(params);
        decl_re = re.compile(
            r'([\w\s\*]+?)\s+(\w+)\s*\(([^)]*)\)\s*;',
            re.DOTALL)

        for m in decl_re.finditer(source):
            ret_raw = m.group(1).strip()
            fname = m.group(2).strip()
            params_raw = m.group(3).strip()

            # skip non-function keywords
            if fname in ('if', 'while', 'for', 'switch', 'return', 'struct', 'union'):
                continue
            if 'typedef' in ret_raw:
                continue

            return_type = normalise_c_type(ret_raw)
            params = self._parse_params(params_raw)
            lineno = source[:m.start()].count('\n') + 1

            sig = FunctionSig(
                name=fname.lower(),
                return_type=return_type,
                params=params,
                source="c",
                line_no=lineno,
            )
            functions.append(sig)

        return functions

    # ── Internals ────────────────────────────────────────────────────────────

    def _parse_params(self, params_raw: str) -> list:
        """Parse a C parameter list string into a list of ParamInfo."""
        if not params_raw or params_raw.strip() == 'void':
            return []

        params = []
        # Split by comma, respecting nested parentheses (function pointers)
        depth = 0
        current = ""
        for ch in params_raw:
            if ch == '(':
                depth += 1
                current += ch
            elif ch == ')':
                depth -= 1
                current += ch
            elif ch == ',' and depth == 0:
                params.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            params.append(current.strip())

        result = []
        for i, p in enumerate(params):
            p = p.strip()
            if not p:
                continue

            # function pointer: ret (*name)(args)
            fp_m = re.match(r'(.+?)\s*\(\s*\*\s*(\w+)\s*\)\s*\(', p)
            if fp_m:
                result.append(ParamInfo(
                    name=fp_m.group(2),
                    base_type='void(*)()',
                    passing_mode=PassingMode.POINTER,
                    raw_c=p,
                ))
                continue

            # array param: type name[] or type name[N]
            arr_m = re.match(r'(.+?)\s+(\w+)\s*\[', p)
            if arr_m:
                canon = normalise_c_type(arr_m.group(1))
                result.append(ParamInfo(
                    name=arr_m.group(2),
                    base_type=canon + '*',
                    passing_mode=PassingMode.POINTER,
                    is_array=True,
                    raw_c=p,
                ))
                continue

            # pointer param: type *name or type* name
            ptr_m = re.match(r'([\w\s]+?)(\*+)\s*(\w+)$', p)
            if ptr_m:
                base = normalise_c_type(ptr_m.group(1))
                stars = ptr_m.group(2)
                pname = ptr_m.group(3)
                result.append(ParamInfo(
                    name=pname,
                    base_type=base + stars,
                    passing_mode=PassingMode.POINTER,
                    raw_c=p,
                ))
                continue

            # plain: type name
            plain_m = re.match(r'([\w\s]+?)\s+(\w+)$', p)
            if plain_m:
                canon = normalise_c_type(plain_m.group(1))
                pname = plain_m.group(2)
                result.append(ParamInfo(
                    name=pname,
                    base_type=canon,
                    passing_mode=PassingMode.VALUE,
                    raw_c=p,
                ))
                continue

            # unnamed param (just a type)
            result.append(ParamInfo(
                name=f'arg{i}',
                base_type=normalise_c_type(p),
                passing_mode=PassingMode.VALUE,
                raw_c=p,
            ))

        return result
