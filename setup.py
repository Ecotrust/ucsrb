import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ucsrb',
    version='0.0.1',
    packages=['ucsrb'],
    include_package_data=True,
    license='TBD',
    description='Core Django Module for UCSRB Tool',
    long_description=README,
    url='http://www.ecotrust.org',
    author='Ecotrust',
    author_email='ksdev@ecotrust.org',
    classifiers=[
        'Environment :: Web Development',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: TBD',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
