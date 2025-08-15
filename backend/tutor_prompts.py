"""tutor_prompts.py

Refactored to use external prompt templates located in `prompts/` directory instead of
large embedded multi‑line string literals. This ensures a single source of truth for
prompt content and avoids Unicode / encoding issues when editing prompts.

Exports (backwards compatible):
    TEACHING_PROMPT_TEMPLATE (str) – contents of `prompts/teaching_prompt.txt`
    RECAP_PROMPT_TEMPLATE (str)    – contents of `prompts/recap_prompt.txt`
    format_teaching_prompt(...)
    format_recap_prompt(...)

Also keeps existing citation / control‑block utilities.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

# ---------------------------------------------------------------------------
# External prompt loader integration
# ---------------------------------------------------------------------------
try:
    from utils.prompt_loader import (
        get_teaching_prompt_template,
        get_recap_prompt_template,
        format_teaching_prompt as _file_format_teaching_prompt,
        format_recap_prompt as _file_format_recap_prompt,
        build_ref_list as _build_ref_list,
        get_images_context_for_prompt as _get_images_context_for_prompt,
    )
except Exception as e:  # pragma: no cover - severe import failure
    # Provide clear error early – templates won't work without loader
    raise ImportError(
        f"Failed to import prompt loader utilities: {e}. Ensure `utils/prompt_loader.py` exists."
    )

# Optional: validate control JSON against a schema if jsonschema is installed.
try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None  # falls back to no‑validation mode

def get_images_context_for_ai() -> str:
    """Backward compatible wrapper (delegates to prompt_loader)."""
    return _get_images_context_for_prompt()

# ---------------------------------------------------------------------------
# Reference‑list helper
# ---------------------------------------------------------------------------

def build_ref_list(refs: list[dict[str, Any]]) -> str:  # noqa: D401
    return _build_ref_list(refs)

### Load external prompt templates (single source of truth)
TEACHING_PROMPT_TEMPLATE = get_teaching_prompt_template()
RECAP_PROMPT_TEMPLATE = get_recap_prompt_template()

# ---------------------------------------------------------------------------
# JSON‑Schema definitions for control blocks
# ---------------------------------------------------------------------------

TEACHING_CONTROL_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "TeachingControl",
    "type": "object",
    "properties": {
        "objective_complete": {
            "type": "boolean",
            "description": "True when learner has mastered the current objective."
        }
    },
    "required": ["objective_complete"],
    "additionalProperties": False,
}

RECAP_CONTROL_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "RecapControl",
    "type": "object",
    "properties": {
        "prereq_complete": {
            "type": "boolean",
            "description": "True when recap questions are answered satisfactorily."
        }
    },
    "required": ["prereq_complete"],
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# Prompt‑formatting helpers
# ---------------------------------------------------------------------------

def format_teaching_prompt(*args, **kwargs) -> str:  # noqa: D401
    """Proxy to file-based implementation (keeps previous import paths working)."""
    return _file_format_teaching_prompt(*args, **kwargs)

def format_recap_prompt(*args, **kwargs) -> str:  # noqa: D401
    return _file_format_recap_prompt(*args, **kwargs)

# ---------------------------------------------------------------------------
# Response cleanup functions
# ---------------------------------------------------------------------------

def clean_improper_citations(text: str, refs: list[dict[str, Any]]) -> str:
    """Clean improper citation formats from AI responses.
    
    Fixes raw reference IDs like [concept_mapping_design] that should be
    properly formatted citations or removed entirely.
    
    Parameters
    ----------
    text : str
        AI response text that may contain improper citations
    refs : list[dict]
        Available references with rid, title, section/loc info
        
    Returns
    -------
    str
        Cleaned text with improper citations fixed
    """
    if not text or not refs:
        return text
    
    # Build mapping of rid to reference info
    rid_to_ref = {ref['rid']: ref for ref in refs}
    
    # Pattern to match raw rid citations like [concept_mapping_design]
    # This should match [alphanumeric_text] that are NOT already proper citations (without §)
    pattern = r'\[([a-zA-Z0-9_-]+)\](?!\s*§)'  # Match [rid] not followed by §
    
    def replace_improper_citation(match):
        rid = match.group(1)
        
        # If this rid exists in our references, convert to proper citation format
        if rid in rid_to_ref:
            ref = rid_to_ref[rid]
            section = ref.get('section') or ref.get('loc', '')
            if section:
                return f"[{rid} §{section}]"
            else:
                # If no section info, replace with descriptive text
                title = ref.get('title', rid)
                return f"research on {title}"
        
        # If rid not found in references, remove the improper citation entirely
        return ""
    
    # Apply the replacement
    cleaned_text = re.sub(pattern, replace_improper_citation, text)
    
    # Clean up artifacts from removals (e.g., empty parens, spaces before punctuation)
    cleaned_text = re.sub(r'\s+([.,?!:;])', r'\1', cleaned_text)  # Fix space before punctuation
    cleaned_text = re.sub(r'\(\s*\)|\[\s*\]', '', cleaned_text)      # Remove empty parens/brackets
    # Preserve line breaks while normalizing spaces within lines
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Collapse spaces and tabs only
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)  # Collapse multiple line breaks to max 2
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text


def remove_control_blocks(text: str) -> str:
    """Remove control blocks from AI responses for user display.
    
    Control blocks like <control>{"objective_complete": true}</control> are used
    internally for system logic but should not be shown to users.
    
    Parameters
    ----------
    text : str
        AI response text that may contain control blocks
        
    Returns
    -------
    str
        Text with control blocks removed
    """
    if not text:
        return text
    
    # Remove control blocks using the same regex pattern as extract_control_block
    cleaned_text = CONTROL_TAG_RE.sub('', text)
    
    # Clean up any leftover whitespace but preserve line breaks for formatting
    # Only collapse multiple spaces on the same line, not line breaks
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)  # Collapse spaces and tabs only
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)  # Collapse multiple line breaks to max 2
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

# ---------------------------------------------------------------------------
# Control‑block extraction + validation helper
# ---------------------------------------------------------------------------

CONTROL_TAG_RE = re.compile(r"<control>(.*?)</control>", re.S)


def extract_control_block(
    assistant_text: str,
    schema: Optional[dict[str, Any]] | None = None,
) -> Optional[dict[str, Any]]:
    """Extract and (optionally) validate a JSON control block.

    Parameters
    ----------
    assistant_text : str
        Full assistant message including possible <control>{…}</control>.
    schema : dict | None
        JSON‑schema to validate against. If None, skip validation.

    Returns
    -------
    dict | None
        Parsed JSON object if found; else None.
    """
    m = CONTROL_TAG_RE.search(assistant_text)
    if not m:
        return None

    try:
        ctrl = json.loads(m.group(1))
    except json.JSONDecodeError:
        raise ValueError("Control block JSON malformed")

    if schema is not None and jsonschema is not None:
        jsonschema.validate(ctrl, schema)

    return ctrl
