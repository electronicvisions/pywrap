#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import classes, namespaces, matchers

wrap = Wrapper()
wrap.set_number_of_files(0)

mb = wrap.mb

cls = mb.class_('ConverterTest')
cls.include()

data_cls = mb.class_('::std::vector<double>')
classes.add_from_pyiterable_converter_to(data_cls, cls)

wrap.finish()
