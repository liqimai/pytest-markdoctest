# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest(
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
