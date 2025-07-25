"""
Deep Research module for Autodidact
Refactored from 02-topic-then-deep-research.py
"""

import json
import time
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import openai
from openai import OpenAI
from utils.config import DEEP_RESEARCH_POLL_INTERVAL
from utils.providers import create_client, get_model_for_task, get_current_provider, get_provider_info, get_api_call_params

import jsonschema, networkx as nx, Levenshtein


# Debugging infrastructure for API responses (copied from backend/jobs.py)
def save_raw_api_response(response, context: str, job_id: str = None):
    """Save raw API response to temp directory for debugging"""
    try:
        # Create debug directory
        debug_dir = Path.home() / '.autodidact' / 'debug_responses'
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds to milliseconds
        job_suffix = f"_{job_id}" if job_id else ""
        filename = f"{timestamp}_{context}{job_suffix}_raw.txt"
        debug_file = debug_dir / filename
        
        # Save raw response - handle various response types
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f"=== RAW API RESPONSE DEBUG ===\n")
            f.write(f"Context: {context}\n")
            f.write(f"Job ID: {job_id or 'N/A'}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Response Type: {type(response)}\n")
            f.write("=" * 50 + "\n\n")
            
            # Try to serialize the response in different ways
            try:
                # First try to convert to dict if it's an object
                if hasattr(response, '__dict__'):
                    f.write("=== RESPONSE AS DICT ===\n")
                    f.write(str(response.__dict__))
                    f.write("\n\n")
                
                # Try JSON serialization
                f.write("=== RESPONSE AS JSON ===\n")
                if hasattr(response, 'model_dump'):
                    # Pydantic object
                    f.write(json.dumps(response.model_dump(), indent=2, default=str))
                elif hasattr(response, 'to_dict'):
                    # Objects with to_dict method
                    f.write(json.dumps(response.to_dict(), indent=2, default=str))
                else:
                    # Try direct JSON serialization
                    f.write(json.dumps(response, indent=2, default=str))
                f.write("\n\n")
                
            except Exception as json_error:
                f.write(f"JSON serialization failed: {json_error}\n")
                f.write("=== RESPONSE AS STRING ===\n")
                f.write(str(response))
                f.write("\n\n")
            
            # Try to extract key fields for analysis
            try:
                f.write("=== KEY FIELDS ANALYSIS ===\n")
                f.write(f"Has 'choices' attribute: {hasattr(response, 'choices')}\n")
                if hasattr(response, 'choices'):
                    f.write(f"choices value: {response.choices}\n")
                    f.write(f"choices type: {type(response.choices)}\n")
                    if response.choices:
                        f.write(f"choices length: {len(response.choices) if response.choices else 'None'}\n")
                        if len(response.choices) > 0:
                            f.write(f"choices[0]: {response.choices[0]}\n")
                            f.write(f"choices[0] type: {type(response.choices[0])}\n")
                            if hasattr(response.choices[0], 'message'):
                                f.write(f"choices[0].message: {response.choices[0].message}\n")
                                if hasattr(response.choices[0].message, 'content'):
                                    f.write(f"choices[0].message.content: {response.choices[0].message.content}\n")
                f.write("\n")
                
                # Check for other common fields
                common_fields = ['id', 'object', 'created', 'model', 'usage', 'error']
                for field in common_fields:
                    if hasattr(response, field):
                        f.write(f"Has '{field}': {getattr(response, field)}\n")
                        
            except Exception as analysis_error:
                f.write(f"Key fields analysis failed: {analysis_error}\n")
        
        print(f"DEBUG: Saved raw API response to {debug_file}")
        return str(debug_file)
        
    except Exception as e:
        print(f"ERROR: Failed to save raw API response: {e}")
        return None


