#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pyjwt[crypto]==2.4.0','orjson==3.9.15']

test_requirements = ['pyjwt[crypto]==2.4.0','orjson==3.9.15']

optional_requirements = {
    "flask": ["Flask>=1.0"],
    "fastapi": ["fastapi==0.98.0"]
}

setup(
    author="Accelbyte Analytics",
    author_email='justice-analytics-team@accelbyte.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Justice common log format for python",
    install_requires=requirements,
    extras_require=optional_requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='justice_python_common_log',
    name='justice_python_common_log',
    packages=find_packages(include=['justice_python_common_log', 'justice_python_common_log.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/AccelByte/justice-python-common-log',
    version='0.1.0',
    zip_safe=False,
)
