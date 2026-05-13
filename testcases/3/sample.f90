! Case 3: correct complex_mul interface
module case_3_interface
  use iso_c_binding
  implicit none
contains
  subroutine c_complex_mul(a, b, result) bind(c, name="complex_mul")
    complex(c_double_complex), intent(in) :: a
    complex(c_double_complex), intent(in) :: b
    complex(c_double_complex), intent(out) :: result
  end subroutine c_complex_mul
end module case_3_interface
