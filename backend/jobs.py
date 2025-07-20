"""
Jobs module for Autodidact
Contains: clarifier agent, deep research wrapper, grader, and tutor nodes
"""

import json
import re
import time
import logging
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import openai
from openai import OpenAI
from utils.config import load_api_key, get_current_provider
from utils.providers import create_client, get_model_for_task, get_provider_info, ProviderError, get_api_call_params
from utils.deep_research import TOPIC_CLARIFYING_PROMPT, TOPIC_REWRITING_PROMPT

logger = logging.getLogger(__name__)


def extract_citations_from_annotations(response):
    """
    Extract citation information from Perplexity response annotations.
    
    Args:
        response: OpenAI response object with annotations
        
    Returns:
        dict: Mapping of citation numbers to URL information
    """
    citations = {}
    if not hasattr(response, 'choices') or not response.choices:
        return citations
        
    choice = response.choices[0]
    if not hasattr(choice, 'message') or not choice.message:
        return citations
        
    annotations = getattr(choice.message, 'annotations', [])
    if not annotations or not hasattr(annotations, '__iter__'):
        return citations
    
    # Create mapping of citation indices to URLs
    citation_index = 1
    for annotation in annotations:
        if hasattr(annotation, 'type') and annotation.type == 'url_citation':
            url_citation = getattr(annotation, 'url_citation', None)
            if url_citation:
                citations[citation_index] = {
                    'url': getattr(url_citation, 'url', ''),
                    'title': getattr(url_citation, 'title', ''),
                    'start_index': getattr(url_citation, 'start_index', 0),
                    'end_index': getattr(url_citation, 'end_index', 0)
                }
                citation_index += 1
    
    logger.info(f"Extracted {len(citations)} citations from Perplexity response")
    return citations


def enhance_resources_with_citations(resources, citations, content):
    """
    Enhance resource entries with citation URLs from Perplexity annotations.
    
    Args:
        resources: List of resource dictionaries
        citations: Dictionary mapping citation numbers to URL info
        content: The response content with numbered citations
        
    Returns:
        list: Enhanced resources with citation URLs
    """
    if not citations or not resources:
        return resources
    
    enhanced_resources = []
    for resource in resources:
        enhanced_resource = resource.copy()
        
        # If the resource doesn't have a URL, try to find one from citations
        if not enhanced_resource.get('url') or enhanced_resource.get('url') == '#':
            # Look for citation markers in the resource title or scope
            title = enhanced_resource.get('title', '')
            scope = enhanced_resource.get('scope', '')
            
            # Find citation numbers that might correspond to this resource
            for cite_num, cite_info in citations.items():
                cite_title = cite_info.get('title', '')
                cite_url = cite_info.get('url', '')
                
                # Simple matching: if citation title appears in resource title or vice versa
                if (cite_title and title and 
                    (cite_title.lower() in title.lower() or title.lower() in cite_title.lower())):
                    enhanced_resource['url'] = cite_url
                    enhanced_resource['citation_source'] = f"Citation [{cite_num}]"
                    logger.info(f"Enhanced resource '{title}' with citation URL: {cite_url}")
                    break
        
        enhanced_resources.append(enhanced_resource)
    
    return enhanced_resources


def process_perplexity_response(response, response_content):
    """
    Process Perplexity response to extract citations and enhance the curriculum.
    
    Args:
        response: OpenAI response object
        response_content: Raw response content string
        
    Returns:
        str: Processed response content with enhanced resources
    """
    try:
        # Extract citations from annotations
        citations = extract_citations_from_annotations(response)
        
        # Try to parse JSON from the response content
        curriculum_data = None
        try:
            # Look for JSON at the end of the content
            lines = response_content.split('\n')
            json_start = None
            
            for i, line in enumerate(lines):
                if line.strip().startswith('```json') or line.strip() == '{':
                    json_start = i
                    break
            
            if json_start is not None:
                # Extract the JSON part
                if lines[json_start].strip().startswith('```json'):
                    json_start += 1
                
                json_lines = []
                for i in range(json_start, len(lines)):
                    line = lines[i]
                    if line.strip() == '```':
                        break
                    json_lines.append(line)
                
                json_text = '\n'.join(json_lines)
                curriculum_data = json.loads(json_text)
                logger.info("Successfully parsed curriculum JSON from Perplexity response")
                
                # Enhance resources with citations
                if 'resources' in curriculum_data and citations:
                    curriculum_data['resources'] = enhance_resources_with_citations(
                        curriculum_data['resources'], citations, response_content
                    )
                
                # Reconstruct the content with enhanced JSON
                enhanced_json = json.dumps(curriculum_data, indent=2)
                
                # Replace the JSON part in the original content
                new_lines = lines[:json_start]
                new_lines.append('```json')
                new_lines.extend(enhanced_json.split('\n'))
                new_lines.append('```')
                
                enhanced_content = '\n'.join(new_lines)
                return enhanced_content
                
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Could not parse JSON from Perplexity response: {e}")
        
        # If we have citations but couldn't parse JSON, at least log the citations
        if citations:
            logger.info(f"Found {len(citations)} citations in Perplexity response:")
            for cite_num, cite_info in citations.items():
                logger.info(f"  [{cite_num}] {cite_info['title']}: {cite_info['url']}")
        
        return response_content
        
    except Exception as e:
        logger.error(f"Error processing Perplexity response: {e}")
        return response_content


