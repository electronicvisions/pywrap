import os
import sys
import argparse

import pyplusplus


class Wrapper(object):
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

    @property
    def ishell(self):
        from IPython.frontend.terminal.embed import InteractiveShellEmbed

        if sys.stdout.isatty():
            return InteractiveShellEmbed()
        else:
            return lambda *v, **k: None

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
