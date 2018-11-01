from setuptools import find_packages, setup
import mp


# Read in the README for the long description on PyPI
def long_description():
    with open('README.md') as f:
        readme = f.read().splitlines()
    return readme


def get_requirements():
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements


setup(name='mp',
      version=mp.__version__,
      description=mp.__doc__,
      long_description=long_description(),
      long_description_content_type='text/markdown',
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
