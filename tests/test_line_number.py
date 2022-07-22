from inspect import cleandoc
from pytest import Pytester


def test_line_number_in_error_msg(pytester: Pytester):
    md = cleandoc(
        """
        ```python
        >>> print("Hello")
        Hello
        >>> 2 + 3
        6
        >>> 5 + 7
        10
        ```

        some text

        ```python
        import math
        assert False
        ```

        <!-- doctest: +NUMBER-->
        ```python
        >>> 2**0.5
        1.8
        ```

        some text

        <!-- doctest: +ELLIPSIS>
        <!-- doctest: +NUMBER-->
        ```python
        >>> 2**0.5
        1.8
        ```

        <!-- doctest: +NUMBER-->
        ```python
        import math
        assert False
        ```

        <!-- doctest: +ELLIPSIS>
        <!-- doctest: +NUMBER-->
        ```python
        import math
        assert False
        ```
        """
    )
    pytester.makefile(".md", md)
    result = pytester.runpytest()
    result.assert_outcomes(failed=6)
    result.stdout.fnmatch_lines(
        [
            '002 >>> print("Hello")',
            "003 Hello",
            "004 >>> 2 + 3",
        ],
        consecutive=True,
    )

    result.stdout.fnmatch_lines(
        [
            "013 import math",
            "014 assert False",
        ],
        consecutive=True,
    )

    result.stdout.fnmatch_lines(
        [
            "019 >>> 2**0.5",
            "028 >>> 2**0.5",
        ]
    )

    result.stdout.fnmatch_lines(
        [
            "034 import math",
            "035 assert False",
        ],
        consecutive=True,
    )

    result.stdout.fnmatch_lines(
        [
            "041 import math",
            "042 assert False",
        ],
        consecutive=True,
    )

    result.stdout.fnmatch_lines(
        [
            "FAILED test_line_number_in_error_msg.md::<python block at line 1>",
            "FAILED test_line_number_in_error_msg.md::<python block at line 12>",
            "FAILED test_line_number_in_error_msg.md::<python block at line 18>",
            "FAILED test_line_number_in_error_msg.md::<python block at line 27>",
            "FAILED test_line_number_in_error_msg.md::<python block at line 33>",
            "FAILED test_line_number_in_error_msg.md::<python block at line 40>",
        ],
        consecutive=True,
    )
