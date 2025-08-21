"""Rich content renderer for assistant messages.

Handles:
 - JSXGraph diagram markup (<jsxgraph>template:id</jsxgraph> or <jsxgraph>custom:id</jsxgraph> + fenced code)
 - Image markup (delegates to existing image handlers)

This allows AI tutor messages to embed interactive diagrams instead of
showing raw tags and code blocks.
"""

from __future__ import annotations

import re
import logging
from typing import List, Tuple

import streamlit as st

from utils.static_assets import get_jsxgraph_assets
from components.image_display import process_image_markup, create_image_placeholder

logger = logging.getLogger("autodidact.rich_renderer")

JSXGRAPH_TAG_PATTERN = re.compile(r"<jsxgraph>([a-zA-Z0-9_]+):([a-zA-Z0-9_\-]+)</jsxgraph>")

def _template_triangle(board_var: str) -> str:
    return (
        "var A="+board_var+".create('point',[0,0],{name:'A'});"\
        "var B="+board_var+".create('point',[4,0],{name:'B'});"\
        "var C="+board_var+".create('point',[4,3],{name:'C'});"\
        +board_var+".create('polygon',[A,B,C],{fillOpacity:0.1});"
    )

def _template_axes(board_var: str) -> str:
    return "/* Axes template just ensures an empty coordinate plane */"

def _template_unitcircle(board_var: str) -> str:
    return (
        "var O="+board_var+".create('point',[0,0],{name:'O',fixed:true});"\
        +board_var+".create('circle',[O,1],{strokeColor:'#555'});"\
        +board_var+".create('point',[1,0],{name:'(1,0)'});"\
        +board_var+".create('point',[0,1],{name:'(0,1)'});"
    )

TEMPLATE_BUILDERS = {
    "triangle": _template_triangle,
    "axes": _template_axes,
    "unitcircle": _template_unitcircle,
}

def _iframe_wrapper(inner_html: str) -> str:
    """Wrap provided HTML snippet in a full HTML document for iframe rendering.

    Each Streamlit component is its own iframe with an isolated DOM. We must
    include JSXGraph assets inside EVERY iframe; injecting them into the parent
    page won't expose JXG to the sandboxed iframe.
    """
    css_content, js_content = get_jsxgraph_assets()
    return f"""
<html>
<head>
{css_content}
{js_content}
</head>
<body style='margin:0;padding:0;'>
{inner_html}
</body>
</html>
""".strip()

def _generate_template_script(template: str, diagram_id: str) -> str:
    container_id = f"board_{diagram_id}"
    board_var = "board"
    body_builder = TEMPLATE_BUILDERS.get(template)
    body_code = body_builder(board_var) if body_builder else "/* Unknown template */"
    snippet = f"""<div id=\"{container_id}\" style=\"width:400px;height:300px;margin:10px auto;border:1px solid #ccc;\"></div>
<script>(function() {{
    function init(retries) {{
        if (typeof JXG==='undefined' || !JXG.JSXGraph) {{
                if (retries > 0) return setTimeout(function(){{init(retries-1);}}, 60);
                console.error('JSXGraph library not loaded');
                return;
        }}
        try {{
                var {board_var}=JXG.JSXGraph.initBoard('{container_id}', {{boundingbox:[-5,5,5,-5],axis:true,showNavigation:true,showZoom:true}});
                {body_code}
        }} catch(e) {{ console.error('JSXGraph template init error', e); }}
    }}
    init(40); // ~2.4s max
}})();</script>"""
    return _iframe_wrapper(snippet)

def _wrap_custom_code(diagram_id: str, code_js: str) -> str:
    container_id = f"board_{diagram_id}"
    needs_board = "initBoard(" not in code_js
    default_board = f"var board = JXG.JSXGraph.initBoard('{container_id}', {{boundingbox:[-5,5,5,-5],axis:true,showNavigation:true,showZoom:true}});\n" if needs_board else ""
    sanitized = re.sub(r"</?script[^>]*>", "", code_js, flags=re.IGNORECASE)
    snippet = f"""<div id=\"{container_id}\" style=\"width:400px;height:300px;margin:10px auto;border:1px solid #ccc;\"></div>
<script>(function() {{
    function init(retries) {{
        if (typeof JXG==='undefined' || !JXG.JSXGraph) {{
                if (retries > 0) return setTimeout(function(){{init(retries-1);}}, 60);
                console.error('JSXGraph library not loaded for custom diagram');
                return;
        }}
        try {{ {default_board}{sanitized} }} catch(e) {{ console.error('JSXGraph custom diagram error', e); }}
    }}
    init(40);
}})();</script>"""
    return _iframe_wrapper(snippet)

def _extract_custom_code(lines: List[str], start_index: int) -> Tuple[str, int]:
    """Extract fenced code block (``` ... ```) starting after start_index.
    Returns (code, new_index_after_block).
    If not found, returns ("", start_index).
    """
    if start_index + 1 >= len(lines):
        return "", start_index
    i = start_index + 1
    if not lines[i].startswith("```"):
        return "", start_index
    i += 1  # move past opening fence
    code_lines: List[str] = []
    while i < len(lines) and not lines[i].startswith("```"):
        code_lines.append(lines[i])
        i += 1
    if i < len(lines) and lines[i].startswith("```"):
        i += 1  # skip closing fence
    return "\n".join(code_lines), i - 1

def _render_segments_with_jsxgraph(content: str) -> None:
    lines = content.splitlines()
    buffer: List[str] = []
    i = 0
    # No global header injection; each component iframe loads assets itself.

    while i < len(lines):
        line = lines[i]
        tag_match = JSXGRAPH_TAG_PATTERN.search(line)
        if tag_match:
            if buffer:
                st.markdown("\n".join(buffer), unsafe_allow_html=True)
                buffer.clear()
            kind, diag_id = tag_match.groups()
            diagram_html = ""
            if kind in TEMPLATE_BUILDERS:
                diagram_html = _generate_template_script(kind, diag_id)
            elif kind == "custom":
                code_js, new_i = _extract_custom_code(lines, i)
                if code_js:
                    diagram_html = _wrap_custom_code(diag_id, code_js)
                    i = new_i
                else:
                    diagram_html = _wrap_custom_code(diag_id, "")
            else:
                buffer.append(line)
                i += 1
                continue
            st.components.v1.html(diagram_html, height=330, scrolling=False)
            i += 1
        else:
            buffer.append(line)
            i += 1
    if buffer:
        st.markdown("\n".join(buffer), unsafe_allow_html=True)

def render_rich_content(content: str) -> None:
    try:
        cleaned_content, image_requests = process_image_markup(content)
        if '<jsxgraph>' in cleaned_content:
            _render_segments_with_jsxgraph(cleaned_content)
        else:
            st.markdown(cleaned_content, unsafe_allow_html=True)
        if image_requests:
            st.markdown("---")
            st.markdown("**📚 Related Educational Images (placeholders)**")
            for req in image_requests:
                create_image_placeholder(f"{req}")
    except Exception as e:
        logger.error(f"Failed to render rich content: {e}")
        st.markdown(content)

__all__ = ["render_rich_content"]
