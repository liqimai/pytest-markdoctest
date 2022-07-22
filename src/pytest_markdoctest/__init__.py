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
import doctest
import sys
import ast
import pytest

from pytest import Parser, Config, Collector
from _pytest.pathlib import fnmatch_ex
from _pytest.doctest import (
    DoctestItem,
    get_optionflags,
    _get_checker,
    _get_continue_on_failure,
    _init_runner_class,
)

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

    # regular expression for markdown code blocks like
    # ```python
    # some python code
    # ```
    _CODE_BLOCK_RE = re.compile(
        r"""
        (?P<option_list>            # html comment with doctest option
                                    # such as <!--- doctest: ... --->
            (
                ^                       # Necessarily at the beginning of a new line
                [ \t]*                  # Possibly leading spaces
                <!--([^\n]*?)-->             # html comment
                [ \t]*                  # trailing spaces
                \n                      # a newline
            )*                      # Zero or more html comments
        )
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

        runner = MarkDoctestRunner(
            verbose=False,
            optionflags=optionflags,
            checker=_get_checker(),
            continue_on_failure=_get_continue_on_failure(self.config),
            globs=globs,  # runner-level globs
        )

        parser = PythonCodeBlockParser()
        charno, lineno = 0, 1
        for m in self._CODE_BLOCK_RE.finditer(text):
            # Update lineno (lines before this example)
            lineno += text.count("\n", charno, m.start())
            charno = m.start()

            code_class = m.group("code_class")
            if code_class is not None:
                code_class = code_class.split()[0]
            if code_class in ("python", "py", "pycon"):
                content_line_no = lineno + m.group("option_list").count("\n")
                name = "<%s block at line %s>" % (code_class, content_line_no)
                test = parser.get_doctest(m, name, filename, lineno)
                if test.examples:
                    yield DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)

            lineno += text.count("\n", charno, m.end())
            charno = m.end()


class ScriptBlockParser(doctest.DocTestParser):
    """
    A parser for script code blocks (lines not starting with '>>>').
    """

    def parse(self, string, name="<string>"):
        """
        parse string into examples.
        """
        ast_tree = ast.parse(string)
        # directives are ignored in script block.
        options = {}
        if sys.version_info[:3] > (3, 9):
            statements = [ast.unparse(element) for element in ast_tree.body]
        elif sys.version_info[:3] > (3, 8):
            statements = self._split_into_statements(string, ast_tree)
        else:
            statements = [self._unparse(element) for element in ast_tree.body]

        examples = []
        for element, stmt in zip(ast_tree.body, statements):
            # Given ELLIPSIS option and  want="...", any output is valid
            # output, because we do not restrict the output of script
            # block.
            options[doctest.ELLIPSIS] = True

            # create an example for the statement
            eg = doctest.Example(
                stmt,
                want="...",
                lineno=element.lineno - 1,
                indent=0,
                options=options,
            )
            # doctest.Example.__init__ always adds a tail '\n' to want,
            # which is not expected here, so we force it to be "..."
            # without '\n', so it can match anything.
            eg.want = "..."
            examples.append(eg)
        return examples

    def _unparse(self, ast_node):
        from pytest_markdoctest.unparse import Unparser
        from io import StringIO

        stmt = StringIO()
        Unparser(ast_node, stmt)
        return stmt.getvalue()

    def _split_into_statements(self, source, ast_tree):
        def get_source_stmt(element: ast.stmt):
            ls = lines[element.lineno - 1 : element.end_lineno]
            ls[-1] = ls[-1][: element.end_col_offset]
            ls[0] = ls[0][element.col_offset :]
            return "\n".join(ls)

        lines = source.splitlines()
        statements = [get_source_stmt(element) for element in ast_tree.body]
        return statements


class PythonCodeBlockParser:

    _OPTION_RE = re.compile(
        r"""
        (?P<option>                 # html comment with doctest option
                                    # such as <!--- doctest: ... --->
            <!--+\s*                # opening comment
            (?P<option_content>
                doctest:\s*([^\n\'"]*?) # doctest option
            )
            \s*--+>                # closing comment
        )
        """,
        re.DOTALL | re.MULTILINE | re.VERBOSE,
    )

    doctest_parser = doctest.DocTestParser()
    script_parser = ScriptBlockParser()

    def get_doctest(self, code_block: "re.Match", name, filename, lineno):
        """
        If `string` starts with '>>>', treat it as an REPL block,
        otherwise treat it as an script block.
        """

        code_content = code_block.group("code_content")
        option_list = code_block.group("option_list")

        # parse code_content into examples
        code_content_lineno = lineno + option_list.count("\n")
        # dummy globs in test. real globs is runner.globs.
        globs = {}
        if code_content.startswith(">>>"):
            test = self.doctest_parser.get_doctest(code_content, globs, name, filename, code_content_lineno)
        else:
            test = self.script_parser.get_doctest(code_content, globs, name, filename, code_content_lineno)

        # parse test-level options
        test.options = {}
        for opt in self._OPTION_RE.finditer(option_list):
            # compose a valid doctest directive, and parse it by
            # doctest.DocTestParser._find_options
            directive = "a # " + opt.group("option_content")
            opt = self.doctest_parser._find_options(directive, name, lineno)
            test.options.update(opt)

        # update example-level options
        for eg in test.examples:
            eg.options = {**test.options, **eg.options}

        return test


class MarkDoctestRunner(_init_runner_class()):
    def __init__(self, *args, globs={}, **kwargs):
        """
        Inheritance chain:

        MarkDoctestRunner -> PytestDoctestRunner
                          -> DebugRunner -> DocTestRunner

        Nearly same as PytestDoctestRunner, except that it has an
        runner-level dict storing globals variables.
        """
        super().__init__(*args, **kwargs)
        self.globs = globs  # runner-level globs

    def run(self, test, compileflags=None, out=None, clear_globs=False):
        """
        clear_globs is default to False, because we want to keep global
        variables across tests.
        """
        # tests share the runner's globs.
        test.globs = self.globs
        return super().run(test, compileflags, out, clear_globs)
