#!/usr/bin/env python

from setuptools import setup, find_packages


VERSION = '0.1'

setup(
    name='aud-gateway',
    version=VERSION,
    description='AUD gateway',
    long_description=open('README.md').read(),
    author='Ian Haywood',
    author_email='ihaywood3@gmail.com',
    maintainer='Ian Haywood',
    maintainer_email='',
    url='http://www.github.com/ihaywood3/aud-gateway',
    keywords=['DEX', 'bot', 'trading', 'api', 'blockchain'],
    packages=[
        "aud_gateway"
    ],
    classifiers=[
        'License :: OSI Approved :: GPL',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    },
    install_requires=[
        "dexbot"
    ],
    dependency_links=[
        "http://github.com/ihaywood3/DEXBot/tarball/master#egg=dexbot=0.1.0"
    ],
    include_package_data=True,
)
