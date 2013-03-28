#!/usr/bin/env python


def depends(ctx):
    ctx('pygccxml')
    ctx('pyplusplus')


def options(opt):
    opt.load('g++')
    opt.load('python')
    opt.load('boost')
    opt.load('pypp')


def configure(cfg):
    cfg.load('g++')
    cfg.load('python')
    cfg.load('boost')
    cfg.load('pypp')

    cfg.check_python_version(minver=(2, 6))
    cfg.check_python_headers()

    cfg.check_boost(lib='serialization python',
            uselib_store='BOOST_PYWRAP')

    cfg.pypp_add_module_path(cfg.path.abspath())
    cfg.pypp_add_use('PYWRAP', 'BOOST_PYWRAP')
    cfg.env.append_unique("INCLUDES_PYWRAP", cfg.path.abspath())

def build(bld):
    pass
