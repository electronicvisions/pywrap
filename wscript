#!/usr/bin/env python

try:
    from waflib.extras import symwaf2ic
    from waflib.extras.gtest import summary
    recurse = lambda *args: None
except ImportError:
    from gtest import summary
    from symwaf2ic import recurse_depends
    recurse = lambda ctx: recurse_depends(depends, ctx)

def depends(ctx):
    if ctx.options.with_bindings:
        ctx('pygccxml')
        ctx('pyplusplus')
        ctx('pyublas')

def options(opt):
    hopts = opt.add_option_group('Python bindings options')
    hopts.add_withoption('bindings', default=True, help='Toggle the generation and build of python bindings')

    recurse(opt)
    opt.load('g++')
    opt.load('python')
    opt.load('boost')
    opt.load('pypp')
    opt.load('pytest')
    opt.load('post_task')

def configure(cfg):
    cfg.env.build_python_bindings = cfg.options.with_bindings
    if not cfg.env.build_python_bindings:
        return

    recurse(cfg)
    cfg.load('g++')
    cfg.load('python')
    cfg.load('boost')
    cfg.load('pypp')
    cfg.load('pytest')
    cfg.load('post_task')

    cfg.check_python_version(minver=(2, 6))
    cfg.check_python_headers()

    cfg.check_boost(
        lib='serialization python',
        uselib_store='BOOST_PYWRAP')

    cfg.pypp_add_module_path(cfg.path.abspath())
    cfg.pypp_add_module_dependency('pywrap')
    cfg.pypp_add_use('pywrap', 'BOOST_PYWRAP')


def build(bld):
    recurse(bld)

    bld(
        target          = "pywrap_inc",
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
    test_flags = {
        "cxxflags" :
            ['-ggdb3', '-std=c++0x', '-O0',
             '-Wall', '-Wextra', '-Wno-long-long', '-Wno-deprecated', '-Wno-format',
             '-fPIC', ],
        "linkflags" :
            ['-Wl,-z,defs'],
        "install_path" : '${PREFIX}/lib',
    }

    bld(
        target          = "pywrap_inc",
        export_includes = [ 'src' ],
    )

    bld(
        target          = 'pywrapsupport',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/support/pywrapsupport.cpp',
        use             = [ 'pywrap_inc', 'pyublas', 'BOOST_PYWRAP' ],
        **test_flags
    )

    bld(
        target          = "pywrap",
        features        = 'cxx cxxshlib pyembed post_task',
        source          = bld.path.ant_glob('src/pywrap/*.cpp'),
        use             = ['pywrap_inc', 'pywrapsupport'],
        post_task       = ['pywraptest'],
        install_path    = '${PREFIX}/lib',
        cxxflags=[
            '-Wall',
            '-Wextra',
            '-fPIC',
            '-std=c++0x',
        ],
        linkflags=[
            '-Wl,-z,defs'
        ])

    bld(
        target          = 'pywraptestmodule',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/test/pywraptest.cpp',
        use             = [ 'pywrap' ],
        **test_flags
    )

    bld(
        target         = 'pywrapstdvector',
        features       = 'cxx pypp cxxshlib pyext pyembed',
        gen_defines    = 'PYPLUSPLUS',
        use            = ['pywrap'],
        headers        = 'src/support/pywrapstdvector.h',
        script         = 'src/support/pywrapstdvector.py',
        **test_flags
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
        **test_flags
    )

    bld(
        name            = "pywraptest",
        tests           = ['src/test/pywraptest.py'],
        features        = 'use pytest',
        use             = 'pywraptestmodule pywraptestpypp pyublas',
        install_path    = '${PREFIX}/bin/tests',
    )

