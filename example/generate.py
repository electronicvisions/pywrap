#!/usr/bin/env python

from pywrap.Boilerplate import Boilerplate

bp = Boilerplate()

# include everything from test namespace
bp.mb.namespace("test").include()

# expose only public interfaces
bp.exclude_by_access_type(['variables', 'calldefs', 'classes'], 'private')
bp.exclude_by_access_type(['variables', 'calldefs', 'classes'], 'protected')

# exclude names begining with a single underscore or ending with Cpp
bp.exclude_by_regex(['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')

bp.finish()
