#!/usr/bin/env python
import os
try:
    from waflib.extras import symwaf2ic
    from waflib.extras.gtest import summary
    recurse = lambda *args: None
except ImportError:
    from gtest import summary
    assert os.getenv('SYMAP2IC_PATH'), "$SYMAP2IC_PATH not set"
    comp_dir = os.path.join(
        os.getenv('SYMAP2IC_PATH'),
        'components')

    dependencies = [
    ]
    recurse = lambda ctx: map(lambda dep: ctx.recurse(dep), dependencies)

from os.path import join

def depends(ctx):
    ctx('pygccxml')
    ctx('pyplusplus')
    ctx('pyublas')


def options(opt):
    recurse(opt)
    opt.load('g++')
    opt.load('python')
    opt.load('boost')
    opt.load('pypp')
    opt.load('pytest')


def configure(cfg):
    recurse(cfg)
    cfg.load('g++')
    cfg.load('python')
    cfg.load('boost')
    cfg.load('pypp')
    cfg.load('pytest')

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
    test_flags = {
        "cxxflags" :
            ['-ggdb3', '-std=c++0x', '-O0',
             '-Wall', '-Wextra', '-Wno-long-long', '-Wno-deprecated', '-Wno-format',
             '-fPIC', ],
        "linkflags" :
            ['-Wl,-z,defs'],
    }

    bld(
        target          = "pywrap",
#        source          = bld.path.ant_glob("pywrap/**/*.py"),
        use             = [ 'pyublas_inc', 'BOOST_PYWRAP' ],
        export_includes = [ 'src' ],
#        install_path    = 'lib/pwrap',
    )

    bld(
        target          = 'pywraptestmodule',
        features        = 'cxx cxxshlib pyext pyembed',
        source          = 'src/test/pywraptest.cpp',
        install_path    = 'lib',
        use             = [ 'pywrap' ],
        **test_flags
    )

    bld(
        tests           = ['src/test/pywraptest.py'],
        features        = 'pytest',
        use             = 'pywraptestmodule',
        install_path    = join('bin', 'tests'),
    )

