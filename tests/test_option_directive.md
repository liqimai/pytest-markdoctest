# Doctest directives
[Doctest directives](https://docs.python.org/3/library/doctest.html#directives) may be used to modify the [option flags](https://docs.python.org/3/library/doctest.html#doctest-options) for an individual example.

Doctest directives are specified by a comment in format `# doctest: ...` such as:

```
# doctest: +OPTIONFLAGS
# doctest: -OPTIONFLAGS
```
where `OPTION` are [option flags](https://docs.python.org/3/library/doctest.html#doctest-options)  defined in doctest package. Prefix `+` or `-` stands for turn the option on or off.

For example, the following option will skip the first line of the example:
```python
>>> 3 + 4  # doctest: +SKIP
8
>>> 5 + 6
11
```

Option `ELLIPSIS` let `...` match any number of characters.
```python
>>> print(list(range(20))) # doctest: +ELLIPSIS, 
[0, 1, ..., 18, 19]
```

Option `NORMALIZE_WHITESPACE` treats all sequences of whitespace (blanks and newlines) as equal. This is useful for ignoring differences in whitespace.
```python
>>> print(list(range(10))) # doctest: +NORMALIZE_WHITESPACE 
[0, 1, 2, 3, 4, 
    5, 6, 7, 8, 9]
```

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