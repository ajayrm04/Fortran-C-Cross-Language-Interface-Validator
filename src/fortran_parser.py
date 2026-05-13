"""
Fortran source parser.
Extracts BIND(C) function/subroutine signatures from Fortran source files.
"""

import re
from .models import ParamInfo, FunctionSig, PassingMode
from .type_mapping import normalise_fortran_type


class FortranParser:
    """Parse Fortran source for BIND(C) interface blocks and functions."""

    INTENT_RE = re.compile(r'intent\s*\(\s*(\w+)\s*\)', re.IGNORECASE)
    BIND_C_RE = re.compile(
        r'bind\s*\(\s*c\s*(?:,\s*name\s*=\s*["\']([^"\']+)["\']\s*)?\)',
        re.IGNORECASE,
    )

    def parse(self, source: str) -> list:
        """Parse Fortran source and return list of FunctionSig."""
        functions = []
        lines = source.splitlines()
        merged = self._merge_continuations(lines)

        i = 0
        while i < len(merged):
            line, orig_lineno = merged[i]
            stripped = line.strip()

            func_match = self._match_function_header(stripped)
            if func_match:
                sig, body_lines = self._extract_body(merged, i)
                if sig:
                    sig.line_no = orig_lineno
                    self._parse_params(sig, body_lines)
                    functions.append(sig)
            i += 1

        return functions

    # ── Internals ────────────────────────────────────────────────────────────

    def _merge_continuations(self, lines):
        """Merge Fortran continuation lines (&) into logical lines."""
        result = []
        buf = ""
        start_lineno = 1
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if stripped.endswith('&'):
                if not buf:
                    start_lineno = i
                buf += stripped[:-1].strip() + ' '
            else:
                if buf:
                    buf += stripped.strip()
                    result.append((buf, start_lineno))
                    buf = ""
                else:
                    result.append((stripped, i))
        if buf:
            result.append((buf, start_lineno))
        return result

    def _match_function_header(self, line: str):
        """Return match info if line is a BIND(C) function/subroutine."""
        bind_match = self.BIND_C_RE.search(line)
        if not bind_match:
            return None

        # subroutine
        sub = re.match(
            r'(?:pure\s+|elemental\s+|recursive\s+)?subroutine\s+(\w+)\s*(\([^)]*\))?\s*bind',
            line, re.IGNORECASE)
        if sub:
            return ('subroutine', sub.group(1), bind_match.group(1))

        # function
        fn = re.match(
            r'(?:[\w\s\(\)]+?\s+)?function\s+(\w+)\s*(\([^)]*\))?\s*(?:result\s*\(\w+\))?\s*bind',
            line, re.IGNORECASE)
        if fn:
            return ('function', fn.group(1), bind_match.group(1))

        return None

    def _extract_body(self, merged, start_idx):
        """Extract the full body of a function/subroutine."""
        header_line, _ = merged[start_idx]
        header = header_line.strip()

        bind_m = self.BIND_C_RE.search(header)
        c_name = bind_m.group(1) if bind_m and bind_m.group(1) else None

        is_sub = bool(re.match(
            r'(?:pure\s+|elemental\s+|recursive\s+)?subroutine\b',
            header, re.IGNORECASE))

        if is_sub:
            nm = re.search(r'subroutine\s+(\w+)', header, re.IGNORECASE)
        else:
            nm = re.search(r'function\s+(\w+)', header, re.IGNORECASE)

        if not nm:
            return None, []

        fortran_name = nm.group(1)
        binding_name = c_name if c_name else fortran_name.lower()

        # extract param list from header
        param_list = []
        pm = re.search(
            r'(?:subroutine|function)\s+\w+\s*\(([^)]*)\)',
            header, re.IGNORECASE)
        if pm:
            param_list = [p.strip() for p in pm.group(1).split(',') if p.strip()]

        # determine return type
        if is_sub:
            return_type = "void"
        else:
            rt_m = re.match(
                r'(integer(?:\([^)]+\))?|real(?:\([^)]+\))?|double\s+precision|'
                r'complex(?:\([^)]+\))?|logical(?:\([^)]+\))?|character(?:\([^)]+\))?|'
                r'type\([^)]+\))\s+function',
                header, re.IGNORECASE)
            return_type = normalise_fortran_type(rt_m.group(1)) if rt_m else "unknown"

        sig = FunctionSig(
            name=binding_name.lower(),
            return_type=return_type,
            params=[],
            source="fortran",
        )
        sig._param_names = param_list
        sig._is_sub = is_sub

        # collect body until END
        body = []
        end_re = re.compile(
            r'end\s+(?:subroutine|function)(?:\s+\w+)?$', re.IGNORECASE)
        for j in range(start_idx + 1, len(merged)):
            ln, _ = merged[j]
            body.append(ln.strip())
            if end_re.match(ln.strip()):
                break

        return sig, body

    def _parse_params(self, sig: FunctionSig, body_lines: list):
        """Parse parameter declarations from the function body."""
        decl_re = re.compile(
            r'^(integer(?:\s*\([^)]+\))?|real(?:\s*\([^)]+\))?|double\s+precision|'
            r'complex(?:\s*\([^)]+\))?|logical(?:\s*\([^)]+\))?|'
            r'character(?:\s*\([^)]+\))?|type\s*\([^)]+\))\s*'
            r'(?:,\s*intent\s*\([^)]+\))?\s*(?:,\s*value)?\s*(?:,\s*dimension\([^)]+\))?\s*'
            r'::\s*(.+)$',
            re.IGNORECASE)

        declarations = {}
        for line in body_lines:
            m = decl_re.match(line)
            if not m:
                continue
            raw_type = m.group(1).strip()
            rest = m.group(2)

            intent_m = self.INTENT_RE.search(line)
            intent = intent_m.group(1).upper() if intent_m else ""
            is_value = bool(re.search(r',\s*value', line, re.IGNORECASE))
            is_array = bool(re.search(r',\s*dimension', line, re.IGNORECASE))

            var_names = [v.strip() for v in rest.split(',')]
            for vn in var_names:
                vn_clean = vn.split('(')[0].strip()
                is_arr = is_array or ('(' in vn)
                declarations[vn_clean.lower()] = {
                    'raw_type': raw_type,
                    'intent': intent,
                    'is_value': is_value,
                    'is_array': is_arr,
                }

        # build params in declaration order
        for pname in getattr(sig, '_param_names', []):
            key = pname.lower()
            if key in declarations:
                d = declarations[key]
                canon_type = normalise_fortran_type(d['raw_type'])
                if d['is_value']:
                    mode = PassingMode.VALUE
                elif d['is_array'] or canon_type.endswith('*'):
                    mode = PassingMode.POINTER
                else:
                    mode = PassingMode.REFERENCE

                param = ParamInfo(
                    name=key,
                    base_type=canon_type,
                    passing_mode=mode,
                    is_array=d['is_array'],
                    intent=d['intent'],
                    raw_fortran=d['raw_type'],
                )
                sig.params.append(param)
