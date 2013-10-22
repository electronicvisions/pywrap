#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import containers, namespaces, matchers

wrap = Wrapper()
wrap.set_number_of_files(0)

containers.extend_std_containers(wrap.mb)
wrap.mb.class_('_Bit_reference').include()

wrap.finish()