def clean_job_id(job_id: str) -> str:
    """
    Clean job_id by removing all control characters including newlines, tabs, etc.
    
    Args:
        job_id: The raw job ID that may contain control characters
        
    Returns:
        Cleaned job ID with all control characters removed
    """
    if not job_id:
        return ""
    
    # Remove all control characters including \n, \r, \t, \f, \v, \0
    # Keep only printable ASCII characters and spaces
    cleaned = re.sub(r'[\r\n\t\f\v\0]', '', job_id.strip())
    
    return cleaned

# After we get the user's topic & time investment preferences, this prompt is used to ask clarifying questions to the user
TOPIC_CLARIFYING_PROMPT = """
You will be given a short topic that a user wants to learn alongside the time they want to invest. Your job is NOT to answer it or complete the task, but instead to ask clarifying questions that would help a syllabus planner to understand what exactly the user wants to learn.

GUIDELINES:
1. **Focus on Learning Scope & Learner Profile**
- Consider what information would change the structure, depth, or direction for the specialized learning plan, and ask questions to clarify.
  - For example, you might want to ask questions to clarify what aspects of the topic the user is interested in, what if any background knowledge they have, their purpose for learning, etc.
- things to avoid asking about: preferred learning method or media formats (since our system will be chat-bot driven)

2. **Do Not Invent Preferences**
- If the user did not mention a preference, *do not assume it*. Ask about it clearly and neutrally. When giving options, they should be relevant to the subject matter.

3. **Use the First Person**
- Phrase your questions from the perspective of the assistant or researcher talking to the user (e.g., “Could you clarify...” or “Do you have a preference for...”)

4. **Use a Bulleted List if Multiple Questions**
- If there are multiple open questions, list them clearly in bullet format for readability.

5. **Avoid Overasking**
- Prioritize the 4-6 questions that would most reduce ambiguity or scope creep. You don’t need to ask *everything*, just the most pivotal unknowns.

6. **Format for Conversational Use**
- The output should sound helpful and conversational—not like a form. Aim for a natural tone while still being precise.
"""

# This prompt will be passed the user's topic, clarifying questions, and their responses.
# It will be used to rewrite the topic into a more specific and detailed topic instruction, which will finally be passed into the deep research prompt.
TOPIC_REWRITING_PROMPT = """
You will be given an initial topic by the user, followed by clarifying questions, followed by the user's responses. Your job is to rewrite these into a concise detailed topic instruction.

GUIDELINES:
1. **Maximize Specificity and Detail**
- Include all known user preferences and explicitly list key attributes or dimensions to consider.
- It is of utmost importance that all details from the user are included in the instructions.

2. **Avoid Unwarranted Assumptions**
- If the user has not provided a particular detail, do not invent one.
- Instead, state the lack of specification and guide the planner to treat it as flexible or accept all possible options.

3. **Important details first**
- The first sentence should contain be a complete sentence saying what the user wants to learn, and further sentences should flesh all relevant details out.

4. **Use the First Person**
- Phrase the request from the perspective of the user.
"""


