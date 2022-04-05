# flake8: noqa: W291
import pytest_markdoctest
from inspect import cleandoc
from pytest import Pytester


def test_html_option_directive_parse():
    CODE_BLOCK_RE = pytest_markdoctest.DoctestMarkdown._CODE_BLOCK_RE
    _OPTION_RE = pytest_markdoctest.PythonCodeBlockParser._OPTION_RE

    text = cleandoc(
        """
        <!---  doctest: +SKIP --->
        ```python
        >>> print("hello")
        ```
        """
    )
    code_blocks = list(CODE_BLOCK_RE.finditer(text))
    assert len(code_blocks) == 1
    option_list = code_blocks[0].group("option_list")
    assert option_list == "<!---  doctest: +SKIP --->\n"
    options = list(_OPTION_RE.finditer(option_list))
    assert len(options) == 1
    assert options[0].group("option") == "<!---  doctest: +SKIP --->"
    assert options[0].group("option_content") == "doctest: +SKIP"

    text = cleandoc(
        """
        This is ignored, because it is not directly followed by a code block.
        <!--doctest:+SKIP,+NUMBER-->  

        <!--doctest:+SKIP,+NUMBER-->  
        <!-- doctest: +SKIP, +NUMBER --> 
        <!-- doctest:   +SKIP     --> 
            <!-- doctest:   -NUMBER   -->  
        ```python
        >>> print("hello")
        ```
        """
    )

    code_blocks = list(CODE_BLOCK_RE.finditer(text))
    assert len(code_blocks) == 1
    option_list = code_blocks[0].group("option_list")

    correct_list = [
        "<!--doctest:+SKIP,+NUMBER-->  \n",
        "<!-- doctest: +SKIP, +NUMBER --> \n",
        "<!-- doctest:   +SKIP     --> \n",
        "    <!-- doctest:   -NUMBER   -->  \n",
    ]
    correct_contents = [
        "doctest:+SKIP,+NUMBER",
        "doctest: +SKIP, +NUMBER",
        "doctest:   +SKIP",
        "doctest:   -NUMBER",
    ]
    assert option_list == "".join(correct_list)
    options = list(_OPTION_RE.finditer(option_list))
    assert len(options) == 4

    for option, correct_option, correct_content in zip(options, correct_list, correct_contents):
        assert option.group("option") == correct_option.strip()
        assert option.group("option_content") == correct_content


def test_html_option_directive_parse(pytester: Pytester):
    md = cleandoc(
        """
        <!-- doctest: +SKIP -->
        ```python
        raise Exception("This is an exception")
        ```
        """
    )
    pytester.makefile(".md", md)
    result = pytester.runpytest()
    result.assert_outcomes(skipped=1)

    md = cleandoc(
        """
        <!-- doctest: +NUMBER, +ELLIPSIS -->
        ```python
        >>> 2**0.5
        1.414
        >>> print(list(range(10)))
        [0, 1, ..., 9]
        ```
        """
    )
    pytester.makefile(".md", md)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    md = cleandoc(
        """
        <!-- doctest: +NORMALIZE_WHITESPACE -->
        <!-- doctest: +ELLIPSIS -->
        ```python
        >>> print(list(range(10)))
        [0,     1,     2,  ...,     9]
        ```
        """
    )
    pytester.makefile(".md", md)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)

    md = cleandoc(
        """
        <!-- doctest: +SKIP -->
        ```python
        >>> 2 + 3   # this line is skipped.
        5
        >>>         # next line is not skipped.
        >>> 9 / 2   # doctest: -SKIP
        4.5
        ```
        """
    )

    pytester.makefile(".md", md)
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
