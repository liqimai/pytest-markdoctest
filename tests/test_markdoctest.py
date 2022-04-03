# -*- coding: utf-8 -*-
import pytest_markdoctest
from inspect import cleandoc
from pytest import Pytester


def test_help_message(pytester: Pytester):
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            # 'markdoctest:',
            "*--doctest-markdown*",
            "*markdown doctests file matching pattern, default:",
            "*test*.md",
        ],
        consecutive=True,
    )


def test_code_block_re():
    text = cleandoc(
        """
        Python block.
        ```python
        x += 1
        b = c
        ```

        Non-Python block.
        ```bash
        $ echo "hello"
        hello
        $ echo "world"
        world
        ```

        Empty block.
        ```
        ```

        Empty python block.
        ```python
        ```

        Four '`'s.
        ````python
        >>> print("hello")
        hello
        ````

        Language class with some other stuff.
        ```python foobar
        >>> print("hello")
        hello
        ```

        Block with indentation.
            ```python
            b = 3
            ```
        """
    )

    results = [
        {
            "code_class": "python",
            "code_content": "x += 1\nb = c\n",
        },
        {
            "code_class": "bash",
            "code_content": '$ echo "hello"\nhello\n$ echo "world"\nworld\n',
        },
        {
            "code_class": None,
            "code_content": "",
        },
        {
            "code_class": "python",
            "code_content": "",
        },
        {
            "code_class": "python",
            "code_content": '>>> print("hello")\n' "hello\n",
            "code_start": "````",
        },
        {
            "code_class": "python",
            "code_content": '>>> print("hello")\n' "hello\n",
        },
        {
            "code_class": "python",
            "code_content": "    b = 3\n",
        },
    ]
    CODE_BLOCK_RE = pytest_markdoctest.DoctestMarkdown._CODE_BLOCK_RE
    cnt = 0
    for m, result in zip(CODE_BLOCK_RE.finditer(text), results):
        # print(m.groupdict(), "\n", result)
        for k, v in result.items():
            assert m.group(k) == v
        cnt += 1
    assert cnt == len(results)


def test_general(pytester: Pytester):
    md = cleandoc(
        """
        First we import math.
        ```python
        >>> import math
        ```

        Then do some calculation:
        ```python
        >>> 2 + 3
        5
        >>> math.sqrt(2)
        1.414
        ```

        and more.
        ```python
        >>> 2 + 3
        5
        >>> print("Hello World!")
        Hello World!
        ```

        This shall be ignored, because it is not python.
        ```javascript
        > a = 3
        3
        > b = 4
        4
        ```

        Empty block.
        ```python
        ```
        """
    )
    pytester.makefile(".md", md)
    pytester.makeini(
        """
        [pytest]
        doctest_optionflags = NUMBER
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=3)