# Updated developer prompt to include learning objectives
DEVELOPER_PROMPT = """
You are a “Deep-Research Curriculum Architect” with the goal of making the optimal learning syllabus for motivated autodidacts on the topic user asks of you.

TASK 1 - RESOURCES
- You will be given a topic and a time investment preference.
- Identify 10-15 authoritative, learner-friendly resources suitable for motivated autodidacts on the specified topic.
- Return them as a JSON array **resources** with:
  { "rid", "title", "type", "url", "date", "scope" }
  - type ∈ {book | paper | video | interactive | article | library}.
  - scope = one-sentence summary.
- An example resource:
  {
    "rid": "bitcoin_whitepaper",
    "title": "Bitcoin: A Peer-to-Peer Electronic Cash System (Whitepaper)",
    "type": "paper",
    "url": "https://bitcoin.org/bitcoin.pdf",
    "date": "2008-10-31",
    "scope": "Original whitepaper by Satoshi Nakamoto introducing Bitcoin's design and goals."
  }

TASK 2 - GRAPH
- Decompose the topic into into the number of learning "nodes" specified in the user input. Nodes should build on each other and each should be scoped to ~30 minutes of focused study.
- Each node should have a "title" and a list of 5-7 "learning_objectives", which detail what the user will learn in this node. Use Bloom verbs, <=12 words for each.
- Each non-root node has 1-3 "prerequisite_node_ids", each of which are ids for nodes in the graph (other nodes one should learn before this)
- The "prerequisite_node_ids" are what define the edges of the graph, which should be a directed acyclic knowledge graph.
  - Avoid isolated nodes or overly linear chains. The graph should feel like a branching river, not a single track or scattered islands.
  - Aim for ≥ 10% roots (no prerequisites) and ≥15% leaves (no dependants)
  - Every prerequisite_node_id **must exactly match an “id” for a node that appears in this JSON**
  - The graph should support multiple learning paths. At most steps, the user should have 2–4 valid “next” nodes they can choose from. Paths may diverge and later converge.
- A node should have "resource_pointers" to sections of resources. Use only "rid" values present in **resources**. Omit if no specific section of a resource maps well to the node
- An example node for clarifying schema:
  {
    "id": "bitcoin-consensus-mechanism",                  // unique  
    "title": "Consensus Mechanisms in Bitcoin",  
    "prerequisite_node_ids": ["bitcoin-whitepaper-intro", "distributed-systems-basics"],
    "learning_objectives": [             
      "Explain the role of proof-of-work in consensus",
      "Calculate the difficulty adjustment formula",
      "Describe the impact of mining pools", 
    ],
    "resource_pointers": [                        // pointers into resources
      { "rid": "mastering_bitcoin_2e", "section": "Ch.8 §Difficulty" },
      { "rid": "bitcoin_whitepaper", "section": "4. Proof-of-Work" }
    ]
  }

TASK 3 - CONSOLIDATE AND RETURN FINAL VALID JSON
- Return **one valid JSON object** with keys `"resources"` and `"nodes"`. no comments, no markdown.
- Any non-JSON text will be discarded.
"""


def poll_background_job(client: OpenAI, job_id: str) -> Dict:
    """Poll until a background deep-research job is complete."""
    # Clean job_id to remove any control characters including embedded newlines
    clean_job_id_value = clean_job_id(job_id)
    
    while True:
        job = client.responses.retrieve(clean_job_id_value)
        status = job.status
        if status in ("completed", "failed", "cancelled", "expired"):
            return job
        print(f"[{time.strftime('%H:%M:%S')}] Job {clean_job_id_value} → {status} …")
        time.sleep(DEEP_RESEARCH_POLL_INTERVAL)



SCHEMA = {
  "type": "object",
  "properties": {
    "resources": {
      "type": "array",
      "items": {
        "type":"object",
        "required":["rid","title","type","url"],
        "properties":{
          "rid":{"type":"string"},
          "title":{"type":"string"},
          "type":{"enum":["book","paper","video","interactive","article","library"]},
          "url":{"type":"string","format":"uri"}
        }
      }
    },
    "nodes": {
      "type":"array",
      "items":{
        "type":"object",
        "required":["id","title","learning_objectives"],
        "properties":{
          "id":{"type":"string"},
          "title":{"type":"string"},
          "prerequisite_node_ids":{"type":"array","items":{"type":"string"}},
          "learning_objectives":{"type":"array","minItems":2,"maxItems":9},
          "resource_pointers":{"type":"array",
              "items":{"type":"object",
                       "required":["rid","section"],
                       "properties":{"rid":{"type":"string"},"section":{"type":"string"}}}
          }
        }
      }
    }
  },
  "required":["resources","nodes"]
}

