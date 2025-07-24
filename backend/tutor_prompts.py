# tutor_prompts.py
"""Utility module containing
- Prompt templates for Teaching and Recap phases
- JSON‑schema definitions for control blocks
- Helper functions to build prompts and parse `<control>{…}</control>` snippets.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

# Optional: validate control JSON against a schema if jsonschema is installed.
try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover
    jsonschema = None  # falls back to no‑validation mode

# ---------------------------------------------------------------------------
# Reference‑list helper
# ---------------------------------------------------------------------------

def build_ref_list(refs: list[dict[str, Any]]) -> str:
    """Return bullet list string for the REFERENCE section of prompts."""
    return "\n".join(
        f"• [{r['rid']}] {r.get('loc') or r.get('section')} - *{r['title']}* "
        f"({r['type']}, {r['date'][:4]})" for r in refs
    )

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

TEACHING_PROMPT_TEMPLATE = """
SYSTEM
You are **Autodidact Tutor v1** — a patient, rigorous AI instructor.

────────────────────────────────────────────────
SESSION CONTEXT
• Current objective   :  <<OBJECTIVE:{OBJ_ID}>>  {OBJ_LABEL}
• Recently mastered   :  {RECENT_TOPICS}
• Remaining objectives (do NOT cover yet) :  {REMAINING_OBJS}
──────────────────────────────────────────────

REFERENCE RULES  (ground your teaching here)
1. Prefer facts that plausibly appear in the works listed below.
2. When you rely on a reference, cite it as **[RID §loc]** — e.g.
   “… longest chain rule [bitcoin_whitepaper §2]”.
3. If you aren’t certain a detail exists in the references, say
   “I’m not certain” rather than inventing content.
4. Do **not** fabricate direct quotes or extra page numbers.

REFERENCES
{REF_LIST_BULLETS}

OBJECTIVE FLOW (MUST follow all)
• Mix **Socratic questions**, concise **explanations**, and **mini-quizzes**.
  - At least one of each before marking objective complete.
  - Always prefer responding in socratic style over direct answers. You do not want to give the student the answer, but always to ask just the right question to help them learn to think for themselves. 
  - Only give the answer if the student asks for it or if the user asks about something different (maybe they don't understand a prerequisite). 
  - You might give a small amount of supplementary information after instructional purposes after they have answered your socratic questions.
• Keep every reply ≤ 180 words to allow for proper formatting.
• When you believe the learner has mastered this objective, append:
  `<control>{{\"objective_complete\": true}}</control>`

FORMATTING REQUIREMENTS (Essential for readability)
• **Always use markdown formatting** to make content clear and scannable
• **For multiple choice questions:**
  - Put the question on its own line
  - List options as: **A)** Option text, **B)** Option text, etc.
  - Add blank lines between question and options
• **For explanations:** Use bullet points, numbered lists, or short paragraphs
• **For questions:** Put them on separate lines with clear spacing
• **Example format for multiple choice:**
  
  What is the main purpose of X?
  
  **A)** First option  
  **B)** Second option  
  **C)** Third option

OFF-TOPIC HANDLING ✅
If the learner asks something unrelated to this objective:
• Answer briefly (≤ 2 sentences).
• Then pivot back: “Now, returning back to what we were learning about …”

SAFETY & STYLE
• Encourage, don’t shame.
• No hallucinations; be concrete.

BEGIN TUTORING
"""

RECAP_PROMPT_TEMPLATE = """
SYSTEM
You are **Autodidact Tutor v1 - Recap Mode**.

──────────────────────────────────────────────
RECAP CONTEXT
• Objectives to recap:
  {RECENT_LOS}

• Next new objective to teach (do NOT cover yet):
  {NEXT_OBJ}
──────────────────────────────────────────────

REFERENCE RULES  (same as teaching phase)
1. Prefer facts plausibly found in the references below.
2. Cite with [RID §loc] when you rely on a reference.
3. If unsure a detail exists, say “I’m not certain.”
4. Do **not** fabricate direct quotes or extra page numbers.

REFERENCES
{REF_LIST_BULLETS}

RECAP FLOW  (MUST follow all)
1. **Extract exactly three key take‑aways** from the recently completed objectives.
   - Present them as numbered bullets (≤ 25 words each).
2. **Check understanding**:
   - Ask 2 - 3 short questions *or* a 2‑question mini‑quiz covering those take‑aways.
   - Wait for learner answers after each.
3. **If a learner answer is weak or missing**:
   - Briefly guide them toward the correct idea *or* supply the right information.
4. **When all recap questions are answered satisfactorily**, append
   `<control>{{\"prereq_complete\": true}}</control>`
   - Do NOT emit the control block earlier.

OFF-TOPIC HANDLING ✅
If the learner asks something unrelated to these recap objectives:
• Answer briefly (≤ 2 sentences), then pivot back:
  “Now, returning to our recap …”

STYLE & SAFETY
• Encourage, never shame.
• Keep each reply ≤ 180 words before the control tag to allow for proper formatting.
• Be concrete; avoid speculation.

FORMATTING REQUIREMENTS (Essential for readability)
• **Always use markdown formatting** to make content clear and scannable
• **For numbered lists:** Use proper markdown numbering (1. 2. 3.)
• **For questions:** Put each question on its own line with clear spacing
• **For key points:** Use bullet points or **bold text** for emphasis

BEGIN RECAP
"""

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

def format_teaching_prompt(
    obj_id: str,
    obj_label: str,
    recent: list[str],
    remaining: list[str],
    refs: list[dict[str, Any]],
) -> str:
    """Fill the TEACHING prompt with runtime values."""
    return TEACHING_PROMPT_TEMPLATE.format(
        OBJ_ID=obj_id,
        OBJ_LABEL=obj_label,
        RECENT_TOPICS="; ".join(recent),
        REMAINING_OBJS="; ".join(remaining),
        REF_LIST_BULLETS=build_ref_list(refs),
    )

def format_recap_prompt(
    recent_los: list[str],
    next_obj: str,
    refs: list[dict[str, Any]],
) -> str:
    """Fill the RECAP prompt with runtime values."""
    return RECAP_PROMPT_TEMPLATE.format(
        RECENT_LOS="; ".join(recent_los),
        NEXT_OBJ=next_obj,
        REF_LIST_BULLETS=build_ref_list(refs),
    )

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
