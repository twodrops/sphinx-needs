from __future__ import annotations

import json
import os.path
import sys
from pathlib import Path

import pytest
from lxml import html as html_parser
from sphinx import version_info
from sphinx.testing.util import SphinxTestApp
from syrupy.filters import props

from sphinx_needs.api.need import NeedsNoIdException


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_build_html(test_app: SphinxTestApp, snapshot_doctree):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""

    # Check if doctree is correct.
    assert app.env.get_doctree("index") == snapshot_doctree

    # Basic checks for the generated html.
    html = Path(app.outdir, "index.html").read_text()
    assert "<h1>TEST DOCUMENT" in html
    assert "ST_001" in html

    # Check if static files got copied correctly.
    build_dir = Path(app.outdir) / "_static" / "sphinx-needs" / "libs" / "html"
    files = [f for f in build_dir.glob("**/*") if f.is_file()]
    assert build_dir / "sphinx_needs_collapse.js" in files
    assert build_dir / "datatables_loader.js" in files
    assert build_dir / "DataTables-1.10.16" / "js" / "jquery.dataTables.min.js" in files


@pytest.mark.skipif(
    sys.platform == "win32", reason="assert fails on windows, need to fix later."
)
@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "html", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_html_head_files(test_app: SphinxTestApp):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""

    # check usage in project root level
    html_path = str(Path(app.outdir, "index.html"))
    root_tree = html_parser.parse(html_path)
    script_nodes = root_tree.xpath("/html/head/script")
    script_files = [x.attrib["src"].rsplit("?", 1)[0] for x in script_nodes]
    assert script_files.count("_static/sphinx-needs/libs/html/datatables.min.js") == 1

    link_nodes = root_tree.xpath("/html/head/link")
    link_files = [x.attrib["href"].rsplit("?", 1)[0] for x in link_nodes]
    assert link_files.count("_static/sphinx-needs/modern.css") == 1

    # Checks if not \ (Backslash) is found as path of js/css files
    # This can happen when working on Windows (would be a bug ;) )
    for head_file in script_files + link_files:
        assert "\\" not in head_file


@pytest.mark.parametrize(
    "test_app",
    [
        {
            "buildername": "singlehtml",
            "srcdir": "doc_test/doc_basic",
            "no_plantuml": True,
        }
    ],
    indirect=True,
)
def test_build_singlehtml(test_app: SphinxTestApp):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "latex", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_build_latex(test_app: SphinxTestApp):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "epub", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_build_epub(test_app: SphinxTestApp):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "json", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_build_json(test_app: SphinxTestApp):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""


@pytest.mark.parametrize(
    "test_app",
    [{"buildername": "needs", "srcdir": "doc_test/doc_basic", "no_plantuml": True}],
    indirect=True,
)
def test_build_needs(test_app: SphinxTestApp, snapshot):
    app = test_app
    app.build()
    assert app._warning.getvalue() == ""

    json_text = Path(app.outdir, "needs.json").read_text()
    needs_data = json.loads(json_text)

    assert needs_data == snapshot(exclude=props("created", "project"))


# Test with needs_id_required=True and missing ids in docs.
@pytest.mark.parametrize(
    "test_app",
    [
        {
            "buildername": "html",
            "srcdir": "doc_test/doc_basic",
            "confoverrides": {"needs_id_required": True},
            "no_plantuml": True,
        }
    ],
    indirect=True,
)
def test_id_required_build_html(test_app: SphinxTestApp):
    with pytest.raises(NeedsNoIdException):
        app = test_app
        app.build()


def test_sphinx_api_build(tmp_path: Path, make_app: type[SphinxTestApp]):
    """
    Tests a build via the Sphinx Build API.
    It looks like that there are scenarios where this specific build makes trouble but no others.
    """
    src_dir = os.path.join(os.path.dirname(__file__), "doc_test", "doc_basic")

    if version_info >= (7, 2):
        src_dir = Path(src_dir)
    else:
        from sphinx.testing.path import path

        src_dir = path(src_dir)
        tmp_path = path(str(tmp_path))

    sphinx_app = make_app(
        srcdir=src_dir,
        builddir=tmp_path,
        buildername="html",
        parallel=4,
        freshenv=True,
    )
    sphinx_app.build()
    assert sphinx_app.statuscode == 0
