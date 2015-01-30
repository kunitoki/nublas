from setuptools import setup, find_packages
from pip.req import parse_requirements

from nublas import __author__, __version__, __license__, __email__

setup(
    name='nublas',
    version=__version__,
    license=__license__,
    url='https://github.com/kunitoki/nublas',
    download_url='https://pypi.python.org/pypi/nublas',
    author=__author__,
    author_email=__email__,
    description='Constituent Relationship Management and Content Management system solution, built for non-profit and governmental groups.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[str(r.req) for r in parse_requirements('requirements.txt')],
    keywords=[
        'django',
        'crm',
        'cms',
        'no-profit',
        'civil',
        'association',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Environment :: Web Environment',
        'Topic :: Software Development',
    ]
)
