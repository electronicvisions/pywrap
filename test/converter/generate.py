#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import containers

wrap = Wrapper()
wrap.set_number_of_files(0)

mb = wrap.mb

containers.extend_std_containers(mb)

cls = mb.class_('ConverterTest')
cls.include()

mb.decl('int_tag').include()
mb.decl('double_tag').include()

for cls in mb.classes():
    print(cls)

wrap.finish()
