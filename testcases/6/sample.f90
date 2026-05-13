! Case 6: return type mismatch (Fortran float vs C double)
module case_6_interface
  use iso_c_binding
  implicit none
contains
  real(c_float) function c_dot_product(x, y, n) bind(c, name="dot_product")
    real(c_double), intent(in) :: x(*)
    real(c_double), intent(in) :: y(*)
    integer(c_int), value :: n
  end function c_dot_product
end module case_6_interface
