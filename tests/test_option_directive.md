# Doctest directives

Doctest directives were originally provided by `doctest` package in the Python standard library and then adapted by `pytest`, to control the behavior of test case defined in docstrings. `markdoctest` also adapt doctest-style directives to control the behavior of each test cases. Here are two example usage.

Block-scope example: skips the whole block and do not test it.
````markdown
<!-- doctest: +SKIP -->
```python
>>> raise Exception("This is an exception")
```
````

Statement scope example: the first line is skipped:
````markdown
```python
>>> 3 + 4  # doctest: +SKIP
8
>>> 5 + 6
11
```
````


### Available options
All directives defined in `doctest` and `pytest` are available.

- [option flags](https://docs.python.org/3/library/doctest.html#doctest-options) defined in doctest package.
- [options](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options) defiined by pytest package.

### Format
Directives in `markdoctest` are in form like

```
doctest: +OPTION_FLAG_1, -OPTION_FLAG_2, ...
```
Prefix `+` or `-` stands for turn the option on or off.

### Scope
There are three different ways to set option flags:
- global option `doctest_optionflags` defined in [configure file](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options).
- block-scope option, defined in HTML comments ahead of individual block.
- statement-scope options, defined in python comments at the end of the statement.

Small-scope options override large-scope options.

## Global options
See [using-doctest-options](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options) in pytest doc.

## Block-scope options
Block-scope options are in HTML comments, ahead of the code block, e.g.,
````markdown
<!-- doctest: +NUMBER, +ELLIPSIS -->
```python
>>> math.pi
3.14
>>> print(list(range(10)))
[0, 1, ..., 9]
```
````


You can separate doctest options into multiple comments. One comment a line.
````markdown
<!-- doctest: +NORMALIZE_WHITESPACE -->
<!-- doctest: +ELLIPSIS -->
```python
>>> math.pi
3.14
>>> print(list(range(10)))
[0, 1, ..., 9]
```
````

Such options are block-scope, and can be overwritten by statement-scope options.
````markdown
<!-- doctest: +SKIP -->
```python
>>> 2 + 3   # this line is skipped.
5
>>>         # next line is not skipped.
>>> 9 / 2   # doctest: -SKIP
4.5
```
````


## Statement-scope options
Statement-scope options are not recommended to use, because they appear as a comment visible to markdown readers, which may distract or confuse readers. Block-scope options are more preferable.

You can specify multiple options by separating them by comma.
```python
>>> print(list(range(10))) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[0, 1, 2, ... 
    7, 8, 9]
```

[Options defined by pytest](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options) can also be used. For example, when enable `NUMBER` option provided by pytest, floating-point numbers only need to match as far as the precision you have written in the expected doctest output. 
```python
>>> import math
>>> math.pi # doctest: +NUMBER
3.14
```

Statement-scope options are ignored in script blocks, because a script block is tested as a whole, not statement by statement.
```python
# Next line has no effect.
# doctest: +FAIL_FAST
def f(x):
    return x + 1

print(f(2))
```
