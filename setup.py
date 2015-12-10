#coding:utf-8
import os

from setuptools import setup, find_packages
from antispam import __version__


def read(fname):
    try:
        import pypandoc
        return pypandoc.convert(os.path.join(os.path.dirname(__file__), fname), 'rst')
    except (IOError, ImportError):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "antispam",
    version = __version__,
    keywords = ('spam', 'filter', 'antispam'),

    packages = find_packages(),
    include_package_data = True,

    package_data = {
        'antispam' : [ './antispam/model.dat' ]
    },
    install_requires = [],
    author = "Dinever",
    author_email = 'dingpeixuan911@gmail.com',
    url = "http://github.com/dinever/antispam",
    description = "Bayesian anti-spam classifier written in Python.",
    long_description = read('README.md'),
    license = "MIT License",
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
