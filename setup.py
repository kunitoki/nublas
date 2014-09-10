from setuptools import setup

from nublas import __version__

setup(
    name='nublas',
    version=__version__,
    license='MIT',
    url='https://github.com/kunitoki/nublas',
    author='Lucio Asnaghi (aka kunitoki)',
    author_email='kunitoki@gmail.com',
    description='Constituent Relationship Management and Content Management system solution, built for non-profit and governmental groups.',
    long_description=open('README.rst').read(),
    packages=[
        'nublas',
        'nublas.tests',
    ],
    package_data={
        'nublas': ['templates/nublas/admin/*.html'],
    },
    install_requires=[
        "Django >= 1.7",
    ],
    keywords=[
        'django',
        'crm',
        'cms',
        'non-profit',
        'civi',
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
