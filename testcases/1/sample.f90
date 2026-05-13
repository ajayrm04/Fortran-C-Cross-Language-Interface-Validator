! Case 1: correct add_int interface
module case_1_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_add_int(a, b, result) bind(c, name="add_int")
    integer(c_int), value :: a
    integer(c_int), value :: b
    integer(c_int), intent(out) :: result
  end subroutine c_add_int
end module case_1_interface
