# backend/quiz_grader.py
"""Lightweight LLM‑based grader for the final quiz.

Returns per‑question scores (0‒1) and an overall average.
No persistence; everything lives in memory until the wrap phase.
"""

from __future__ import annotations

import json
from typing import List, Tuple

from langchain_openai import ChatOpenAI
from utils.config import load_api_key
from utils.providers import get_model_for_task, get_provider_config, get_current_provider

# Initialize grader LLM using provider layer
def _get_grader_llm():
    """Get or create the grader LLM instance using the current provider."""
    provider = get_current_provider()
    api_key = load_api_key(provider)
    
    if not api_key:
        raise ValueError(f"No API key configured for provider: {provider}")
    
    # Get provider configuration
    config = get_provider_config(provider)
    chat_model = get_model_for_task("chat", provider)
    
    # Create ChatOpenAI instance with provider-specific settings
    llm_kwargs = {
        "model_name": chat_model,
        "temperature": 0,           # deterministic scoring
        "openai_api_key": api_key,
    }
    
    # Add base_url if provider requires it (e.g., OpenRouter)
    if config.get("base_url"):
        llm_kwargs["base_url"] = config["base_url"]
    
    # Add OpenRouter app attribution headers if using OpenRouter
    if provider == "openrouter":
        from utils.config import APP_NAME, APP_URL
        llm_kwargs["default_headers"] = {
            "HTTP-Referer": APP_URL,
            "X-Title": APP_NAME,
        }
    
    return ChatOpenAI(**llm_kwargs)

_GRADER_SYSTEM_PROMPT = (
    "You are a strict but fair examiner. "
    "Read the question and the learner's answer, then reply with *only* a JSON "
    "object on a single line in the form {\"score\": <float 0-1>, \"feedback\": <str>} . "
    "Score 1.0 means fully correct; 0.5 partially correct; 0.0 incorrect or blank."
)

_JSON_TAG = "```json"  # guard against code‑block wrapping

def _grade_one(llm: ChatOpenAI, question: str, answer: str) -> Tuple[float, str]:
    """Grade a single Q/A pair. Returns (score, feedback)."""
    user_prompt = f"Question:\n{question}\n\nLearner answer:\n{answer}"
    resp = llm([
        {"role": "system", "content": _GRADER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]).content.strip()

    # tolerate code‑block fences
    if resp.startswith(_JSON_TAG):
        resp = resp.removeprefix(_JSON_TAG).rstrip("`").strip()
    try:
        data = json.loads(resp)
        return float(data.get("score", 0.0)), str(data.get("feedback", ""))
    except Exception:
        return 0.0, "Could not parse grader output"


def grade_test(llm: ChatOpenAI, questions: List[str], answers: List[str]) -> Tuple[List[float], float]:
    """Grade aligned lists of questions & answers. Missing answers → score 0."""
    scores: List[float] = []
    for q, a in zip(questions, answers + [""] * (len(questions) - len(answers))):
        score, _ = _grade_one(llm, q, a)
        scores.append(score)
    overall = sum(scores) / len(scores) if scores else 0.0
    return scores, overall


def grade_test_with_current_provider(questions: List[str], answers: List[str]) -> Tuple[List[float], float]:
    """Grade test using the current provider. Convenience function."""
    llm = _get_grader_llm()
    return grade_test(llm, questions, answers)
