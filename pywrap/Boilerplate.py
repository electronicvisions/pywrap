import os
import re
import argparse

import pyplusplus
from pygccxml.declarations.matchers import (
    access_type_matcher_t, custom_matcher_t
)


class Boilerplate(object):
    def __init__(self, license='//greetings earthling'):
        self.license = license

        parser = argparse.ArgumentParser(description='Generate Python Bindings')
        parser.add_argument('-I', '--include', dest='includes', action='append')
        parser.add_argument('-D', '--define', dest='defines', action='append')
        parser.add_argument('-o', '--output_dir', dest='output_dir', action='store')
        parser.add_argument('-M', '--module_name', dest='module_name', action='store')
        parser.add_argument('sources', nargs='+')
        self.args = parser.parse_args()

        self.mb = pyplusplus.module_builder.module_builder_t(
            self.args.sources,
            working_directory=os.path.abspath(os.path.curdir),
            include_paths=self.args.includes,
            define_symbols=self.args.defines,
            indexing_suite_version=2)

    def find(self, groups, filters, allow_missing=False):
        """Yields all objects in groups ('classes', 'namespaces', ...)
        that match one of the given filters.  By default raises an error
        if a filter did not match in any group."""

        if isinstance(groups, basestring):
            groups = re.split(r'\W+', groups)

        groups = set(groups)

        for f in filters:
            matched = False

            for name in groups:
                group = getattr(self.mb.global_ns, name)
                for obj in group(f, allow_empty=True):
                    matched = True
                    yield obj

            if not (allow_missing or matched):
                raise RuntimeError(
                    'No match found for {} in [{}]'.format(
                        f, ', '.join(groups)
                    ))

    def exclude(self, groups, filters, allow_missing=False):
        """Prevents declarations that match one of the filters from being exported.
        By default raises an error if a filter did not match in any group."""

        for obj in self.find(groups, filters, allow_missing):
            obj.exclude()

    def include(self, groups, filters, allow_missing=False):
        """Includes declarations that match one of the filters.
        By default raises an error if a filter did not match in any group."""

        for obj in self.find(groups, filters, allow_missing):
            obj.include()

    def exclude_by_access_type(self, groups, t):
        """Prevents certain declarations from being exported based on their access type:
        >>> bp.exclude_by_access_type(['variables', 'calldefs', 'classes'], 'protected')
        """

        self.exclude(groups, [access_type_matcher_t(t)], True)

    def exclude_by_regex(self, groups, pattern):
        """Prevents certain declarations from being exported based on their name:
        >>> bp.exclude_by_regex(['calldefs'], r'(^_[^_])|(.*Cpp$)|(^impl$)')
        """

        regex = pattern if hasattr(pattern, 'match') else re.compile(pattern)
        member_filter = custom_matcher_t(lambda decl: regex.match(decl.name))

        self.exclude(groups, [member_filter], True)

    @property
    def ishell(self):
        from IPython.frontend.terminal.embed import InteractiveShellEmbed
        return InteractiveShellEmbed()

    def finish(self):
        # Py++ will generate next code: def( ..., function type( function ref )
        # => safe for function overloading
        self.mb.calldefs().create_with_signature = True

        # Every declaration will be exposed at its own line
        self.mb.classes().always_expose_using_scope = True

        # Creating code creator.
        # After this step you should not modify/customize declarations.
        self.mb.build_code_creator(module_name=self.args.module_name)
        self.mb.code_creator.license = self.license

        # Prevent absolute includes within code.
        for d in self.args.includes:
            self.mb.code_creator.user_defined_directories.append(d)

        # Write code to files.
        self.mb.split_module(self.args.output_dir)

# vim: ts=4 sts=4 sw=4 et
