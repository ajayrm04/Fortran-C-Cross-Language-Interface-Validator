! Case 5: correct set_flag interface
module case_5_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_set_flag(ctx, flag) bind(c, name="set_flag")
    type(c_ptr), value :: ctx
    logical(c_bool), value :: flag
  end subroutine c_set_flag
end module case_5_interface
