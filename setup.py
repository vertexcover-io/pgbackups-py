#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import os
import re

from setuptools import setup, find_packages


def get_readme():
    """Get the contents of the ``README.rst`` file as a Unicode string."""
    try:
        import pypandoc
        description = pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError):
        description = open('README.md').read()

    return description


def get_absolute_path(*args):
    """Transform relative pathnames into absolute pathnames."""
    directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directory, *args)


def get_version():
    """Get the version of `package` (by extracting it from the source code)."""
    module_path = get_absolute_path('pgbackups', '__init__.py')
    with open(module_path) as handle:
        for line in handle:
            match = re.match(r'^__version__\s*=\s*["\']([^"\']+)["\']$', line)
            if match:
                return match.group(1)
    raise Exception("Failed to extract version from %s!" % module_path)


requirements = [
    'boto3==1.4.1',
    'heroku==0.2.0',
    'ipython==5.1.0',
    'pandoc==1.0.0b2',
    'progressbar2==3.12.0',
    'requests==2.9.1',
    'six == 1.9.0',
]

test_requirements = [
]

setup(
    name='pgbackups-py',
    version=get_version(),
    description="A cli to perform a backup of postgres db on heroku and store to s3",
    long_description=get_readme(),
    author="Ritesh Kadmawala",
    author_email='ritesh@loanzen.in',
    url='https://github.com/loanzen/pgbackups-py',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['pgbackups = pgbackups.__main__:main'],
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords=['heroku', 'backups', 'postgres', 'pgbackup'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Backup',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
