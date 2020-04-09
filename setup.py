import codecs
import os

from setuptools import setup

import dever


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


setup(
    name='dever',
    packages=['dever'],
    package_dir={'dever': 'dever'},
    version=dever.__version__,
    license='Apache License 2.0',
    description='Manage your dev environment at ease',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author='Yaser Alnajjar',
    author_email='yaser.alnajjar@hotmail.com',
    url='https://github.com/yaseralnajjar/dever',
    # download_url='https://github.com/user/reponame/archive/v_01.tar.gz',
    keywords=['dev environment', 'docker', 'setup dev env'],
    install_requires=[
        'docker >= 4.2.0',
    ],
    entry_points={
        'console_scripts': [
            'dever=dever.core:main',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
