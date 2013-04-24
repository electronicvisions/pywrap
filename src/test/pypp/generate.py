#!/usr/bin/env python
from pywrap.wrapper import Wrapper
from pywrap import containers, namespaces, matchers, classes

wrap = Wrapper()
wrap.set_number_of_files(0)
module_name = wrap.module_name()
mb = wrap.mb

containers.extend_std_containers(mb)
namespaces.include_default_copy_constructors(mb)

mb.decl("get_string_vector").include()

# expose only public interfaces
namespaces.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'private')
namespaces.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'protected')

# exclude names begining with a single underscore or ending with Cpp
namespaces.exclude_by_regex(mb, ['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')

wrap.finish()
