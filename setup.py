#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
# To use a consistent encoding
import codecs
import os
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

# Shortcut for building/publishing to Pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()


def parse_reqs(req_path='./requirements.txt'):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with codecs.open(req_path, 'r') as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle
                 if line.strip() and not line.startswith('#'))
        for line in lines:
            # check for nested requirements files
            if line.startswith('-r'):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            else:
                # add the line as a new requirement
                install_requires.append(line)
    return install_requires


# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):

    """Set up the py.test test runner."""

    def finalize_options(self):
        """Set options for the command line."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Execute the test runner command."""
        # Import here, because outside the required eggs aren't loaded yet
        import pytest
        sys.exit(pytest.main(self.test_args))


# Get the long description from the relevant file
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='housekeeper',

    # Versions should comply with PEP440. For a discussion on
    # single-sourcing the version across setup.py and the project code,
    # see http://packaging.python.org/en/latest/tutorial.html#version
    version='1.0.0',

    description=('Housekeeper takes care of files.'),
    long_description=long_description,
    # What does your project relate to? Separate with spaces.
    keywords='housekeeper development',
    author='Robin Andeer',
    author_email='robin.andeer@scilifelab.se',
    license='MIT',

    # The project's main homepage
    url='https://github.com/Clinical-Genomics/housekeeper',

    packages=find_packages(exclude=('tests*', 'docs', 'examples')),

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    include_package_data=True,
    zip_safe=False,

    # Although 'package_data' is the preferred approach, in some case you
    # may need to place data files outside of your packages.
    # In this case, 'data_file' will be installed into:
    # '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # Install requirements loaded from ``requirements.txt``
    install_requires=parse_reqs(),
    tests_require=[
        'pytest',
    ],
    cmdclass=dict(
        test=PyTest,
    ),

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and
    # allow pip to create the appropriate form of executable for the
    # target platform.
    entry_points={
        'console_scripts': [
            'housekeeper = housekeeper.cli:root',
        ],
        'housekeeper.subcommands.1': [
            'init = housekeeper.initiate:init',
            'add = housekeeper.pipelines.cli:add',
            'get = housekeeper.store.cli:get',
            'getsha1 = housekeeper.store.cli:getsha1',
            'postpone = housekeeper.store.cli:postpone',
            'extend = housekeeper.pipelines.cli:extend',
            'delete = housekeeper.store.cli:delete',
            'compile = housekeeper.compile.cli:compile',
            'archive = housekeeper.archive.cli:archive',
            'clean = housekeeper.store.cli:clean',
            'restore = housekeeper.compile.cli:restore',
            'ls = housekeeper.store.cli:ls',
            'migrate = housekeeper.store.cli:migrate',
            'runs = housekeeper.store.cli:runs',
            'scout = housekeeper.pipelines.cli:scout',
            'status = housekeeper.store.cli:status',
            'samples = housekeeper.store.cli:samples',
            'cases = housekeeper.store.cli:cases',
            'add-sample = housekeeper.store.cli:add_sample',
            'add-case = housekeeper.store.cli:add_case',
            'export = housekeeper.export:export',
        ],
    },

    # See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',

        'Environment :: Console',
    ],
)
