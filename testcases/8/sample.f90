! Case 8: passing mode mismatch (Fortran value vs C pointer)
module case_8_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_fill_array(arr, n, val) bind(c, name="fill_array")
    real(c_double), intent(out) :: arr(*)
    integer(c_int), value :: n
    real(c_double), value :: val
  end subroutine c_fill_array
end module case_8_interface
