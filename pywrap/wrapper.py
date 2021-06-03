import os
import sys
import argparse
import logging
import tempfile

import pyplusplus

from pygccxml.parser import load_xml_generator_configuration
xml_generator_config = load_xml_generator_configuration('/fasthome/sschmitt/projects/pywrap-py3/gccxml.cfg')

class Wrapper(object):
    def __init__(self, license='//greetings earthling', cpp_revision=201103):
        self.license = license

        logging.basicConfig(level=logging.INFO)

        parser = argparse.ArgumentParser(description='Generate Python Bindings')
        parser.add_argument('-I', '--include', dest='includes', action='append')
        parser.add_argument('-D', '--define', dest='defines', action='append')
        parser.add_argument('-o', '--output_dir', dest='output_dir', action='store')
        parser.add_argument('-M', '--module_name', dest='module_name', action='store')
        parser.add_argument('--dep_module', dest='dep_modules', action='append', default=[])
        parser.add_argument('--decl_db', dest='decl_dbs', action='append', default=[])
        parser.add_argument('sources', nargs='+')
        self.args = parser.parse_args()

        xml_generator_config.include_paths = self.args.includes
        xml_generator_config.define_symbols = self.args.defines

        self.mb = pyplusplus.module_builder.module_builder_t(
            self.args.sources,
            working_directory=os.path.abspath(os.path.curdir),
            indexing_suite_version=2,
            xml_generator_config=xml_generator_config
            #cplusplus_revision=cpp_revision
            )

        self.number_of_files = -1

        try:
            os.makedirs(self.args.output_dir)
        except OSError:
            pass

        with open(os.path.join(self.args.output_dir, 'generate.sh'), 'w') as f:
            f.writelines([
                '#!/bin/sh\n',
                'export PYTHONPATH="{}"\n'.format(os.pathsep.join(sys.path).replace('"', '\\"').strip(':')),
                'ipython $@ -- {}\n'.format(' \\\n'.join(sys.argv))
            ])

        for cls in self.mb.classes(allow_empty=True):
            cls.redefine_operators = False

        # Register dependency modules so that already exposed declarations are 
        # known to us
        decl_db_ext = '.exposed_decl.pypp.txt'
        for decl_db in self.args.decl_dbs:
            if not os.path.exists(decl_db):
                raise ValueError('Couldn\'t find "%s"' % decl_db)
            if not decl_db.endswith(decl_db_ext):
                raise ValueError('Invalid file ending on "%s", expected "%s"' % (decl_db, decl_db_ext))
            module = os.path.basename(decl_db)[:-len(decl_db_ext)]
            self.mb.register_module_dependency(decl_db, module)

        # Store the aliases of already exposed declarations
        self.already_exposed_aliases = [
                (d, d.alias)
                for d in self.mb.global_ns.decls()
                if d.already_exposed]

        for module in self.args.dep_modules:
            self.mb.add_registration_code('bp::import("%s");' % module, False)

    @property
    def ishell(self):
        try:
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            if sys.stdout.isatty():
                return InteractiveShellEmbed()
        except:
            pass
        return lambda *v, **k: None

    def module_name(self):
        """ get module name"""
        return self.args.module_name

    def set_number_of_files(self, number_of_files):
        """ set number of generated file

        number_of_files means:
        -1 : one file per class
        0  :   all in one file
        >0 : number of files to generate
        """
        self.number_of_files = number_of_files

    def finish(self):
        # Some aliases of already exposed declarations might got broken, here
        # we fix them
        for decl, alias in self.already_exposed_aliases:
            decl.alias = alias

        # Py++ will generate next code: def( ..., function type( function ref )
        # => safe for function overloading
        self.mb.calldefs(allow_empty=True).create_with_signature = True

        # Every declaration will be exposed at its own line
        self.mb.classes(allow_empty=True).always_expose_using_scope = True

        # Creating code creator.
        # After this step you should not modify/customize declarations.
        self.mb.build_code_creator(module_name=self.module_name())
        self.mb.code_creator.license = self.license

        # Prevent absolute includes within code.
        for d in self.args.includes:
            self.mb.code_creator.user_defined_directories.append(d)

        # Write code to files.
        if self.number_of_files < 0:
            self.mb.split_module(self.args.output_dir, use_files_sum_repository=True)
        elif self.number_of_files == 0:
            self.mb.write_module(os.path.join(self.args.output_dir, self.module_name() + ".cpp"))
        else:
            self.mb.balanced_split_module(self.args.output_dir, self.number_of_files, use_files_sum_repository=True)

# vim: ts=4 sts=4 sw=4 et
