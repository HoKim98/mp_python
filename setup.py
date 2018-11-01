from setuptools import find_packages, setup
from mp import version


# Read in the README for the long description on PyPI
def long_description():
    with open('README.md') as f:
        readme = f.read()
    return readme


def get_requirements():
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements


setup(
    # Basic Description
    name=version.__name__,
    version=version.__version__,
    description=version.__doc__,
    long_description=long_description(),
    long_description_content_type='text/markdown',
    # Author Information
    author=version.__author__,
    author_email=version.__email__,
    # Package Description
    url=version.__git__,
    license=version.__license__,

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
