import os
import re
from setuptools import setup, find_packages

base_package = 'artisan'

# Get the version (borrowed from SQLAlchemy)
base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, 'artisan', '__init__.py')) as f:
    module_content = f.read()
    VERSION = re.compile(r'.*__version__ = \'(.*?)\'', re.S).match(module_content).group(1)
    LICENSE = re.compile(r'.*__license__ = \'(.*?)\'', re.S).match(module_content).group(1)


with open('README.rst') as f:
    readme = f.read()

with open('CHANGELOG.rst') as f:
    changes = f.read()


packages = [base_package + '.' + x for x in find_packages(os.path.join(base_path, base_package))]
if base_package not in packages:
    packages.append(base_package)


if __name__ == '__main__':
    setup(
        name='artisan',
        description=('Modern, flexible, and platform-agnostic interface for '
                     'automation, continuous integration, and farm management.'),
        long_description='\n\n'.join([readme, changes]),
        license=LICENSE,
        url='http://artisan.readthedocs.io',
        version=VERSION,
        author='Seth Michael Larson',
        author_email='sethmichaellarson@protonmail.com',
        maintainer='Seth Michael Larson',
        maintainer_email='sethmichaellarson@protonmail.com',
        entry_points={'console_scripts': ['artisan = artisan.cli:cli']},
        install_requires=['click',
                          'colorama',
                          'monotonic',
                          'paramiko',
                          'picklepipe',
                          'selectors2',
                          'toml'],
        keywords=['artisan'],
        packages=packages,
        zip_safe=False,
        classifiers=['Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.4',
                     'Programming Language :: Python :: 3.5',
                     'Programming Language :: Python :: 3.6']
    )
