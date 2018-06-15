#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import classes

wrap = Wrapper()
wrap.set_number_of_files(0)

mb = wrap.mb

cls = mb.class_('OMPTest')
cls.include()
classes.add_omp_safe_virtual_functions(cls)



wrap.finish()
