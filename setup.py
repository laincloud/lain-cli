# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from lain_cli import __version__

ENTRY_POINTS = """
[console_scripts]
lain = lain_cli.lain:main
"""

requirements = [
    'PyYAML==3.11',
    'argh==0.26.1',
    'humanfriendly==1.29',
    'requests>=2.6.1',
    'tabulate==0.7.5',
    'entryclient==2.3.0',
    'lain-sdk>=2.3.9',
    'pytest',
]

setup(
    name="lain_cli",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    entry_points=ENTRY_POINTS,
    install_requires=requirements,
)
