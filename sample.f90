! Sample Fortran module with BIND(C) interfaces for testing
! Some are correct, some have intentional bugs

module math_interface
  use iso_c_binding
  implicit none

contains

  ! CORRECT: simple scalar addition
  subroutine c_add_int(a, b, result) bind(c, name="add_int")
    integer(c_int), value :: a
    integer(c_int), value :: b
    integer(c_int), intent(out) :: result
  end subroutine c_add_int

  ! BUG: return type mismatch (Fortran returns real, C expects double)
  real(c_float) function c_dot_product(x, y, n) bind(c, name="dot_product")
    real(c_double), intent(in) :: x(*)
    real(c_double), intent(in) :: y(*)
    integer(c_int), value :: n
  end function c_dot_product

  ! BUG: parameter count mismatch (Fortran has 3, C has 2)
  subroutine c_matrix_scale(mat, rows, cols) bind(c, name="matrix_scale")
    real(c_double), intent(inout) :: mat(*)
    integer(c_int), value :: rows
    integer(c_int), value :: cols
  end subroutine c_matrix_scale

  ! CORRECT: string manipulation
  subroutine c_copy_string(src, dst, len) bind(c, name="copy_string")
    character(kind=c_char), intent(in) :: src(*)
    character(kind=c_char), intent(out) :: dst(*)
    integer(c_int), value :: len
  end subroutine c_copy_string

  ! BUG: passing mode mismatch (Fortran passes by value, C expects pointer)
  subroutine c_fill_array(arr, n, val) bind(c, name="fill_array")
    real(c_double), intent(out) :: arr(*)
    integer(c_int), value :: n
    real(c_double), value :: val
  end subroutine c_fill_array

  ! CORRECT: complex number operation
  subroutine c_complex_mul(a, b, result) bind(c, name="complex_mul")
    complex(c_double_complex), intent(in) :: a
    complex(c_double_complex), intent(in) :: b
    complex(c_double_complex), intent(out) :: result
  end subroutine c_complex_mul

  ! BUG: integer width mismatch (32-bit vs 64-bit)
  subroutine c_large_sum(data, n, total) bind(c, name="large_sum")
    real(c_double), intent(in) :: data(*)
    integer(c_int32_t), value :: n
    real(c_double), intent(out) :: total
  end subroutine c_large_sum

  ! CORRECT: void pointer (opaque handle)
  subroutine c_init_context(handle) bind(c, name="init_context")
    type(c_ptr), intent(out) :: handle
  end subroutine c_init_context

  ! CORRECT: logical flag
  subroutine c_set_flag(ctx, flag) bind(c, name="set_flag")
    type(c_ptr), value :: ctx
    logical(c_bool), value :: flag
  end subroutine c_set_flag

  ! BUG: parameter order swapped
  subroutine c_memcopy(src, dst, nbytes) bind(c, name="memcopy")
    type(c_ptr), value :: src
    type(c_ptr), value :: dst
    integer(c_size_t), value :: nbytes
  end subroutine c_memcopy

end module math_interface
