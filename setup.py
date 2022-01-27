import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="better-threads",
    version="0.3.0",
    description="The package provides extended control over threads",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ItsYasiru/Better-Threads",
    author="Yasiru",
    author_email="mwmykd@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["BetterThreads"],
    include_package_data=True
)
