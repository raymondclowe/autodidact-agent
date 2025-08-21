"""Tests for rich_content_renderer JSXGraph parsing."""

from components.rich_content_renderer import (
    JSXGRAPH_TAG_PATTERN,
    _generate_template_script,
)

def test_jsxgraph_tag_regex_basic():
    m = JSXGRAPH_TAG_PATTERN.search("<jsxgraph>triangle:abc123</jsxgraph>")
    assert m, "Regex failed to match basic triangle tag"
    assert m.group(1) == 'triangle'
    assert m.group(2) == 'abc123'

def test_template_generation_triangle():
    html = _generate_template_script('triangle', 'tri1')
    assert 'board_tri1' in html
    assert 'initBoard' in html
    assert 'create' in html

def test_template_generation_unitcircle():
    html = _generate_template_script('unitcircle', 'uc1')
    assert 'board_uc1' in html
    assert 'circle' in html

def test_unknown_template_fallback():
    html = _generate_template_script('nonexistent', 'x1')
    assert 'initBoard' in html  # still initializes board
