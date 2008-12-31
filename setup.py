#! /usr/bin/env python

from distutils.core import setup

setup(
    name = 'Bzrwc',
    version = '0.1-pre-alpha',
    description = 'Graph e.g. lines of code in bzr repositories',
    url = 'http://code.jodal.no/git/?p=bzrwc.git',
    author = 'Stein Magnus Jodal',
    author_email = 'stein.magnus@jodal.no',
    license = 'GPLv2',

    packages = ['bzrwc'],
)