def lint(payload:str)->list[str]:
    """Return list of error strings or [] if valid."""
    errors=[]
    try:
        data=json.loads(payload)
    except Exception as e:
        return [f"Invalid JSON: {e}"]
    try:
        jsonschema.validate(data, SCHEMA)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema error: {e.message}")
    # ---- custom checks ----
    node_ids={n["id"] for n in data["nodes"]}
    rid_set={r["rid"] for r in data["resources"]}
    # dangling prereqs
    for n in data["nodes"]:
        for p in n.get("prerequisite_node_ids",[]):
            if p not in node_ids:
                errors.append(f"Node '{n['id']}' has unknown prerequisite '{p}'")
    # dangling rid refs
    for n in data["nodes"]:
        for s in n.get("resource_pointers",[]):
            if s["rid"] not in rid_set:
                errors.append(f"Node '{n['id']}' references unknown rid '{s['rid']}'")
    # cycles
    g=nx.DiGraph([(p,n["id"]) for n in data["nodes"] for p in n.get("prerequisite_node_ids",[])])
    try:
        nx.find_cycle(g,orientation="original")
        errors.append("Graph contains a prerequisite cycle")
    except nx.exception.NetworkXNoCycle:
        pass
    return errors

JSON_GUARDIAN_PROMPT = """
You are a “JSON Repair Assistant”.
Below is RAW_JSON followed by ERRORS detected by our validator.
• Return a **single corrected JSON object**—no comments, no markdown.
• Fix each error.  Strategies:
  1. If a prerequisite or rid is a near-miss typo, rename to the closest existing id (Levenshtein ≤ 2).
  2. Otherwise delete that prerequisite / section entry.
  3. Add missing brackets/commas to make valid JSON.
• Do NOT invent new nodes or resources beyond what exists.
• Preserve field order; keep text unchanged unless required to fix an error.

RAW_JSON:
<<<
{raw_json}
>>>

ERRORS:
{error_bullets}
"""