def optimize_prompt_for_perplexity(base_prompt):
    """
    Optimize the prompt specifically for Perplexity's deep research capabilities.
    
    Args:
        base_prompt: The original developer prompt
        
    Returns:
        str: Optimized prompt for Perplexity
    """
    perplexity_additions = """

PERPLEXITY-SPECIFIC INSTRUCTIONS:
- Leverage your web search capabilities to find the most current and authoritative resources
- Include specific publication dates and author information when available
- Provide URLs to high-quality, accessible learning materials
- Use your citations to support resource recommendations
- Focus on resources that are freely accessible or widely available
- Include recent developments and current best practices in the field
- Ensure all URLs are functional and lead to educational content

ENHANCED CITATION REQUIREMENTS:
- When referencing sources, use numbered citations [1][2][3] in your narrative text
- Ensure each citation corresponds to a specific, verifiable source
- Prioritize academic papers, established educational platforms, and authoritative websites
- Include a mix of foundational and cutting-edge resources

OUTPUT FORMAT REMINDER:
- Provide both the comprehensive curriculum explanation AND the final JSON structure
- Ensure the JSON contains actionable learning objectives and resource pointers
- Make sure resource URLs are real and functional"""

    return base_prompt + perplexity_additions


# Debugging infrastructure for API responses
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
        
        logger.info(f"DEBUG: Saved raw API response to {debug_file}")
        return str(debug_file)
        
    except Exception as e:
        logger.error(f"ERROR: Failed to save raw API response: {e}")
        return None


# Constants for retry logic
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def get_token_count(response) -> str:
    """
    Extract token count from API response, handling both object and dict formats.
    
    Args:
        response: API response object
        
    Returns:
        str: Token count as string or 'n/a' if not available
    """
    usage_info = getattr(response, 'usage', None)
    if usage_info:
        if hasattr(usage_info, 'total_tokens'):
            return str(usage_info.total_tokens)
        elif isinstance(usage_info, dict):
            return str(usage_info.get('total_tokens', 'n/a'))
    return 'n/a'


