import pathlib
import re

from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

packages = [
    "BetterThreads"
]

version = None
with open('BetterThreads/__init__.py') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Version is not set")

setup(
    name="better-threads",
    version=version,
    description="A package that provides extended control over threads",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ItsYasiru/Better-Threads",
    author="Yasiru",
    author_email="yasiru.dharmathilaka@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9"
    ],
    packages=packages,
    include_package_data=True
)
