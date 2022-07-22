# pytest-markdoctest

[![PyPI version](https://img.shields.io/pypi/v/pytest-markdoctest.svg)](https://pypi.org/project/pytest-markdoctest)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-markdoctest.svg)](https://pypi.org/project/pytest-markdoctest)

A pytest plugin to doctest your markdown files.

Help you test your python blocks in markdown in `doctest` style, and make sure them behaving as you expected. This is especially helpful when dealing with markdown files containing many demo code, such as 
- A project documented in markdown files, 
- A tutorial on python written in markdown.


## Requirements

- python>=3.7
- pytest>=6

## Installation

You can install \"pytest-markdoctest\" via
[pip](https://pypi.org/project/pip/) from
[PyPI](https://pypi.org/project):

    $ pip install pytest-markdoctest

## Usage

To test a single markdown file:
```sh
$ pytest docs/index.md
```
or test all markdown files in a directory:
```sh
$ pytest docs/
```

Your markdown file may contains REPL block (Read-Eval-Print-Loop).

```python
>>> 2 + 3
5
>>> print("Hello World!")
Hello World!
```

Or script block.
```python
import math
def square(x):
    return x*x
```

Variables/functions defined before are accessible in subsequent blocks.
```python
>>> math.pow(2, 2)
4.0
>>> square(2)
4
```

Markdoctest automatically find all code blocks tagged by `python`, `py`, `pycon` and test them.

Directives are allowed to control testing behavior.
````markdown
<!-- doctest: +SKIP -->
```python
import math
a = 3 / 0
```
````

## Advanced Usage

- [Option directives](./tests/test_option_directive.md)
- [Script block](./tests/test_script_block.md)


## License

Distributed under the terms of the
[MIT](http://opensource.org/licenses/MIT) license,
\"pytest-markdoctest\" is free and open source software

## Acknowledgement

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated
with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with
[\@hackebrot](https://github.com/hackebrot)\'s
[cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
template.