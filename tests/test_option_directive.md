# Doctest directives

[Doctest directives](https://docs.python.org/3/library/doctest.html#directives) may be used to modify the [option flags](https://docs.python.org/3/library/doctest.html#doctest-options) for an individual example, which are in form

```
doctest: +OPTION_FLAG_1, -OPTION_FLAG_2, ...
```
where `OPTION_FLAG` are [option flags](https://docs.python.org/3/library/doctest.html#doctest-options). Prefix `+` or `-` stands for turn the option on or off.

There are three different ways to set option flags:
- global option `doctest_optionflags` defined in [configure file](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options).
- block-scope option, defined in HTML comments ahead of individual block.
- statement-scope options, defined in python comments at the end of the statement.

Small-scope option can rewrite large-scope option.

Block-scope example: skips the whole block.
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
- [option flags](https://docs.python.org/3/library/doctest.html#doctest-options) defined in doctest package.
- [options](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options) defiined by pytest package.

## Statement-scope options

You can specify multiple options by separating them by comma.
```python
>>> print(list(range(10))) # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[0, 1, 2, ... 
    7, 8, 9]
```

Can also be used in script block.
```python
# doctest: +FAIL_FAST
def f(x):
    return x + 1

print(f(2))
```

[Options defiined by pytest](https://docs.pytest.org/en/7.0.x/how-to/doctest.html#using-doctest-options) can also be used. For example, when enable `NUMBER` option provided by pytest, floating-point numbers only need to match as far as the precision you have written in the expected doctest output. 
```python
>>> import math
>>> math.pi # doctest: +NUMBER
3.14
```


## Block-scope options
However, doctest options in python comments are also visible to markdown readers, which diverts reader's attention. To solve it, you can use block-scope options, which is in HTML comments and thus completely invisible to markdown readers.

Multiple doctest options in HTML comment, separated by comma.
````markdown
<!-- doctest: +NUMBER, +ELLIPSIS -->
```python
>>> math.pi
3.14
>>> print(list(range(10)))
[0, 1, ..., 9]
```
````


Separate doctest options into multiple comments, one comment a line.
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
````