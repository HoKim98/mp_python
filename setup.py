from m2r import parse_from_file
from setuptools import find_packages, setup

import mp


# Read in the README for the long description on PyPI
def long_description():
    # (m2r) .md to .rst
    readme = parse_from_file('README.md')
    with open('README.rst', 'w') as f:
        f.write(readme)
    return readme


setup(name='mp',
      version=mp.__version__,
      description=mp.__doc__,
      long_description=long_description(),
      url='https://github.com/kerryeon/mp',
      author='kerryeon',
      author_email='besqer996@gnu.ac.kr',
      license='MIT',
      packages=find_packages(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          ],
      zip_safe=False,
      )
