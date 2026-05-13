#ifndef CASE10_INTERFACE_H
#define CASE10_INTERFACE_H

#include <stddef.h>

/* Case 10: C order is dst, src, nbytes */
void memcopy(void *dst, void *src, size_t nbytes);

#endif /* CASE10_INTERFACE_H */
