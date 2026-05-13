! Case 9: integer width mismatch (int32 vs int64)
module case_9_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_large_sum(data, n, total) bind(c, name="large_sum")
    real(c_double), intent(in) :: data(*)
    integer(c_int32_t), value :: n
    real(c_double), intent(out) :: total
  end subroutine c_large_sum
end module case_9_interface
