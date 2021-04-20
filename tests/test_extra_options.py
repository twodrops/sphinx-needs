import re
from pathlib import Path

from sphinx_testing import with_app


@with_app(buildername="html", srcdir="doc_test/extra_options")
def test_custom_attributes_appear(app, status, warning):
    app.build()

    html = Path(app.outdir, "index.html").read_text()

    # Custom options should appear
    # assert 'introduced: <cite>1.0.0</cite>' in html
    assert '<span class="needs_data">1.5.1' in html
    assert '<span class="needs_data">1.1.1' in html
    assert '<span class="needs_data">component_b' in html

    tables = re.findall("(<table .*?</table>)", html, re.DOTALL)
    assert len(tables) == 4

    # First table should have all requirements
    assert "R_12345" in tables[2]
    assert "R_12346" in tables[2]
    assert all(column in tables[2] for column in ("Introduced", "Updated", "Impacts"))

    # Second table should only have component A requirements
    assert "R_12345" in tables[3]
    assert "R_12346" not in tables[3]

    # Need list should only have component B requirements
    items = re.findall('(<div class="line-block" id="needlist-index-.*?</div>)', html, re.DOTALL)
    assert len(items) == 1
    assert "R_12346" in items[0]
