"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
import io

# To use a consistent encoding
import os

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

NAME = "housekeeper"
DESCRIPTION = "Housekeeper takes care of files"
AUTHOR = "Robin Andeer"
EMAIL = "mans.magnusson@scilifelab.se"
URL = "https://github.com/Clinical-Genomics/housekeeper"

HERE = os.path.abspath(os.path.dirname(__file__))


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with open(req_path, "r") as handle:
        # remove comments and empty lines
        lines = (
            line.strip() for line in handle if line.strip() and not line.startswith("#")
        )
        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            else:
                # add the line as a new requirement
                install_requires.append(line)
    return install_requires


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


setup(
    name=NAME,
    # Versions should comply with PEP440. For a discussion on
    # single-sourcing the version across setup.py and the project code,
    # see http://packaging.python.org/en/latest/tutorial.html#version
    version="2.7.5",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    # What does your project relate to? Separate with spaces.
    keywords="housekeeper development",
    author=AUTHOR,
    author_email=EMAIL,
    license="MIT",
    # The project's main homepage
    url=URL,
    packages=find_packages(exclude=("tests*", "docs", "examples")),
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    include_package_data=True,
    zip_safe=False,
    # Although 'package_data' is the preferred approach, in some case you
    # may need to place data files outside of your packages.
    # In this case, 'data_file' will be installed into:
    # '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # Install requirements loaded from ``requirements.txt``
    install_requires=parse_reqs(),
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and
    # allow pip to create the appropriate form of executable for the
    # target platform.
    entry_points={"console_scripts": ["housekeeper = housekeeper.cli:base"]},
    # See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
    ],
)
