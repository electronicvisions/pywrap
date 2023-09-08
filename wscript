#!/usr/bin/env python
from os import environ

from waflib import Logs


def bss1_only_dependencies(ctx):
    """Dependencies only used within the BSS-1 software stack."""
    if ctx.options.with_pywrap_bindings:
        ctx('pygccxml')
        ctx('pyplusplus')
        ctx('pyublas')


def depends(ctx):
    if "wafer" in environ.get("SINGULARITY_APPNAME", "").lower():
        bss1_only_dependencies(ctx)


def options(opt):
    hopts = opt.add_option_group('Python bindings options')
    hopts.add_withoption('pywrap-bindings', default=True,
                         help='Toggle the generation and build of python'
                              'bindings (only available for Python2)')

    opt.load('compiler_cxx')
    opt.load('python')
    opt.load('pytest')
    opt.load('boost')

    # cannot decide if not needed (py2vs3 checks only run in configure)
    opt.load('pypp')


def configure(cfg):
    cfg.env.build_python_bindings = cfg.options.with_pywrap_bindings

    cfg.load('compiler_cxx')

    if cfg.env.build_python_bindings:
        cfg.load('python')
        cfg.check_python_version(minver=(2, 6))
        cfg.check_python_headers()
        cfg.load('pytest')

    cfg.load('boost')

    cfg.find_program('gccxml', var='GCCXML', mandatory=False)
    if not cfg.env.GCCXML:
        Logs.warn("gccxml not found, disabling pywrap/py++/pygccxml-based Python wrapper generation")
        cfg.env.build_python_bindings = False
        cfg.options.with_pywrap_bindings = False

    if cfg.env.build_python_bindings:
        cfg.load('pypp')
        cfg.find_program('gccxml')
        cfg.check_boost(
            lib='serialization python',
            uselib_store='BOOST_PYWRAP')

        cfg.pypp_add_module_path(cfg.path.abspath())
        cfg.pypp_add_module_dependency('pywrap')
        cfg.pypp_add_use('pywrap', 'BOOST_PYWRAP')
        cfg.env.LIB_PYWRAP = cfg.env.LIB_PYEMBED
        cfg.check_cxx(lib='gomp', cxxflags='-fopenmp', uselib_store='OPENMP4PYWRAP')

    # non-py++ stuff
    cfg.check_cxx(mandatory=True,
                  header_name='cereal/cereal.hpp')


def build(bld):
    bld.install_files(
        dest = '${PREFIX}/include',
        files = bld.path.ant_glob('src/pywrap/**/*.(h|hpp)'),
        name = 'pywrap_header',
        relative_trick = True,
        relative_base = bld.path.find_dir("src")
    )

    bld(
        target          = "pywrap_inc",
        export_includes = [ 'src' ],
        depends_on = 'pywrap_header'
    )

    if bld.env.build_python_bindings:
        build_pywrap(bld)
    else:
        bld(
            target          = "pywrap",
            export_includes = [ 'src' ],
        )

def build_pywrap(bld):
    bld(
        target          = 'pywrapsupport',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/support/pywrapsupport.cpp',
        use             = [ 'pywrap_inc', 'pyublas', 'BOOST_PYWRAP' ],
    )

    bld(
        target          = "pywrap",
        features        = 'cxx cxxshlib pyembed',
        source          = bld.path.ant_glob('src/pywrap/*.cpp'),
        use             = ['pywrap_inc', 'pywrapsupport', 'PYWRAP', 'ZTL'], # propagate python dependency
    )

    bld(
        target          = 'pywraptestmodule',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/test/pywraptest.cpp',
        use             = [ 'pywrap' ],
    )

    bld(
        target         = 'pywrapstdvector',
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS',
        use            = ['pywrap'],
        headers        = 'src/support/pywrapstdvector.h',
        script         = 'src/support/pywrapstdvector.py',
    )

    bld(
        target         = "pywraptestpypp",
        module         = "pywraptestpypp",
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS __STRICT_ANSI__',
        script         = 'src/test/pypp/generate.py',
        use            = ['pywrap', 'pywrapstdvector'],
        headers        = bld.path.ant_glob("src/test/pypp/*.hpp"),
        source         = bld.path.ant_glob("src/test/pypp/*.cpp"),
    )

    bld(
        name            = "pywraptest",
        tests           = ['src/test/pywraptest.py'],
        features        = 'use pytest',
        use             = 'pywraptestmodule pywraptestpypp pyublas',
        install_path    = '${PREFIX}/bin/tests',
    )

    bld(
        target         = "convertertestmodule",
        module         = "convertertestmodule",
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS __STRICT_ANSI__',
        script         = 'test/converter/generate.py',
        use            = ['pywrap', 'pywrapstdvector', 'pyublas'],
        headers        = bld.path.ant_glob("test/converter/*.h"),
    )

    bld(
        name            = "test_pywrap_converter",
        tests           = ['test/converter/test_pywrap_converter.py'],
        features        = 'use pytest',
        use             = 'convertertestmodule pywraptestpypp pyublas',
        install_path    = '${PREFIX}/bin/tests',
    )

    bld(
        target         = "namespace_utiltestmodule",
        module         = "namespace_utiltestmodule",
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS __STRICT_ANSI__',
        script         = 'test/namespace_util/generate.py',
        use            = ['pywrap'],
        headers        = bld.path.ant_glob("test/namespace_util/*.h"),
    )

    bld(
        name            = "test_pywrap_namespace_util",
        tests           = ['test/namespace_util/test_pywrap_namespace_util.py'],
        features        = 'use pytest',
        use             = 'namespace_utiltestmodule pywraptestpypp pyublas',
        install_path    = '${PREFIX}/bin/tests',
    )

    bld(
        target         = "omptestmodule",
        module         = "omptestmodule",
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS __STRICT_ANSI__',
        script         = 'test/omp_helper/generate.py',
        use            = ['pywrap', 'OPENMP4PYWRAP'],
        headers        = bld.path.ant_glob("test/omp_helper/*.h"),
    )
