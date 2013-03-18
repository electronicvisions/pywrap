#!/usr/bin/env python


def depends(ctx):
    ctx('pygccxml')
    ctx('pyplusplus')


def options(opt):
    opt.load('g++')
    opt.load('python')
    opt.load('pypp')


def configure(cfg):
    cfg.load('g++')
    cfg.load('python')
    cfg.load('pypp')

    cfg.check_python_version(minver=(2, 6))
    cfg.check_python_headers()

    cfg.pypp_add_module_path(cfg.path.abspath())


def build(bld):
    pass
