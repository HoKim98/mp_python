try:
    from m2r import parse_from_file
    import_ok = True
except ModuleNotFoundError:
    import_ok = False

from setuptools import find_packages, setup
from mp.version import __doc__, __version__


# Read in the README for the long description on PyPI
def long_description():
    if not import_ok:
        return ''
    # (m2r) .md to .rst
    readme = parse_from_file('README.md')
    with open('README.rst', 'w') as f:
        f.write(readme)
    return readme


def get_requirements():
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements


setup(name='mp',
      version=__version__,
      description=__doc__,
      long_description=long_description(),
      url='https://github.com/kerryeon/mp',
      author='kerryeon',
      author_email='besqer996@gnu.ac.kr',
      license='MIT',
      packages=find_packages(),
      install_requires=get_requirements(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          ],
      zip_safe=False,
      platforms='any',
      )
