/**
 * Sample C header for Fortran-C interop testing.
 * Contains some correct and some deliberately broken declarations.
 */

#ifndef MATH_INTERFACE_H
#define MATH_INTERFACE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* CORRECT: simple scalar addition */
void add_int(int a, int b, int *result);

/* BUG: C declares double return, Fortran returns float */
double dot_product(double *x, double *y, int n);

/* BUG: C only has 2 params (missing 'cols'), Fortran has 3 */
void matrix_scale(double *mat, int rows, double scale_factor);

/* CORRECT: string manipulation */
void copy_string(const char *src, char *dst, int len);

/* BUG: C takes double*, but Fortran passes val by value (not pointer) */
void fill_array(double *arr, int n, double *val);

/* CORRECT: complex multiplication */
void complex_mul(double _Complex *a, double _Complex *b, double _Complex *result);

/* BUG: C uses int64_t for n, Fortran uses int32_t */
void large_sum(double *data, int64_t n, double *total);

/* CORRECT: opaque handle */
void init_context(void **handle);

/* CORRECT: boolean flag */
void set_flag(void *ctx, bool flag);

/* BUG: parameter order is dst, src, nbytes — but Fortran says src, dst, nbytes */
void memcopy(void *dst, void *src, size_t nbytes);

#endif /* MATH_INTERFACE_H */
