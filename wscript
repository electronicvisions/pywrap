#!/usr/bin/env python

def depends(ctx):
    if ctx.options.with_pywrap_bindings:
        ctx('pygccxml')
        ctx('pyplusplus')
        ctx('pyublas')

def options(opt):
    hopts = opt.add_option_group('Python bindings options')
    hopts.add_withoption('pywrap-bindings', default=True,
            help='Toggle the generation and build of python bindings')

    opt.load('compiler_cxx')
    opt.load('python')
    opt.load('boost')
    opt.load('pypp')
    opt.load('pytest')
    opt.load('post_task')

def configure(cfg):
    cfg.load('compiler_cxx')

    cfg.env.build_python_bindings = cfg.options.with_pywrap_bindings
    if not cfg.env.build_python_bindings:
        return

    cfg.load('python')
    cfg.load('boost')
    cfg.load('pypp')
    cfg.load('pytest')
    cfg.load('post_task')

    cfg.find_program('gccxml')

    cfg.check_python_version(minver=(2, 6))
    cfg.check_python_headers()

    cfg.check_boost(
        lib='serialization python',
        cpp_standard = 'c++14',
        uselib_store='BOOST_PYWRAP')
    cfg.pypp_add_module_path(cfg.path.abspath())
    cfg.pypp_add_module_dependency('pywrap')
    cfg.pypp_add_use('pywrap', 'BOOST_PYWRAP')

    cfg.env.LIB_PYWRAP = cfg.env.LIB_PYEMBED

    cfg.check_cxx(lib='gomp', cxxflags='-fopenmp', uselib_store='OPENMP4PYWRAP')


def build(bld):
    bld(
        target          = "pywrap_inc",
        use             = [ 'pyublas_inc' ],
        export_includes = [ 'src' ],
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
        install_path    = '${PREFIX}/lib'
    )

    bld(
        target          = "pywrap",
        features        = 'cxx cxxshlib pyembed post_task',
        source          = bld.path.ant_glob('src/pywrap/*.cpp'),
        use             = ['pywrap_inc', 'pywrapsupport', 'PYWRAP'], # propagate python dependency
        post_task       = ['pywraptest'],
        install_path    = '${PREFIX}/lib'
    )

    bld(
        target          = 'pywraptestmodule',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/test/pywraptest.cpp',
        use             = [ 'pywrap' ],
        install_path    = '${PREFIX}/lib'
    )

    bld(
        target         = 'pywrapstdvector',
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS',
        use            = ['pywrap'],
        headers        = 'src/support/pywrapstdvector.h',
        script         = 'src/support/pywrapstdvector.py',
        install_path   = '${PREFIX}/lib'
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
        install_path   = '${PREFIX}/lib'
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
        install_path   = '${PREFIX}/lib'
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
        install_path   = '${PREFIX}/lib'
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
        install_path   = '${PREFIX}/lib'
    )
