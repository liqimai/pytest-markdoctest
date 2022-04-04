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
    MultipleDoctestFailures,
    _get_runner,
    _get_checker,
    _get_continue_on_failure,
    _check_all_skipped,
)
from _pytest.config.argparsing import Parser
from _pytest.config import Config

from typing import Optional
from typing import Iterable
from typing import List


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

    #
    _CODE_BLOCK_RE = re.compile(
        r"""
        ^                           # Necessarily at the beginning of a new line
        (?P<code_all>
            (?P<code_start>
                [ \t]*              # Possibly leading spaces
                \`{3,}              # 3 code marks (backticks) or more
            )
            [ \t]*                  # Possibly some spaces or tab
            (?P<code_class>[\w\-\.]+)?    # or a code class like html, ruby, perl
            (?:[^\n]*)?             # possibly some text before newline
            \n                      # newline
            (?P<code_content>.*?)   # enclosed content
            # \n+
            (?<!`)
            (?P=code_start)         # balanced closing block marks
            (?!`)
        )
        $                # and a new line or end of string
        """,
        re.DOTALL | re.MULTILINE | re.VERBOSE,
    )

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
        runner.globs = globs  # runner-level globs

        parser = doctest.DocTestParser()
        charno, lineno = 0, 1
        for m in self._CODE_BLOCK_RE.finditer(text):
            # Update lineno (lines before this example)
            lineno += text.count("\n", charno, m.start())
            charno = m.start()

            code_content = m.group("code_content")
            code_class = m.group("code_class").split()[0]
            if code_class in ("python", "py", "pycon"):
                name = "<%s block at line %s>" % (code_class, lineno)
                # dummy globs in test. real globs is runner.globs.
                test = parser.get_doctest(code_content, {}, name, filename, lineno)
                if test.examples:
                    yield DoctestMarkdownItem.from_parent(self, name=test.name, runner=runner, dtest=test)

            lineno += text.count("\n", charno, m.end())
            charno = m.end()


class DoctestMarkdownItem(DoctestItem):
    def runtest(self) -> None:
        assert self.dtest is not None
        assert self.runner is not None
        _check_all_skipped(self.dtest)
        self._disable_output_capturing_for_darwin()
        failures: List["doctest.DocTestFailure"] = []
        # Hack DoctestItem to let test share the runner's globs and let
        # clear_globs=False.
        self.dtest.globs = self.runner.globs
        self.runner.run(self.dtest, out=failures, clear_globs=False)  # type: ignore[arg-type]
        if failures:
            raise MultipleDoctestFailures(failures)
