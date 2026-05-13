! Case 10: parameter order mismatch (src/dst swapped)
module case_10_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_memcopy(src, dst, nbytes) bind(c, name="memcopy")
    type(c_ptr), value :: src
    type(c_ptr), value :: dst
    integer(c_size_t), value :: nbytes
  end subroutine c_memcopy
end module case_10_interface
