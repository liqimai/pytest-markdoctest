#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


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
    long_description=read("README.md"),
    py_modules=["pytest_markdoctest"],
    package_dir={"": "src"},
    python_requires=">=3.6",
    install_requires=["pytest>=6"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
