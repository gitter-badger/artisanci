import os
import re
from setuptools import setup, find_packages

base_package = 'artisanci'

# Get the version (borrowed from SQLAlchemy)
base_path = os.path.dirname(__file__)
with open(os.path.join(base_path, 'artisan', '__init__.py')) as f:
    module_content = f.read()
    VERSION = re.compile(r'.*__version__ = \'(.*?)\'', re.S).match(module_content).group(1)
    LICENSE = re.compile(r'.*__license__ = \'(.*?)\'', re.S).match(module_content).group(1)


with open('README.rst') as f:
    readme = f.read()
    readme = readme.replace(' :beers: ', ' ')

with open('CHANGELOG.rst') as f:
    changes = f.read()


packages = [base_package + '.' + x for x in find_packages(os.path.join(base_path, base_package))]
if base_package not in packages:
    packages.append(base_package)


if __name__ == '__main__':
    setup(name='artisanci',
          description='Community powered Continuous Integration!',
          long_description='\n\n'.join([readme, changes]),
          license=LICENSE,
          url='http://artisanci.readthedocs.io',
          version=VERSION,
          author='Seth Michael Larson',
          author_email='sethmichaellarson@protonmail.com',
          maintainer='Seth Michael Larson',
          maintainer_email='sethmichaellarson@protonmail.com',
          install_requires=['colorama',
                            'distro',
                            'enum34',
                            'monotonic',
                            'requests',
                            'pendulum',
                            'psutil',
                            'pytzdata',
                            'pyvbox',
                            'PyYAML',
                            'semver',
                            'six'],
          keywords=['artisan', 'ci', 'build', 'continuous', 'integration', 'testing'],
          packages=packages,
          zip_safe=False,
          entry_points={
              'console_scripts': [
                  'artisan = artisanci.cli:main'
              ]
          },
          classifiers=['Development Status :: 2 - Pre-Alpha',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: Apache Software License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Topic :: Software Development :: Build Tools',
                       'Topic :: Software Development :: Quality Assurance',
                       'Topic :: Software Development :: Testing',
                       'Programming Language :: Python :: 2',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 3',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: Implementation :: PyPy'])
