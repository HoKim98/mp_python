from setuptools import find_packages, setup

import mp


# Read in the README for the long description on PyPI
def long_description():
    import io
    with io.open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
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
