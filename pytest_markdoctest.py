# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2004 Holger Krekel and others

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from pathlib import Path
from _pytest.pathlib import fnmatch_ex
import pytest
import doctest

# from _pytest import doctest as pytest_doctest
# import _pytest.doctest as pytest_doctest
from _pytest.doctest import (
    Collector,
    DoctestItem,
    get_optionflags,
    _get_runner,
    _get_checker,
    _get_continue_on_failure,
)
from _pytest.config.argparsing import Parser
from _pytest.config import Config

from typing import Optional
from typing import Iterable


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup("collect")
    group.addoption(
        "--doctest-markdown",
        action="append",
        default=[],
        metavar="pat",
        help="markdown doctests file matching pattern, default: test*.md",
        dest="doctestmarkdown",
    )


def pytest_collect_file(
    file_path: Path,
    parent: Collector,
) -> Optional["DoctestMarkdown"]:
    config = parent.config
    if file_path.suffix == ".md" and _is_doctest_markdown(config, file_path, parent):
        md: DoctestMarkdown = DoctestMarkdown.from_parent(parent, path=file_path)
        return md


def _is_doctest_markdown(config: Config, path: Path, parent: Collector) -> bool:
    if path.suffix in (".md") and parent.session.isinitpath(path):
        return True
    globs = config.getoption("doctestmarkdown") or ["test*.md"]
    # globs = None or ["test*.md"]
    return any(fnmatch_ex(glob, path) for glob in globs)


class DoctestMarkdown(pytest.Module):
    obj = None

    def collect(self) -> Iterable[DoctestItem]:

        # Inspired by doctest.testfile; ideally we would use it directly,
        # but it doesn't support passing a custom checker.
        encoding = self.config.getini("doctest_encoding")
        text = self.path.read_text(encoding)
        filename = str(self.path)
        name = self.path.name
        globs = {"__name__": "__main__"}

        optionflags = get_optionflags(self)

        runner = _get_runner(
            verbose=False,
            optionflags=optionflags,
            checker=_get_checker(),
            continue_on_failure=_get_continue_on_failure(self.config),
        )

        # Inspired by _pytest.doctest.DoctestTextfile; ideally we would use it directly,
        # but it doesn't support passing a custom parser.
        parser = MarkdownTestParser()

        test = parser.get_doctest(text, globs, name, filename, 0)
        if test.examples:
            yield DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)


class MarkdownTestParser(doctest.DocTestParser):
    """
    A class used to parse markdown files containing doctest examples.
    """

    # This regular expression is used to find doctest examples in a
    # string.  It defines three groups: `source` is the source code
    # (including leading indentation and prompts); `indent` is the
    # indentation of the first (PS1) line of the source code; and
    # `want` is the expected output (including leading indentation).
    _EXAMPLE_RE = re.compile(
        r"""
        # Source consists of a PS1 line followed by zero or more PS2 lines.
        (?P<source>
            (?:^(?P<indent> [ ]*) >>>    .*)    # PS1 line
            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
        \n?
        # Want consists of any non-blank lines that do not start with PS1.
        (?P<want> (?:(?![ ]*$)    # Not a blank line
                     (?![ ]*>>>)  # Not a line starting with PS1
                     (?![ ]*```+) # Not a line starting with ```
                     .+$\n?       # But any other line
                  )*)
        """,
        re.MULTILINE | re.VERBOSE,
    )
