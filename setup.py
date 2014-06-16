import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
LICENSE = open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

setup(
    name='wcdb',
    version='1.1.0',
    packages=['wcdb', 'wcdbcli', 'wcdbsearch', 'wcdbweb'],
    include_package_data=True,
    license='MIT',
    description='A Django application for storing, browsing, and searching whole-cell model predictions.',
    long_description=README,
    license=LICENSE,
    url='http://wholecelldb.stanford.edu',
    download_url='http://github.com/CovertLab/WholeCellDB',
    author='Jonathan Karr, Nolan Phillips and Markus Covert',
    author_email='wholecell@lists.stanford.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
      # 'License :: OSI Approved :: BSD License :: FreeBSD', 
        'Natural Language :: English',
      # 'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
      # 'Topic :: Scientific/Engineering :: Visualization',
    ],
)


