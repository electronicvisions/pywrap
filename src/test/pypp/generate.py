#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import containers, namespaces, matchers, classes, functions
from pygccxml import declarations

wrap = Wrapper()
wrap.set_number_of_files(0)
module_name = wrap.module_name()
mb = wrap.mb

containers.extend_std_containers(mb)
namespaces.include_default_copy_constructors(mb)

for c in ("KProxy", ):
    cls = mb.class_(c)
    for v in cls.variables():
        if declarations.is_reference(v.decl_type):
            v.use_make_functions = True

mb.decl("get_string_vector").include()
mb.namespace("test").include()

cl = mb.class_("RefWrap")
cl.include()
functions.convert_vector_of_references_return_type(cl.mem_fun("ints"))

for cl_name in ["ReturnOptional", "ReturnOptionalB", "ReturnOptionalC"]:
    cl = mb.class_(cl_name)
    cl.include()
    for fun in cl.member_functions():
        functions.return_optional_by_value(fun)

# expose only public interfaces
namespaces.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'private')
namespaces.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'protected')

# exclude names begining with a single underscore or ending with Cpp
namespaces.exclude_by_regex(mb, ['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')

cls = mb.class_("WithPickle")
classes.add_pickle_suite(cls)

cls = mb.class_("WithPickleCereal")
classes.add_pickle_suite(cls, serialization_framework='cereal')

wrap.finish()
