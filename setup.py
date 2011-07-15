from setuptools import setup, find_packages

setup(
    name='django-obit-desk',
    author='John Heasly',
    url='http://github.com/jheasly/django-obit-desk/tree',
    download_url='http://github.com/jheasly/django-obit-desk/downloads',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web  Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ],
)