from setuptools import setup, Extension

module = Extension('MahjongBot', sources=[
    'mahjong_wrapper.cpp',  # wrapper cpp
    'mahjong.cpp' # source code
], language='c++', extra_compile_args=["-std=c++14"])

# run `python setup.py install` for installing custom module
setup(name='MahjongBot', ext_modules=[module])
