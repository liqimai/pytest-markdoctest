#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="pytest-markdoctest",
    version="0.1.0",
    author="Qimai Li",
    author_email="liqimai@qq.com",
    maintainer="Qimai Li",
    maintainer_email="liqimai@qq.com",
    license="MIT",
    url="https://github.com/liqimai/pytest-markdoctest",
    description="A package to doctest your markdown files",
    long_description=readme,
    py_modules=["pytest_markdoctest"],
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "pytest11": [
            "markdoctest = pytest_markdoctest",
        ],
    },
)
