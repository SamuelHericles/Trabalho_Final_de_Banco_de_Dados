#!/usr/bin/env python
# coding=utf-8
#

""" Declaração de pacotes em python.
"""

from setuptools import setup, find_packages
import teca

with open('requirements.txt') as f:
    install_requires = list(map(str.strip, f.readlines()))


setup(
    name=teca.__name__,
    version=teca.__version__,
    description="Sistema de Gerenciamento de Biblioteca",
    classifiers=[
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # Pegas as strings a partir de http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='teca databases library',
    author=teca.__author__,
    author_email=teca.__email__,
    packages=find_packages(exclude=['ez_setup', 'examples',
                                    'tests', 'docs', '__pycache__']),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'teca = teca.main:main'
        ]
    },
)
