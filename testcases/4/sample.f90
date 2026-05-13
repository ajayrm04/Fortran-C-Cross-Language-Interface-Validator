! Case 4: correct init_context interface
module case_4_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_init_context(handle) bind(c, name="init_context")
    type(c_ptr), intent(out) :: handle
  end subroutine c_init_context
end module case_4_interface