def retry_api_call(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """Retry API calls with exponential backoff"""
    last_error = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except openai.RateLimitError as e:
            wait_time = RETRY_DELAY * (2 ** attempt)
            logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
            time.sleep(wait_time)
            last_error = e
        except openai.APIError as e:
            if attempt < max_retries - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.warning(f"API error, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                last_error = e
            else:
                raise
        except Exception as e:
            logger.error(f"Non-API error during API call: {type(e).__name__}: {str(e)}")
            raise
    logger.error(f"Failed after {max_retries} attempts. Last error: {str(last_error)}")
    raise RuntimeError(f"Failed after {max_retries} attempts. Last error: {str(last_error)}")


def clarify_topic(topic: str, hours: Optional[int] = None) -> List[str]:
    """
    Generate clarifying questions for a given topic using TOPIC_CLARIFYING_PROMPT.
    Always returns questions to ask the user.
    
    Args:
        topic: The learning topic
        hours: Optional number of hours the user wants to invest
        
    Returns:
        List of clarifying questions
    """
    logger.info(f"Starting clarification for topic: '{topic}'")
    if hours:
        logger.info(f"User wants to invest {hours} hours")

    # Create client using provider abstraction
    try:
        client = create_client()
    except ProviderError as e:
        logger.error(f"Provider configuration error: {str(e)}")
        raise ValueError(f"Provider configuration error: {str(e)}")

    # Prepare user message
    user_msg = f"Topic: {topic}"
    if hours:
        user_msg += f"\nTime investment: {hours} hours"

    logger.info(f"Using model: {get_model_for_task('chat')}")
    logger.debug(f"User message: {user_msg}")

    try:
        # Call API with retry logic using chat model
        def make_clarifier_call():
            params = get_api_call_params(
                model=get_model_for_task("chat"),
                messages=[
                    {"role": "system", "content": TOPIC_CLARIFYING_PROMPT},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )
            logger.info(f"[API CALL] Reason: Topic clarification | Model: {params.get('model')} | Provider: {get_provider_info(params.get('model', 'openai')).get('name', 'unknown')}")
            return client.chat.completions.create(**params)

        logger.info("Making API call for topic clarification...")
        response = retry_api_call(make_clarifier_call)
        
        # DEBUG: Save raw response
        save_raw_api_response(response, "clarify_topic")
        
        meta = getattr(response, 'meta', None) or getattr(response, 'metadata', None) or {}
        logger.info(f"[API RETURN] Topic clarification complete | Model: {get_model_for_task('chat')} | Tokens: {get_token_count(response)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")

        # Extract the response content with proper null checks
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise ValueError("Invalid response structure: missing or empty choices")
        
        if not response.choices[0] or not hasattr(response.choices[0], 'message') or not response.choices[0].message:
            raise ValueError("Invalid response structure: missing or empty message")
        
        questions_text = response.choices[0].message.content
        if not questions_text:
            raise ValueError("Invalid response structure: empty content")
        
        questions_text = questions_text.strip()
        logger.debug(f"Raw response:\n{questions_text}")

        # Parse the questions from the response
        questions = []
        lines = questions_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or 
                        (len(line) > 2 and line[0].isdigit() and line[1] in '.)')):
                question = re.sub(r'^[-•*\d.)\s]+', '', line).strip()
                if question:
                    questions.append(question)

        if not questions:
            logger.info("No bullet points found, trying to split by sentences")
            sentences = re.split(r'[?!.]\s+', questions_text)
            questions = [s.strip() + '?' if not s.strip().endswith('?') else s.strip() 
                        for s in sentences if s.strip() and len(s.strip()) > 10]

        logger.info(f"Extracted {len(questions)} questions")
        for i, q in enumerate(questions, 1):
            logger.debug(f"Q{i}: {q}")

        return questions

    except openai.AuthenticationError:
        logger.error("Authentication failed")
        raise RuntimeError("Invalid API key. Please check your API key configuration.")
    except openai.PermissionDeniedError:
        logger.error("Permission denied")
        raise RuntimeError("API key doesn't have access to the required model.")
    except ProviderError as e:
        logger.error(f"Provider error: {str(e)}")
        raise RuntimeError(f"Provider configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Clarifier API call failed: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Clarifier API call failed: {str(e)}")


def rewrite_topic(initial_topic: str, questions: List[str], user_answers: str) -> str:
    """
    Rewrite the topic based on clarifying questions and user answers.
    
    Args:
        initial_topic: The original topic from the user
        questions: List of clarifying questions that were asked
        user_answers: User's answers to all questions in a single string
        
    Returns:
        Rewritten, detailed topic instruction
    """
    logger.info(f"Starting topic rewriting")
    logger.info(f"Initial topic: '{initial_topic}'")
    logger.info(f"Number of questions: {len(questions)}")
    logger.info(f"User answers length: {len(user_answers)} chars")
    
    # Create client using provider abstraction
    try:
        client = create_client()
    except ProviderError as e:
        raise ValueError(f"Provider configuration error: {str(e)}")
    
    # Format the content for the rewriting prompt
    formatted_content = f"""Initial topic: {initial_topic}

Clarifying questions:
"""
    for i, question in enumerate(questions, 1):
        formatted_content += f"{i}. {question}\n"
    
    formatted_content += f"\nUser's responses:\n{user_answers}"
    
    logger.debug(f"Formatted content for API:\n{formatted_content}")
    logger.info(f"Using model: {get_model_for_task('chat')}")
    
    try:
        def make_rewriter_call():
            params = get_api_call_params(
                model=get_model_for_task("chat"),
                messages=[
                    {"role": "system", "content": TOPIC_REWRITING_PROMPT},
                    {"role": "user", "content": formatted_content}
                ],
                temperature=0.7
            )
            logger.info(f"[API CALL] Reason: Topic rewriting | Model: {params.get('model')} | Provider: {get_provider_info(params.get('model', 'openai')).get('name', 'unknown')}")
            return client.chat.completions.create(**params)

        logger.info("Making API call for topic rewriting...")
        response = retry_api_call(make_rewriter_call)
        
        # DEBUG: Save raw response
        save_raw_api_response(response, "rewrite_topic")
        
        meta = getattr(response, 'meta', None) or getattr(response, 'metadata', None) or {}
        logger.info(f"[API RETURN] Topic rewriting complete | Model: {get_model_for_task('chat')} | Tokens: {get_token_count(response)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")
        
        # Extract the rewritten topic with proper null checks
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise ValueError("Invalid response structure: missing or empty choices")
        
        if not response.choices[0] or not hasattr(response.choices[0], 'message') or not response.choices[0].message:
            raise ValueError("Invalid response structure: missing or empty message")
        
        rewritten_topic = response.choices[0].message.content
        if not rewritten_topic:
            raise ValueError("Invalid response structure: empty content")
        
        rewritten_topic = rewritten_topic.strip()
        logger.info(f"Rewritten topic:\n{rewritten_topic}")
        
        return rewritten_topic
        
    except Exception as e:
        logger.error(f"ERROR: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Failed to rewrite topic: {str(e)}")


def is_skip_response(response: str) -> bool:
    """Check if response is a non-answer using regex patterns"""
    skip_pattern = re.compile(r'^\s*(idk|i don\'t know|skip|na|n/a|none)\s*$', re.IGNORECASE)
    return bool(skip_pattern.match(response.strip()))


def process_clarification_responses(questions: List[str], responses: List[str]) -> str:
    """
    Process user responses to clarification questions and create refined topic
    """
    # Filter out skip responses
    valid_responses = []
    for i, (q, r) in enumerate(zip(questions, responses)):
        if not is_skip_response(r):
            valid_responses.append(f"Q: {q}\nA: {r}")
    
    if not valid_responses:
        return None  # No valid responses, use original topic
    
    # Create client using provider abstraction
    try:
        client = create_client()
    except ProviderError as e:
        raise ValueError(f"Provider configuration error: {str(e)}")
    
    # Create prompt to refine topic based on responses
    refinement_prompt = """
    Based on the following clarification Q&A, create a refined, specific learning topic.
    
    Original topic and clarification Q&A:
    {qa_text}
    
    Return only the refined topic as a clear, specific statement.
    """
    
    qa_text = "\n\n".join(valid_responses)
    
    try:
        def make_refinement_call():
            params = get_api_call_params(
                model=get_model_for_task("chat"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that refines learning topics based on user input."},
                    {"role": "user", "content": refinement_prompt.format(qa_text=qa_text)}
                ],
                temperature=0.7
            )
            logger.info(f"[API CALL] Reason: Topic refinement | Model: {params.get('model')} | Provider: {get_provider_info(params.get('model', 'openai')).get('name', 'unknown')}")
            return client.chat.completions.create(**params)

        logger.info("Making API call for topic refinement...")
        response = retry_api_call(make_refinement_call)
        
        # DEBUG: Save raw response
        save_raw_api_response(response, "process_clarification_responses")
        
        meta = getattr(response, 'meta', None) or getattr(response, 'metadata', None) or {}
        logger.info(f"[API RETURN] Topic refinement complete | Model: {get_model_for_task('chat')} | Tokens: {get_token_count(response)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")
        
        # Extract response content with proper null checks
        if not response or not hasattr(response, 'choices') or not response.choices:
            raise ValueError("Invalid response structure: missing or empty choices")
        
        if not response.choices[0] or not hasattr(response.choices[0], 'message') or not response.choices[0].message:
            raise ValueError("Invalid response structure: missing or empty message")
        
        response_content = response.choices[0].message.content
        if not response_content:
            raise ValueError("Invalid response structure: empty content")
        
        return response_content.strip()
        
    except Exception as e:
        raise RuntimeError(f"Failed to process clarification responses: {e}")


# def run_deep_research_job(topic: str, hours: Optional[int] = None) -> Dict:
#     """
#     Wrapper for Deep Research API call with error handling and partial result recovery.
#     Adapted from 02-topic-then-deep-research.py
    
#     Returns:
#         Dict with report_markdown, graph, and resources
#     """
#     print(f"\n[run_deep_research_job] Starting deep research")
#     print(f"[run_deep_research_job] Topic: '{topic}'")
#     if hours:
#         print(f"[run_deep_research_job] Hours: {hours}")
    
#     # Get API key and create client
#     api_key = load_api_key()
#     if not api_key:
#         raise ValueError("OpenAI API key not found. Please configure your API key.")
    
#     client = OpenAI(api_key=api_key)
    
#     try:
#         # Call the deep research API
#         print("[run_deep_research_job] Calling deep research API...")
#         job_id = start_deep_research_job(topic, hours)

#         # Poll for completion
#         resp = poll_background_job(client, job_id)
        
#         if resp.status != "completed":
#             raise RuntimeError(f"Job ended with status {resp.status}")

#         # Extract the final assistant message
#         content_block = resp.output[-1].content[0]
#         result = wait_for_deep_research_out(job_id)
        
#         print("[run_deep_research_job] Deep research completed, validating results...")
        
#         # Validate result has required fields
#         if "report_markdown" not in result:
#             # Try to salvage partial results
#             if "graph" in result:
#                 result["report_markdown"] = f"# {topic}\n\n*Note: Report generation failed, but knowledge graph was created successfully.*"
#             else:
#                 raise ValueError("Missing report_markdown in Deep Research result")
        
#         if "graph" not in result:
#             raise ValueError("Missing graph in Deep Research result")
        
#         # Ensure graph has required structure
#         if "nodes" not in result["graph"]:
#             result["graph"]["nodes"] = []
#         if "edges" not in result["graph"]:
#             result["graph"]["edges"] = []
        
#         if "resources" not in result:
#             result["resources"] = {}  # Default to empty if missing
        
#         print(f"[run_deep_research_job] Found {len(result['graph']['nodes'])} nodes and {len(result['graph']['edges'])} edges")
        
#         # Validate nodes have learning objectives
#         for i, node in enumerate(result["graph"]["nodes"]):
#             if "learning_objectives" not in node or not node["learning_objectives"]:
#                 print(f"[run_deep_research_job] Warning: Node '{node.get('label', 'unknown')}' missing learning objectives, generating defaults")
#                 # Generate placeholder objectives if missing
#                 node["learning_objectives"] = [
#                     f"Understand the key concepts of {node['label']}",
#                     f"Apply {node['label']} principles in practice",
#                     f"Analyze relationships between {node['label']} and related topics",
#                     f"Evaluate different approaches to {node['label']}",
#                     f"Create solutions using {node['label']} knowledge"
#                 ]
        
#         print("[run_deep_research_job] Deep research validation complete")
#         return result
        
#     except openai.AuthenticationError:
#         print("[run_deep_research_job] ERROR: Authentication failed")
#         raise RuntimeError("Invalid API key. Please check your OpenAI API key.")
#     except openai.PermissionDeniedError:
#         print("[run_deep_research_job] ERROR: Permission denied")
#         raise RuntimeError("API key doesn't have access to Deep Research model.")
#     except openai.RateLimitError:
#         print("[run_deep_research_job] ERROR: Rate limit exceeded")
#         raise RuntimeError("Rate limit exceeded. Please try again in a few minutes.")
#     except openai.APIError as e:
#         print(f"[run_deep_research_job] ERROR: OpenAI API error: {str(e)}")
#         raise RuntimeError(f"OpenAI API error: {str(e)}")
#     except Exception as e:
#         print(f"[run_deep_research_job] ERROR: {type(e).__name__}: {str(e)}")
#         raise RuntimeError(f"Deep Research failed: {str(e)}") 


def start_deep_research_job(topic: str, hours: Optional[int] = None, oldAttemptSalvagedTxt: str = None, research_model: str = None) -> str:
    """
    Start a deep research job and return the job_id immediately.
    For OpenAI: Uses background jobs that run on their servers.
    For Perplexity: Creates a pseudo job_id and executes immediately (may take 4-5 minutes).
    
    Args:
        topic: The learning topic (already refined/rewritten)
        hours: Optional number of hours the user wants to invest
        
    Returns:
        str: The job ID for polling (OpenAI) or pseudo-ID for immediate execution (Perplexity)
    """
    logger.info(f"[API CALL] Reason: Start deep research | Topic: {topic} | Hours: {hours if hours else 'n/a'}")
    if hours:
        logger.info(f"User wants to invest {hours} hours")
    
    # Create client using provider abstraction
    try:
        client = create_client()
        current_provider = get_current_provider()
    except ProviderError as e:
        raise ValueError(f"Provider configuration error: {str(e)}")
    
    try:
        # Import the DEVELOPER_PROMPT from deep_research module
        from utils.deep_research import DEVELOPER_PROMPT
        
        # Get the appropriate model for deep research
        try:
            research_model = research_model or get_model_for_task("deep_research")
        except ProviderError:
            # Fallback to chat model if deep research not available
            logger.info(f"Deep research model not available for {current_provider}, using chat model")
            research_model = research_model or get_model_for_task("chat")
        
        logger.info(f"Using provider: {current_provider}")
        logger.info(f"Using model: {research_model}")
        
        # Check if this provider supports deep research features
        provider_info = get_provider_info(current_provider)
        supports_deep_research = provider_info.get("supports_deep_research", False)
        
        # Prepare the user message with optional hours
        user_message = f"Topic: {topic}"
        if hours:
            user_message += f"\n\nTime user wants to invest to study: {hours} hours"
            target_nodes = min(max(hours * 2, 4), 40)
            user_message += f"\nTarget node count ≈ {target_nodes} (keep between {target_nodes - 2} and {target_nodes + 2})."
        user_message += "\nPlease follow the developer instructions."

        if oldAttemptSalvagedTxt:
            user_message += "\n\n"+oldAttemptSalvagedTxt
        
        logger.debug(f"User message: {user_message}")
        
        # Handle different provider approaches
        if current_provider == "openai" and supports_deep_research:
            # OpenAI approach: Use background jobs with responses.create()
            input_messages = [
                {
                    "role": "developer",
                    "content": [{"type": "input_text", "text": DEVELOPER_PROMPT}]
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_message}]
                }
            ]

            # Tools configuration
            tools = [{"type": "web_search_preview"}]
            
            logger.info("Submitting OpenAI deep-research background job...")
            resp = client.responses.create(
                model=research_model,
                background=True,
                input=input_messages,
                tools=tools,
                reasoning={"summary": "auto"},
            )
            meta = getattr(resp, 'meta', None) or getattr(resp, 'metadata', None) or {}
            logger.info(f"[API RETURN] Deep research job submitted | Model: {research_model} | Job ID: {resp.id} | Tokens: {get_token_count(resp)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")
            
            job_id = resp.id
            # Clean the job ID in case it contains control characters
            from backend.db import clean_job_id
            cleaned_job_id = clean_job_id(job_id)
            logger.info(f"OpenAI job submitted successfully with ID: {cleaned_job_id}")
            
            return cleaned_job_id
            
        elif current_provider == "openrouter" and "perplexity" in research_model.lower():
            # Perplexity approach: Run in a background thread, immediately return job ID
            logger.info("Using Perplexity Sonar Deep Research (background thread)...")
            import uuid, threading, json
            from pathlib import Path
            pseudo_job_id = f"perplexity-{str(uuid.uuid4())[:8]}"
            from utils.config import PERPLEXITY_DEEP_RESEARCH_TIMEOUT
            temp_dir = Path.home() / '.autodidact' / 'temp_responses'
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"{pseudo_job_id}.json"

            # Write initial status as 'queued'
            with open(temp_file, 'w') as f:
                json.dump({
                    "status": "queued",
                    "content": None,
                    "model": research_model,
                    "provider": current_provider
                }, f)

            def run_perplexity_job():
                try:
                    long_timeout_client = openai.OpenAI(
                        api_key=client.api_key,
                        base_url=client.base_url,
                        timeout=PERPLEXITY_DEEP_RESEARCH_TIMEOUT
                    )
                    
                    # Optimize prompt for Perplexity's deep research capabilities
                    optimized_prompt = optimize_prompt_for_perplexity(DEVELOPER_PROMPT)
                    
                    logger.info(f"[API CALL] Reason: Perplexity deep research | Model: {research_model} | Provider: {current_provider} | Job ID: {pseudo_job_id}")
                    response = long_timeout_client.chat.completions.create(
                        model=research_model,
                        messages=[
                            {"role": "system", "content": optimized_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.7,
                        timeout=PERPLEXITY_DEEP_RESEARCH_TIMEOUT
                    )
                    
                    # DEBUG: Save raw response
                    save_raw_api_response(response, "perplexity_deep_research", pseudo_job_id)
                    
                    meta = getattr(response, 'meta', None) or getattr(response, 'metadata', None) or {}
                    logger.info(f"[API RETURN] Perplexity deep research complete | Model: {research_model} | Job ID: {pseudo_job_id} | Tokens: {get_token_count(response)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")
                    
                    # Safely extract response content with proper null checks
                    if not response or not hasattr(response, 'choices') or not response.choices:
                        raise ValueError("Invalid response structure: missing or empty choices")
                    
                    if not response.choices[0] or not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                        raise ValueError("Invalid response structure: missing or empty message")
                    
                    response_content = response.choices[0].message.content
                    if not response_content:
                        raise ValueError("Invalid response structure: empty content")
                    
                    # Enhanced Perplexity processing: extract citations and optimize content
                    processed_content = process_perplexity_response(response, response_content)
                    response_content = processed_content
                    
                    with open(temp_file, 'w') as f:
                        json.dump({
                            "status": "completed",
                            "content": response_content,
                            "model": research_model,
                            "provider": current_provider
                        }, f)
                    logger.info(f"Completed and stored result for {pseudo_job_id}")
                except Exception as e:
                    with open(temp_file, 'w') as f:
                        json.dump({
                            "status": "failed",
                            "content": str(e),
                            "model": research_model,
                            "provider": current_provider
                        }, f)
                    logger.error(f"[API RETURN] Perplexity deep research failed | Model: {research_model} | Job ID: {pseudo_job_id} | Error: {e}")

            threading.Thread(target=run_perplexity_job, daemon=True).start()
            logger.info(f"Perplexity job {pseudo_job_id} started in background thread.")
            return pseudo_job_id
            
        else:
            # Fallback approach: Use regular chat completion
            logger.info(f"[API CALL] Reason: Fallback chat completion | Model: {research_model} | Provider: {current_provider}")
            params = get_api_call_params(
                model=research_model,
                messages=[
                    {"role": "system", "content": DEVELOPER_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            response = client.chat.completions.create(**params)
            
            # DEBUG: Save raw response
            save_raw_api_response(response, "fallback_research")
            
            meta = getattr(response, 'meta', None) or getattr(response, 'metadata', None) or {}
            logger.info(f"[API RETURN] Fallback chat completion complete | Model: {research_model} | Tokens: {get_token_count(response)} | Price: {meta.get('price', 'n/a')} | Meta: {meta}")
            
            # Generate a pseudo job ID and store response
            import uuid
            pseudo_job_id = f"chat-{str(uuid.uuid4())[:8]}"
            
            # Store the response temporarily
            from pathlib import Path
            temp_dir = Path.home() / '.autodidact' / 'temp_responses'
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / f"{pseudo_job_id}.json"
            
            import json
            
            # Safely extract response content with proper null checks
            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Invalid response structure: missing or empty choices")
            
            if not response.choices[0] or not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                raise ValueError("Invalid response structure: missing or empty message")
            
            response_content = response.choices[0].message.content
            if not response_content:
                raise ValueError("Invalid response structure: empty content")
            
            with open(temp_file, 'w') as f:
                json.dump({
                    "status": "completed",
                    "content": response_content,
                    "model": research_model,
                    "provider": current_provider
                }, f)
            
            return pseudo_job_id
        
    except openai.AuthenticationError:
        logger.error("Authentication failed")
        raise RuntimeError("Invalid API key. Please check your API key configuration.")
    except openai.PermissionDeniedError:
        logger.error("Permission denied")
        raise RuntimeError("API key doesn't have access to the required model.")
    except openai.APITimeoutError:
        logger.error("Request timeout")
        raise RuntimeError("Deep research request timed out. Perplexity requests can take 4-5 minutes.")
    except ProviderError as e:
        logger.error(f"Provider error: {str(e)}")
        raise RuntimeError(f"Provider configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        raise RuntimeError(f"Failed to start research job: {str(e)}") 


def test_job():
    print("test: run the jobs")
    try:
        client = create_client()
    except ProviderError as e:
        raise ValueError(f"Provider configuration error: {str(e)}")

    from utils.deep_research import test_data, deep_research_output_cleanup

    input_data = test_data
    val = deep_research_output_cleanup(input_data, client)
    print(f"[test_job] Val: {val}")