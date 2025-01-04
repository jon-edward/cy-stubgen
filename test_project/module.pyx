
module_property: int = 1


cdef class MyClass:
    cdef int x

    def __init__(self) -> None:
        """
        This class is used to test Cython stub file generation.
        """
        self.x = 0
    
    cdef int private_method(self):
        print("private_method called!")
    
    cpdef int get_x(self):
        """
        This gets the value of the internal property `x`.
        """
        return self.x
    
    cpdef set_x(self, int x):
        """
        This sets the value of the internal property `x`.
        """
        self.x = x
