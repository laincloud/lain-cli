# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from lain_cli import __version__

ENTRY_POINTS = """
[console_scripts]
lain = lain_cli.lain:main
"""

requirements = [
    'Jinja2==2.7.3',
    'PyYAML==3.11',
    'argh==0.26.1',
    'argcomplete==0.9.0',
    'six==1.9.0',
    'websocket-client==0.32.0',
    'retrying==1.3.3',
    'docker-py==1.7.2',
    'humanfriendly==1.29',
    'paramiko==1.15.2',
    'gevent==1.0.2',
    'requests==2.6.0',
    'tabulate==0.7.5',
    'protobuf==3.0.0b3',
    'entryclient==2.2.0',
    'lain-sdk==2.2.2',
]

setup(
    name="lain_cli",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    entry_points=ENTRY_POINTS,
    install_requires=requirements,
    dependency_links=[
        'https://github.com/laincloud/entry/archive/v2.2.0.zip#egg=entryclient-2.2.0',
        'https://github.com/laincloud/lain-sdk/archive/v2.2.2.zip#egg=lain-sdk-2.2.2',
    ],
)
