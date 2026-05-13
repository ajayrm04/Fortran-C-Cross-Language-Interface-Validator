"""
Cross-language validator.
Compares Fortran and C function signatures for ABI compatibility.
"""

from .models import ParamInfo, FunctionSig, Mismatch, PassingMode


class Validator:
    """Cross-validate Fortran and C function signatures."""

    def validate(self, fortran_funcs: list, c_funcs: list) -> dict:
        """Match functions by binding name and check for mismatches."""
        mismatches = []
        matched_pairs = []
        unmatched_fortran = []
        unmatched_c = []

        c_by_name = {f.name.lower(): f for f in c_funcs}
        f_by_name = {f.name.lower(): f for f in fortran_funcs}

        matched_names = set()

        for fname, f_sig in f_by_name.items():
            if fname in c_by_name:
                matched_names.add(fname)
                c_sig = c_by_name[fname]
                pair_mismatches = self._compare(f_sig, c_sig)
                mismatches.extend(pair_mismatches)
                matched_pairs.append({
                    'name': fname,
                    'fortran_line': f_sig.line_no,
                    'c_line': c_sig.line_no,
                    'mismatch_count': len(pair_mismatches),
                })
            else:
                unmatched_fortran.append(fname)

        for cname in c_by_name:
            if cname not in matched_names:
                unmatched_c.append(cname)

        return {
            'matched_pairs': matched_pairs,
            'mismatches': [self._mismatch_to_dict(m) for m in mismatches],
            'unmatched_fortran': unmatched_fortran,
            'unmatched_c': unmatched_c,
            'summary': {
                'total_fortran': len(fortran_funcs),
                'total_c': len(c_funcs),
                'matched': len(matched_pairs),
                'errors': sum(1 for m in mismatches if m.severity == 'ERROR'),
                'warnings': sum(1 for m in mismatches if m.severity == 'WARNING'),
                'clean': len([p for p in matched_pairs if p['mismatch_count'] == 0]),
            }
        }

    # ── Comparison Logic ─────────────────────────────────────────────────────

    def _compare(self, f_sig: FunctionSig, c_sig: FunctionSig) -> list:
        """Compare a matched Fortran/C pair and return list of Mismatch."""
        issues = []

        # 1. Return type
        if not self._types_compat(f_sig.return_type, c_sig.return_type):
            issues.append(Mismatch(
                kind='return_type',
                function=f_sig.name,
                description=f"Return type mismatch for '{f_sig.name}'",
                fortran_value=f_sig.return_type,
                c_value=c_sig.return_type,
                severity='ERROR',
            ))

        # 2. Parameter count
        if len(f_sig.params) != len(c_sig.params):
            issues.append(Mismatch(
                kind='param_count',
                function=f_sig.name,
                description=(
                    f"Parameter count mismatch: "
                    f"Fortran has {len(f_sig.params)}, C has {len(c_sig.params)}"
                ),
                fortran_value=str(len(f_sig.params)),
                c_value=str(len(c_sig.params)),
                severity='ERROR',
            ))
            n = min(len(f_sig.params), len(c_sig.params))
        else:
            n = len(f_sig.params)

        # 3. Per-parameter checks
        for i in range(n):
            fp = f_sig.params[i]
            cp = c_sig.params[i]

            # Type mismatch
            if not self._types_compat(fp.base_type, cp.base_type):
                issues.append(Mismatch(
                    kind='param_type',
                    function=f_sig.name,
                    description=(
                        f"Type mismatch at param {i+1} "
                        f"(Fortran: '{fp.name}', C: '{cp.name}')"
                    ),
                    fortran_value=fp.base_type,
                    c_value=cp.base_type,
                    param_index=i,
                    param_name=f"{fp.name}/{cp.name}",
                    severity='ERROR',
                ))

            # Passing mode mismatch
            expected_c_mode = self._expected_c_mode(fp)
            if expected_c_mode != cp.passing_mode:
                issues.append(Mismatch(
                    kind='passing_mode',
                    function=f_sig.name,
                    description=(
                        f"Passing mode mismatch at param {i+1} "
                        f"(Fortran '{fp.name}' is {fp.passing_mode.value}, "
                        f"C '{cp.name}' is {cp.passing_mode.value})"
                    ),
                    fortran_value=fp.passing_mode.value,
                    c_value=cp.passing_mode.value,
                    param_index=i,
                    param_name=f"{fp.name}/{cp.name}",
                    severity='ERROR',
                ))

        return issues

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _expected_c_mode(self, fp: ParamInfo) -> PassingMode:
        """What passing mode should the C side use given the Fortran side?"""
        if fp.passing_mode == PassingMode.VALUE:
            return PassingMode.VALUE
        elif fp.is_array:
            return PassingMode.POINTER
        else:
            return PassingMode.POINTER  # Fortran pass-by-ref -> C pointer

    def _types_compat(self, a: str, b: str) -> bool:
        """Check if two canonical types are ABI-compatible."""
        if a == b:
            return True
        if a.endswith('*') and b.endswith('*'):
            if 'void' in (a, b):
                return True
            return a == b
        synonyms = [
            {'int32', 'int', 'long'},
            {'int64', 'long long'},
            {'float', 'real'},
            {'void', 'subroutine'},
            {'char', 'character'},
        ]
        for s in synonyms:
            if a in s and b in s:
                return True
        return False

    def _mismatch_to_dict(self, m: Mismatch) -> dict:
        """Convert a Mismatch dataclass to a plain dict."""
        return {
            'kind': m.kind,
            'function': m.function,
            'description': m.description,
            'fortran_value': m.fortran_value,
            'c_value': m.c_value,
            'param_index': m.param_index,
            'param_name': m.param_name,
            'severity': m.severity,
        }
