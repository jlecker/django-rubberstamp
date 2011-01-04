#!/usr/bin/env python

from distutils.core import setup

import rubberstamp


setup(
    name='django-rubberstamp',
    version=rubberstamp.__version__,
    description='Permissions manager and backend for Django 1.2.',
    author='James Lecker Jr',
    author_email='james@jameslecker.com',
    url='http://github.com/jlecker/django-rubberstamp',
    packages=['rubberstamp']
)