def guardian_fixer(raw_json_str, error_bullets, client, high_model=False):
    prompt = JSON_GUARDIAN_PROMPT.format(
        raw_json=raw_json_str,
        error_bullets="\n".join(f"• {e}" for e in error_bullets)
    )
    print(f"[deep_research_output_cleanup] Prompt: {prompt}")
    
    current_provider = get_current_provider()
    provider_info = get_provider_info(current_provider)
    
    # For OpenAI, use the o4-mini model if available, otherwise fallback
    if current_provider == "openai" and high_model:
        model_to_use = "o4-mini"
        print(f"[deep_research_output_cleanup] Model: {model_to_use}")
        start = time.perf_counter()
        resp = client.responses.create(
              model=model_to_use,
              input=[{"role": "user", "content": prompt}],
              reasoning={"summary": "auto"}
            )
        elapsed = time.perf_counter() - start
        print(f"Guardian pass finished in {elapsed:.2f} s")
        return resp.output_text
    else:
        # For other providers or low model, use regular chat completion
        chat_model = get_model_for_task("chat")
        print(f"[deep_research_output_cleanup] Model: {chat_model}")
        start = time.perf_counter()
        params = get_api_call_params(
            model=chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        resp = client.chat.completions.create(**params)
        
        # DEBUG: Save raw response
        save_raw_api_response(resp, "guardian_fixer")
        
        elapsed = time.perf_counter() - start
        print(f"Guardian pass finished in {elapsed:.2f} s")
        
        # Extract response content with proper null checks
        if not resp or not hasattr(resp, 'choices') or not resp.choices:
            raise ValueError("Invalid response structure: missing or empty choices")
        
        if not resp.choices[0] or not hasattr(resp.choices[0], 'message') or not resp.choices[0].message:
            raise ValueError("Invalid response structure: missing or empty message")
        
        response_content = resp.choices[0].message.content
        if not response_content:
            raise ValueError("Invalid response structure: empty content")
        
        return response_content

def extract_json_from_markdown(content: str) -> str:
    """
    Extract JSON content from markdown code blocks or by trimming intro text.
    
    Args:
        content: Raw content that may contain JSON wrapped in markdown or with intro text
        
    Returns:
        Extracted JSON string, or original content if no JSON found
    """
    lines = content.split('\n')
    json_start = -1
    json_end = -1
    
    # First, look for ```json ... ``` blocks
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '```json':
            json_start = i + 1
        elif stripped == '```' and json_start != -1:
            json_end = i
            break
    
    if json_start != -1 and json_end != -1:
        json_lines = lines[json_start:json_end]
        extracted_json = '\n'.join(json_lines)
        print(f"[extract_json_from_markdown] Extracted JSON from markdown (length: {len(extracted_json)} chars)")
        # Validate that we got actual JSON content
        if extracted_json.strip().startswith('{') and extracted_json.strip().endswith('}'):
            return extracted_json
        else:
            print(f"[extract_json_from_markdown] Warning: Extracted content doesn't look like JSON, using original")
            return content
    
    # If no markdown blocks found, try to find JSON by looking for the first line with '{'
    print(f"[extract_json_from_markdown] No JSON markdown block found, trying to find JSON start")
    
    # Look for the first line that starts with '{' (ignoring whitespace)
    json_start_line = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('{'):
            json_start_line = i
            break
    
    if json_start_line != -1:
        # Now find the matching closing brace by counting brace balance
        brace_count = 0
        json_end_line = -1
        for i in range(json_start_line, len(lines)):
            line = lines[i]
            for char in line:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end_line = i
                        break
            if json_end_line != -1:
                break
        
        if json_end_line != -1:
            # Extract the JSON content
            json_lines = lines[json_start_line:json_end_line + 1]
            json_candidate = '\n'.join(json_lines).strip()
            
            # Basic validation: should start with '{' and end with '}'
            if json_candidate.startswith('{') and json_candidate.endswith('}'):
                print(f"[extract_json_from_markdown] Found JSON by trimming intro text (length: {len(json_candidate)} chars)")
                return json_candidate
            else:
                print(f"[extract_json_from_markdown] Found '{{' but content doesn't look like valid JSON structure")
        else:
            print(f"[extract_json_from_markdown] Found opening '{{' but no matching closing '}}'")
    
    # If no JSON structure found, return original content
    print(f"[extract_json_from_markdown] No JSON found, using original content")
    return content


def deep_research_output_cleanup(raw_json_str, client):
    # First, try to extract JSON from markdown if present
    extracted_content = extract_json_from_markdown(raw_json_str)
    
    # lint and if error, passes to higher model to fix
    errs = lint(extracted_content)
    print(f"[deep_research_output_cleanup] first lint: Errs: {errs}")
    if not errs:
        return extracted_content
    else:
        current_provider = get_current_provider()
        print(f"[deep_research_output_cleanup] Trying to fix with chat model for {current_provider}")
        fixed = guardian_fixer(extracted_content, errs, client, high_model=False)
        errs2 = lint(fixed)
        if not errs2:
            return fixed
        else: 
            if current_provider == "openai":
                print(f"[deep_research_output_cleanup] Trying to fix with o4-mini")
                fixed = guardian_fixer(fixed, errs2, client, high_model=True)
                errs3 = lint(fixed)
                if not errs3:
                    return fixed
                else:
                    raise RuntimeError(f"[deep_research_output_cleanup] Failed to fix with both models")
            else:
                raise RuntimeError(f"[deep_research_output_cleanup] Failed to fix with {current_provider} chat model")

test_data = """
{
  "resources": [
    {
      "rid": "bitcoin_whitepaper2",
      "title": "Bitcoin: A Peer-to-Peer Electronic Cash System",
      "type": "paper",
      "url": "https://bitcoin.org/bitcoin.pdf",
      "date": "2008-10-31",
      "scope": "Original whitepaper by Satoshi Nakamoto introducing Bitcoin\u2019s design and goals."
    },
    {
      "rid": "mastering_bitcoin_2e",
      "title": "Mastering Bitcoin, 2nd Ed.",
      "type": "book",
      "url": "https://www.oreilly.com/library/view/mastering-bitcoin-2nd/9781491954379/",
      "date": "2021-01-13",
      "scope": "Comprehensive, developer-friendly guide to Bitcoin\u2019s protocol, mining and security."
    },
    {
      "rid": "digital_gold",
      "title": "Digital Gold: Bitcoin and the Inside Story of the Misfits and Millionaires Trying to Reinvent Money",
      "type": "book",
      "url": "https://www.harpercollins.com/products/digital-gold-nathaniel-popper",
      "date": "2015-05-19",
      "scope": "Narrative history of Bitcoin\u2019s early years and key personalities (2009-2014)."
    },
    {
      "rid": "bitcoin_standard",
      "title": "The Bitcoin Standard",
      "type": "book",
      "url": "https://saifedean.com/the-bitcoin-standard",
      "date": "2018-04-24",
      "scope": "Explores Bitcoin\u2019s monetary history, fixed supply and economic implications."
    },
    {
      "rid": "3b1b_bitcoin_video",
      "title": "But How Does Bitcoin Actually Work? (3Blue1Brown)",
      "type": "video",
      "url": "https://www.3blue1brown.com/lessons/bitcoin",
      "date": "2025-05-04",
      "scope": "Visual 30-minute lesson on ledgers, proof-of-work, mining and blockchains."
    },
    {
      "rid": "forbes_bitcoin_intro",
      "title": "What Is Bitcoin? How Does It Work? \u2013 Forbes Advisor",
      "type": "article",
      "url": "https://www.forbes.com/advisor/investing/cryptocurrency/what-is-bitcoin/",
      "date": "2024-06-08",
      "scope": "Plain-English explainer covering Bitcoin basics, history and supply cap."
    },
    {
      "rid": "ledger_most_btc",
      "title": "Who Owns the Most Bitcoin? \u2013 Ledger Academy",
      "type": "article",
      "url": "https://www.ledger.com/academy/topics/crypto/who-owns-the-most-bitcoin-the-largest-bitcoin-wallet-addresses",
      "date": "2025-03-20",
      "scope": "Breakdown of largest known wallets, Satoshi\u2019s stash, corporate and ETF holdings."
    },
    {
      "rid": "bitinfo_rich_list",
      "title": "Top 100 Richest Bitcoin Addresses & Distribution Charts",
      "type": "interactive",
      "url": "https://bitinfocharts.com/en/top-100-richest-bitcoin-addresses.html",
      "date": "2025-07-08",
      "scope": "Live dashboard of address balances and ownership distribution statistics."
    },
    {
      "rid": "btc_treasuries",
      "title": "BitcoinTreasuries.net \u2013 Public & Private Entities Holding BTC",
      "type": "interactive",
      "url": "https://bitcointreasuries.net/",
      "date": "2025-07-09",
      "scope": "Continuously-updated list of corporate treasuries and ETFs with Bitcoin on balance sheets."
    },
    {
      "rid": "whitehouse_btc_reserve",
      "title": "Executive Order: Establishment of the U.S. Strategic Bitcoin Reserve",
      "type": "article",
      "url": "https://www.whitehouse.gov/presidential-actions/2025/03/establishment-of-the-strategic-bitcoin-reserve-and-united-states-digital-asset-stockpile/",
      "date": "2025-03-06",
      "scope": "Official policy detailing U.S. federal Bitcoin holdings and custodial framework."
    },
    {
      "rid": "reuters_ath_2025",
      "title": "Bitcoin Surges to Record $116,000 amid Institutional Demand",
      "type": "article",
      "url": "https://www.reuters.com/world/middle-east/dollar-catches-breath-brazil-real-slides-tariff-threat-bitcoin-near-record-high-2025-07-10/",
      "date": "2025-07-10",
      "scope": "News timeline summarising 2023-25 price milestones and policy catalysts."
    },
    {
      "rid": "vaneck_chaincheck",
      "title": "VanEck Bitcoin ChainCheck Dashboard \u2013 April 2025",
      "type": "article",
      "url": "https://www.vaneck.com/corp/en/news-and-insights/blogs/digital-assets/matthew-sigel-vaneck-mid-april-2025-bitcoin-chaincheck/",
      "date": "2025-04-14",
      "scope": "On-chain metrics on supply dormancy, holder categories and miner activity."
    }
  ],
  "nodes": [
    {
      "id": "bitcoin-origins-whitepaper",
      "title": "Bitcoin Origins & Whitepaper Fundamentals",
      "learning_objectives": [
        "Describe problems Bitcoin set out to solve",
        "Summarize whitepaper\u2019s peer-to-peer model",
        "Explain role of proof-of-work in consensus",
        "Identify genesis block and first 50 BTC",
        "Contrast Bitcoin with earlier e-cash attempts",
        "Define key terms: block, hash, timestamp"
      ],
      "resource_pointers": [
        {
          "rid": "bitcoin_whitepaper",
          "section": "\u00a71\u2013\u00a76"
        },
        {
          "rid": "digital_gold",
          "section": "Ch.1 \u2018Genesis\u2019"
        }
      ]
    },
    {
      "id": "early-adoption-2010-2014",
      "title": "Early Adoption & Milestones (2010-2014)",
      "prerequisite_node_ids": [
        "bitcoin-origins-whitepaper"
      ],
      "learning_objectives": [
        "Recall first Bitcoin transaction and Pizza Day",
        "Discuss Mt. Gox and Silk Road impacts",
        "Outline emergence of exchanges and wallets",
        "Explain regulatory firsts (FinCEN 2013)",
        "Assess community growth metrics by 2014",
        "Describe media perception in early years"
      ],
      "resource_pointers": [
        {
          "rid": "digital_gold",
          "section": "Ch.6 \u2018Gox Rising\u2019"
        },
        {
          "rid": "reuters_ath_2025",
          "section": "Timeline 2009-14 inset"
        }
      ]
    },
    {
      "id": "supply-halving-mechanics",
      "title": "Bitcoin Supply, Halvings & Monetary Policy",
      "prerequisite_node_ids": [
        "bitcoin-origins-whitepaper"
      ],
      "learning_objectives": [
        "Explain 21 million cap and issuance schedule",
        "Calculate block reward changes after halvings",
        "Interpret miner incentives and difficulty",
        "Relate scarcity narrative to store-of-value",
        "Compare inflation rates pre- and post-2024 halving",
        "Analyze supply-active metrics from on-chain data"
      ],
      "resource_pointers": [
        {
          "rid": "mastering_bitcoin_2e",
          "section": "Ch.8 \u00a7Difficulty & Halving"
        },
        {
          "rid": "bitcoin_standard",
          "section": "Ch.8 \u2018Sound Money\u2019"
        },
        {
          "rid": "vaneck_chaincheck",
          "section": "Supply tables"
        }
      ]
    },
    {
      "id": "major-price-milestones",
      "title": "Major Price Milestones & Market Catalysts",
      "prerequisite_node_ids": [
        "early-adoption-2010-2014",
        "supply-halving-mechanics"
      ],
      "learning_objectives": [
        "Chart BTC price from $0.01 to $116k",
        "Correlate halvings with bull cycles",
        "Identify ETF approvals and policy impacts",
        "Evaluate institutional FOMO narratives",
        "Discuss volatility and drawdown patterns"
      ],
      "resource_pointers": [
        {
          "rid": "reuters_ath_2025",
          "section": "All-time-high report"
        }
      ]
    },
    {
      "id": "address-distribution-basics",
      "title": "Address Structure & Ownership Distribution",
      "prerequisite_node_ids": [
        "bitcoin-origins-whitepaper",
        "supply-halving-mechanics"
      ],
      "learning_objectives": [
        "Differentiate address vs. wallet concepts",
        "Navigate public ledger to trace balances",
        "Summarize Glassnode long-/short-term holders",
        "Calculate % supply on exchanges",
        "Discuss privacy limits of pseudonymity",
        "Interpret distribution charts by size"
      ],
      "resource_pointers": [
        {
          "rid": "forbes_bitcoin_intro",
          "section": "\u2018Public Ledger\u2019 section"
        },
        {
          "rid": "bitinfo_rich_list",
            "section": "Distribution pie chart"
        }
      ]
    },
    {
      "id": "major-whales-and-wallets",
      "title": "Satoshi & Other Major Whales",
      "prerequisite_node_ids": [
        "address-distribution-basics"
      ],
      "learning_objectives": [
        "Estimate Satoshi\u2019s dormant holdings",
        "Rank top exchange-controlled wallets",
        "Differentiate custodian vs. proprietary funds",
        "Assess whale influence on liquidity",
        "Explain proof-of-reserves concepts",
        "Evaluate risks of concentrated ownership"
      ],
      "resource_pointers": [
        {
          "rid": "ledger_most_btc",
          "section": "\u2018Top Bitcoin Holders\u2019"
        },
        {
          "rid": "bitinfo_rich_list",
          "section": "Top 10 addresses table"
        }
      ]
    },
    {
      "id": "corporate-bitcoin-treasuries",
      "title": "Corporate & ETF Bitcoin Treasuries",
      "prerequisite_node_ids": [
        "major-whales-and-wallets"
      ],
      "learning_objectives": [
        "Identify leading public-company BTC holders",
        "Compare MicroStrategy vs. ETFs like IBIT",
        "Analyze balance-sheet motivations",
        "Calculate treasury % of circulating supply",
        "Discuss accounting and regulatory factors",
        "Summarize 2025 surge in corporate adoption"
      ],
      "resource_pointers": [
        {
          "rid": "btc_treasuries",
          "section": "Top 10 companies table"
        }
      ]
    },
    {
      "id": "government-bitcoin-holdings",
      "title": "Government Bitcoin Reserves & Seizures",
      "prerequisite_node_ids": [
        "corporate-bitcoin-treasuries"
      ],
      "learning_objectives": [
        "List nations publicly holding BTC",
        "Explain U.S. strategic reserve policy",
        "Quantify estimated 200k BTC U.S. holdings",
        "Contrast seizure-based vs. purchase-based reserves",
        "Debate geopolitical implications of state BTC",
        "Assess transparency challenges in sovereign wallets"
      ],
      "resource_pointers": [
        {
          "rid": "whitehouse_btc_reserve",
          "section": "Sec.1-4"
        },
        {
          "rid": "ledger_most_btc",
          "section": "\u2018What Country Owns the Most Bitcoin?\u2019"
        }
      ],
    },
    {
      "id": "onchain-analysis-tools",
      "title": "Hands-On: Using On-Chain Analysis Tools",
      "learning_objectives": [
        "Use block explorers to trace transactions",
        "Query rich-list and supply dashboards",
        "Visualize dormancy and HODL waves",
        "Verify exchange proof-of-reserves claims",
        "Apply hash-rate and difficulty charts",
        "Interpret data limitations and biases"
      ],
      "resource_pointers": [
        {
          "rid": "3b1b_bitcoin_video",
          "section": "\u2018Creating a Blockchain\u2019 segment"
        },
        {
          "rid": "bitinfo_rich_list",
          "section": "Explorer UI"
        }
      ],
    },
    {
      "id": "interpreting-ownership-landscape",
      "title": "Interpreting the 2025 Ownership Landscape",
      "prerequisite_node_ids": [
        "address-distribution-basics",
        "onchain-analysis-tools"
      ],
      "learning_objectives": [
        "Synthesize data from whales, corporates, governments",
        "Evaluate concentration vs. decentralization trends",
        "Estimate long-term vs. short-term holder ratios",
        "Forecast impact of ETF growth on ownership",
        "Debate future scenarios for BTC distribution",
        "Formulate personal risk assessment strategies"
      ],
      "resource_pointers": [
        {
          "rid": "vaneck_chaincheck",
          "section": "Holder composition metrics"
        },
        {
          "rid": "ledger_most_btc",
          "section": "Summary conclusions"
        }
      ],
    }
  ]
}
"""

