! Case 2: correct copy_string interface
module case_2_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_copy_string(src, dst, len) bind(c, name="copy_string")
    character(kind=c_char), intent(in) :: src(*)
    character(kind=c_char), intent(out) :: dst(*)
    integer(c_int), value :: len
  end subroutine c_copy_string
end module case_2_interface
