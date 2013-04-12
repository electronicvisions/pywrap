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
        os.path.join(comp_dir, 'pygccxml'),
        os.path.join(comp_dir, 'pyplusplus'),
    ]
    recurse = lambda ctx: map(lambda dep: ctx.recurse(dep), dependencies)


def depends(ctx):
    ctx('pygccxml')
    ctx('pyplusplus')


def options(opt):
    recurse(opt)
    opt.load('g++')
    opt.load('python')
    opt.load('boost')
    opt.load('pypp')


def configure(cfg):
    recurse(cfg)
    cfg.load('g++')
    cfg.load('python')
    cfg.load('boost')
    cfg.load('pypp')

    cfg.check_python_version(minver=(2, 6))
    cfg.check_python_headers()

    cfg.check_boost(
        lib='serialization python',
        uselib_store='BOOST_PYWRAP')

    cfg.pypp_add_module_path(cfg.path.abspath())
    cfg.pypp_add_use('PYWRAP', 'BOOST_PYWRAP')
    cfg.env.append_unique("INCLUDES_PYWRAP", cfg.path.abspath())


def build(bld):
    recurse(bld)
