#!/usr/bin/env python

from pywrap.wrapper import Wrapper
import pywrap.namespaces as ns

wrap = Wrapper()
mb = wrap.mb

# include everything from test namespace
mb.namespace("test").include()

# expose only public interfaces
ns.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'private')
ns.exclude_by_access_type(mb, ['variables', 'calldefs', 'classes'], 'protected')

# exclude names begining with a single underscore or ending with Cpp
ns.exclude_by_regex(mb, ['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')

wrap.finish()
