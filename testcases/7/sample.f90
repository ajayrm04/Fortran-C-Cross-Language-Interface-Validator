! Case 7: parameter type mismatch (int vs double)
module case_7_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_matrix_scale(mat, rows, cols) bind(c, name="matrix_scale")
    real(c_double), intent(inout) :: mat(*)
    integer(c_int), value :: rows
    integer(c_int), value :: cols
  end subroutine c_matrix_scale
end module case_7_interface
