from setuptools import setup, find_packages

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
    install_requires=[
        "Django >= 1.7.4",
        "django-modeltranslation >= 0.8",
        "django-taggit >= 0.12.2",
        "django-widget-tweaks >= 1.3",
        "django-formaldehyde >= 0.2",
        "django-custard >= 0.8",
    ],
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
