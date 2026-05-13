#ifndef CASE9_INTERFACE_H
#define CASE9_INTERFACE_H

#include <stdint.h>

/* Case 9: C uses int64_t for n, Fortran uses int32_t */
void large_sum(double *data, int64_t n, double *total);

#endif /* CASE9_INTERFACE_H */
