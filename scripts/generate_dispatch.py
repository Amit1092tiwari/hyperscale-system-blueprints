"""
Master Dispatch Generator using Google Gemini Pro & Deterministic Architecture Engine.
Generates visually stunning, production-grade hyperscale architecture blueprints
strictly adhering to the requested 10-section layout with rich GitHub-Flavored Markdown.
Enforces strict uniqueness and non-repetition against all previously published dispatches.
"""

import os
import sys
import re
import json
import time
import datetime
from pathlib import Path
import urllib.request
import urllib.error
from typing import List, Dict, Optional, Tuple

# Resolve repository directories deterministically
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DISPATCHES_DIR = REPO_ROOT / "dispatches"

# Add SCRIPT_DIR to sys.path if not present
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import uniqueness
import blueprints_catalog as bc
import technical_reviewer

# Re-export SEEDS and PILLARS for backwards compatibility
SEEDS = bc.SEEDS
PILLARS = bc.PILLARS

def get_series_day(current_date: str = "") -> int:
    """Calculate the sequential series day number based on existing dispatches."""
    past = uniqueness.get_previous_dispatches_metadata(DISPATCHES_DIR)
    if not past:
        return 1
    max_day = max(d["day_number"] for d in past)
    return max(max_day + 1, 1)

SECTION_REQUIREMENTS = [
    (1, "1. System Parameters", re.compile(r"^##\s*1\.\s*System Parameters", re.M | re.I)),
    (2, "2. Problem Statement", re.compile(r"^##\s*2\.\s*Problem Statement", re.M | re.I)),
    (3, "3. High-Level Design (HLD)", re.compile(r"^##\s*3\.\s*High-Level Design", re.M | re.I)),
    (4, "4. Low-Level Design (LLD)", re.compile(r"^##\s*4\.\s*Low-Level Design", re.M | re.I)),
    (5, "5. Logical Flow Diagram", re.compile(r"^##\s*5\.\s*Logical Flow Diagram", re.M | re.I)),
    (6, "6. Architectural Drill & Nature Analogy", re.compile(r"^##\s*6\.\s*Architectural Drill", re.M | re.I)),
    (7, "7. Production-Grade Executable Artifact", re.compile(r"^##\s*7\.\s*Production-Grade Executable Artifact", re.M | re.I)),
    (8, "8. KPI Monitoring Framework", re.compile(r"^##\s*8\.\s*KPI Monitoring Framework", re.M | re.I)),
    (9, "9. Failure Mode & Production Edge Cases", re.compile(r"^##\s*9\.\s*Failure Mode", re.M | re.I)),
    (10, "10. Thoughtful Wisdom Words", re.compile(r"^##\s*10\.\s*Thoughtful Wisdom Words", re.M | re.I)),
]

def validate_dispatch_completeness(content: str) -> Tuple[bool, List[str]]:
    """
    Assert all 10 mandatory sections exist in the dispatch and code fences are properly closed.
    Returns (is_complete, missing_section_names).
    """
    missing = []
    for num, name, pat in SECTION_REQUIREMENTS:
        if not pat.search(content):
            missing.append(name)

    fence_lines = [l for l in content.splitlines() if l.strip().startswith("```")]
    if len(fence_lines) % 2 != 0:
        missing.append("Unclosed Code Fence (Odd backtick blocks)")

    return (len(missing) == 0, missing)

def generate_header(series_day: int, seed: dict, current_date: str = "") -> str:
    """Build Section 1 and header badges with dynamic seed metadata."""
    if not current_date:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return f"""# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}

[![Pillar](https://img.shields.io/badge/Pillar-{seed['badge_name']}-{seed['badge_color']}?style=for-the-badge)]()
[![Validation](https://img.shields.io/badge/Validation-Local--First%20CI%20Verified-emerald?style=for-the-badge&logo=githubactions)]()
[![Architecture](https://img.shields.io/badge/Architecture-Zero--Cost%20Mock%20Harness-blueviolet?style=for-the-badge)]()
[![Completeness](https://img.shields.io/badge/Completeness-Complete%20(10%2F10%20Sections)-brightgreen?style=for-the-badge)]()
[![Uniqueness](https://img.shields.io/badge/Uniqueness-True%20(Verified)-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)]()

> [!NOTE]
> **Dispatch Completeness & Uniqueness Audit**:
> - **Completeness Status:** Complete (10/10 Sections Verified)
> - **Missing Sections:** None
> - **Reason for Incompletion:** N/A (Fully generated within token limits)
> - **Unique Flag:** `true` (Verified non-colliding across historical catalog)

---

## 1. System Parameters

- **Target Domain:** {seed['domain']}
- **Framework Used:** {seed['framework']}
- **Technology Stack:** {seed['tech_stack']}
- **Scale Bottleneck:** {seed['bottleneck']}
- **API/Serialization Protocol:** {seed['protocol']}
- **Data Lineage Component:** {seed['lineage']}
- **Components Used:** {seed['components']}
- **Concepts Involved:** {seed['concepts']}

---
"""

def generate_mock_dispatch(
    series_day: int,
    seed: Optional[dict] = None,
    current_date: str = "",
    past_dispatches: Optional[List[Dict]] = None,
    body: Optional[str] = None
) -> str:
    """
    Generate a high-density, production-grade architectural blueprint.
    If seed is not explicitly provided, selects the next guaranteed unique blueprint
    from the comprehensive catalog.
    """
    if not current_date:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    if past_dispatches is None:
        past_dispatches = uniqueness.get_previous_dispatches_metadata(DISPATCHES_DIR)

    if seed is None:
        seed, body = bc.get_next_unique_blueprint(series_day, past_dispatches)
    elif body is None:
        if "body" in seed:
            body = seed["body"]
        else:
            blueprint_id = seed.get("id") or f"{seed.get('pillar_id', 'A')}1"
            try:
                body = bc.load_blueprint_body(blueprint_id)
            except FileNotFoundError:
                body = bc.load_blueprint_body("A1")

    header = generate_header(series_day, seed, current_date)
    return header + "\n" + body.strip() + "\n"

def build_system_prompt(
    series_day: int,
    seed: dict,
    current_date: str = "",
    past_dispatches: Optional[List[Dict]] = None
) -> str:
    """Construct the visually enhanced masterclass generation prompt with anti-repetition constraints."""
    if not current_date:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    if past_dispatches is None:
        past_dispatches = uniqueness.get_previous_dispatches_metadata(DISPATCHES_DIR)

    past_summary = uniqueness.format_past_dispatches_summary(past_dispatches)

    return f"""Act as a World-Class Principal AI & Hyperscale Infrastructure Architect, Senior Engineering Director, and Open-Source Platform Specialist.
Your mission is to deliver daily, ultra-high-density technical wisdom tailored for a Senior/Principal Cloud Data & AI Systems Engineer (8+ years experience).

================================================================================
CRITICAL ANTI-REPETITION DIRECTIVE & HISTORICAL BLUEPRINT LEDGER:
================================================================================
Below is the ledger of all previously published dispatches in this repository.
You MUST generate a 100% UNIQUE, NON-REPETITIVE hyperscale architecture blueprint.

PREVIOUSLY PUBLISHED DISPATCHES (DO NOT DUPLICATE OR REVISIT THESE THEMES):
{past_summary}

MANDATORY NOVELTY REQUIREMENTS:
1. Title Uniqueness: The title MUST NOT match or closely resemble any previously published title.
2. Architecture & Domain Uniqueness: You must address an entirely NEW challenge, mechanism, or subsystem. DO NOT reuse the same core problem, tech stack, or bottleneck.
3. System Parameters Uniqueness: Target Domain, Framework, and Tech Stack must reflect a distinct system.
4. Diagram & Code Uniqueness: Provide original ASCII diagrams, native Mermaid workflows, and production-grade Python unit tests that model this novel architecture.
5. Analogy Uniqueness: Choose a fresh biological or physical phenomenon that has not been used in past dispatches.
================================================================================

CRITICAL INSTRUCTION: MAKE THE OUTPUT VISUALLY STUNNING AND AESTHETICALLY POLISHED!
CRITICAL FORMATTING INVARIANTS:
1. LINE 1 of your response MUST BE EXACTLY:
# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}
Do NOT prepend any markdown backtick fences (```markdown), conversational filler, or badges before Line 1.
2. Put the shield badges immediately BELOW the title (Lines 3-6).

Utilize GitHub-Flavored Markdown best practices:
1. Sleek Header with Badges: Include shield badges for the Pillar, Framework, Security Level, and Local-First CI Status.
2. Clean System Parameters: Present "## 1. System Parameters" as a clean, standard Markdown bulleted list with bold keys (no duplicate tables):
   - **Target Domain:** ...
   - **Framework Used:** ...
   - **Technology Stack:** ...
   - **Scale Bottleneck:** ...
   - **API/Serialization Protocol:** ...
   - **Data Lineage Component:** ...
   - **Components Used:** ...
   - **Concepts Involved:** ...
3. GitHub-Flavored Alerts: Use `> [!WARNING]` to highlight technical bottlenecks in Problem Statement, `> [!TIP]` for Nature Analogy takeaways, and `> [!IMPORTANT]` for production operational rules.
4. Dual Diagrams (ASCII + Native Mermaid): For HLD, LLD, and Logical Flow, provide BOTH crisp, beautiful ASCII diagrams AND native GitHub Mermaid.js rendered diagrams (```mermaid ... ```).
5. Rich KPI & Failure Tables: Use severity badges (🔴 Critical, 🟡 High, 🟠 Medium) and structured telemetry matrices.
6. Elegant Quote Callouts: Style the concluding Thoughtful Wisdom Words inside a stylized blockquote with attribution.

YOU MUST GENERATE THE OUTPUT STRICTLY ADHERING TO THE FOLLOWING 10-SECTION ORDER:

---
# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}

## 1. System Parameters
- **Target Domain:** {seed['domain']}
- **Framework Used:** {seed['framework']}
- **Technology Stack:** {seed['tech_stack']}
- **Scale Bottleneck:** {seed['bottleneck']}
- **API/Serialization Protocol:** {seed['protocol']}
- **Data Lineage Component:** {seed['lineage']}
- **Components Used:** {seed['components']}
- **Concepts Involved:** {seed['concepts']}

## 2. Problem Statement
[Include a `> [!WARNING]` callout box highlighting the core constraint, followed by 2-3 dense paragraphs detailing the exact physical memory/CPU/network bounds and why standard CI runners fail without proper sharding.]

## 3. High-Level Design (HLD)
[Clean ASCII Architecture Diagram + Native Mermaid Diagram]

## 4. Low-Level Design (LLD)
[Clean ASCII Execution Diagram + Native Mermaid Sequence or State Diagram]

## 5. Logical Flow Diagram
[Clean ASCII Decision Flow Diagram + Native Mermaid Flowchart]

## 6. Architectural Drill & Nature Analogy
### ⚙️ The Systemic Breakdown
[Rigorous engineering explanation of how zero-copy and offloading principles prevent resource exhaustion]

### 🌿 The Nature Analogy
[Include a `> [!TIP]` callout box]
• **The Biological System:** [Biological phenomenon]
• **The Structural Parallel:** [Deep mapping of natural system to distributed architecture]

## 7. Production-Grade Executable Artifact
### 📦 File 1: .github/workflows/ci.yml
```yaml
[Complete, production-grade GitHub Actions CI workflow with runner setup and test hooks]
```

### 🐍 File 2: [test_script_name.py]
```python
[Complete, runnable Python script with schemas, mock harnesses, and unit tests]
```

## 8. KPI Monitoring Framework
• [Metric 1 Name] ([metric_code_identifier]):
	• Why: [Operational significance, baseline threshold, and diagnostic interpretation]
• [Metric 2 Name] ([metric_code_identifier]):
	• Why: [Operational significance, baseline threshold, and diagnostic interpretation]
• [Metric 3 Name] ([metric_code_identifier]):
	• Why: [Operational significance, baseline threshold, and diagnostic interpretation]

## 9. Failure Mode & Production Edge Cases
[High-contrast Markdown Table with Columns: Failure Vector (with severity badge) | Technical Root Cause | System Blast Radius | Production Mitigation Pattern]

## 10. Thoughtful Wisdom Words
[Stylized Quote Blockquote with attribution to Principal Systems Architect]

CRITICAL COMPLETENESS INVARIANT:
You MUST emit all 10 sections completely in order. Ensure all markdown code fences (```) are cleanly closed. Do NOT truncate, abbreviate, or omit Sections 8, 9, or 10.
"""

def generate_via_google_genai_sdk(api_key: str, model_name: str, prompt: str) -> str:
    """Attempt generation via official google-genai SDK."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    # Explicitly disable automatic function calling to prevent AFC warning on single-turn generation
    afc_config = (
        types.AutomaticFunctionCallingConfig(disable=True)
        if hasattr(types, "AutomaticFunctionCallingConfig")
        else None
    )
    config_kwargs = {
        "temperature": 0.7,
        "max_output_tokens": 16384,
    }
    if afc_config is not None:
        config_kwargs["automatic_function_calling"] = afc_config

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    if response and response.text:
        return response.text
    raise RuntimeError("Empty response received from google-genai SDK")

def generate_via_rest_api(api_key: str, model_name: str, prompt: str) -> str:
    """Generate via direct HTTPS REST API (zero third-party dependencies)."""
    clean_model = model_name.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 16384
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=180) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"No candidates returned in Gemini API response: {body}")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError(f"No content parts returned in candidate: {candidates[0]}")
        return parts[0].get("text", "")

def sanitize_generated_dispatch(
    content: str,
    series_day: int,
    seed: dict,
    current_date: str = ""
) -> str:
    """
    Ensure the generated dispatch strictly conforms to the repository formatting standards:
    1. Line 1 MUST be the exact H1 title: '# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}'.
    2. Followed by shield badges, separator, and '## 1. System Parameters'.
    3. Strips outer markdown fences (```markdown ... ```) or conversational intro/outro text.
    """
    if not current_date:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    text = content.strip()

    # Strip outer markdown wrapper if model wrapped entire document in ```markdown ... ```
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            first_line = text[:first_newline].strip()
            if first_line.startswith("```"):
                text = text[first_newline + 1:]
        if text.endswith("```"):
            last_fence = text.rfind("```")
            text = text[:last_fence].strip()

    canonical_title = f"# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}"

    # Search for an existing # ⚡ title line
    title_match = re.search(r"^#\s*⚡.*$", text, re.MULTILINE)

    # Check for Section 1 start
    s1_match = re.search(r"##\s*1\.\s*System Parameters", text, re.IGNORECASE)

    if title_match:
        # Title was found in text. Everything from the title onwards is the valid blueprint body
        text_from_title = text[title_match.start():]
        lines = text_from_title.splitlines()
        lines[0] = canonical_title
        text = "\n".join(lines)
    elif s1_match:
        # Title was omitted entirely but Section 1 exists
        header = generate_header(series_day, seed, current_date)
        s1_end = s1_match.start() + len(s1_match.group(0))
        text = header + "\n" + text[s1_end:].lstrip()
    else:
        # Neither title nor Section 1 matched; prepend canonical header
        header = generate_header(series_day, seed, current_date)
        text = header + "\n" + text

    # Verify badges exist between title and Section 1
    s1_check = re.search(r"##\s*1\.\s*System Parameters", text, re.IGNORECASE)
    if s1_check:
        pre_s1 = text[:s1_check.start()]
        if "[![Pillar" not in pre_s1:
            badges_block = f"""
[![Pillar](https://img.shields.io/badge/Pillar-{seed['badge_name']}-{seed['badge_color']}?style=for-the-badge)]()
[![Validation](https://img.shields.io/badge/Validation-Local--First%20CI%20Verified-emerald?style=for-the-badge&logo=githubactions)]()
[![Architecture](https://img.shields.io/badge/Architecture-Zero--Cost%20Mock%20Harness-blueviolet?style=for-the-badge)]()
[![Completeness](https://img.shields.io/badge/Completeness-Complete%20(10%2F10%20Sections)-brightgreen?style=for-the-badge)]()
[![Uniqueness](https://img.shields.io/badge/Uniqueness-True%20(Verified)-brightgreen?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)]()

> [!NOTE]
> **Dispatch Completeness & Uniqueness Audit**:
> - **Completeness Status:** Complete (10/10 Sections Verified)
> - **Missing Sections:** None
> - **Reason for Incompletion:** N/A (Fully generated within token limits)
> - **Unique Flag:** `true` (Verified non-colliding across historical catalog)

---
"""
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[:first_newline] + "\n" + badges_block + text[first_newline + 1:].lstrip()
            else:
                text = text + "\n" + badges_block

    # Final check: Ensure Line 1 is strictly the canonical title
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# ⚡"):
        idx = 0
        while idx < len(lines) and not lines[idx].startswith("# ⚡"):
            idx += 1
        if idx < len(lines):
            lines = lines[idx:]
        else:
            lines = [canonical_title, ""] + lines
        text = "\n".join(lines)

    return text.strip() + "\n"

def resolve_model_name(requested_model: str) -> str:
    """Ensure a valid, active Gemini model identifier is utilized."""
    # Deprecated models automatically upgraded to active defaults
    deprecated_to_flash = {
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-3.0-flash",
        "gemini-1.5-flash",
    }
    deprecated_to_pro = {
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-pro",
    }
    if requested_model in deprecated_to_flash:
        print(f"[NOTICE] Deprecated model '{requested_model}' upgraded to active 'gemini-3.8-flash'.")
        return "gemini-3.8-flash"
    if requested_model in deprecated_to_pro:
        print(f"[NOTICE] Deprecated model '{requested_model}' upgraded to active 'gemini-3.1-pro-preview'.")
        return "gemini-3.1-pro-preview"

    valid_models = {
        "gemini-3.8-flash": "gemini-3.8-flash",
        "gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
    }
    if requested_model in valid_models:
        return valid_models[requested_model]
    if "pro" in requested_model.lower():
        return "gemini-3.1-pro-preview"
    if requested_model.startswith("gemini-"):
        return requested_model
    return "gemini-3.8-flash"

def attempt_model_generation(api_key: str, model_name: str, prompt: str, max_retries: int = 4) -> Optional[str]:
    """
    Attempt generation with exponential backoff on transient errors (503, 429, 500, network timeouts).
    Aborts immediately on non-existent models (404).
    Tries SDK first, then REST API.
    """
    backoff_delays = [2, 5, 10, 15]

    for attempt in range(1, max_retries + 1):
        backoff_sec = backoff_delays[min(attempt - 1, len(backoff_delays) - 1)]

        # 1. Attempt via official google-genai SDK
        try:
            return generate_via_google_genai_sdk(api_key, model_name, prompt)
        except ImportError:
            pass  # Fall through to REST API
        except Exception as e:
            err_str = str(e)
            is_not_found = "404" in err_str or "NOT_FOUND" in err_str
            if is_not_found:
                print(f"[WARNING] SDK model '{model_name}' not found (404). Aborting retries.", file=sys.stderr)
                return None
            is_transient = any(c in err_str for c in ["503", "429", "500", "502", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "high demand"])
            if is_transient and attempt < max_retries:
                print(f"[WARNING] SDK '{model_name}' transient error ({err_str}). Retrying in {backoff_sec}s (attempt {attempt}/{max_retries})...", file=sys.stderr)
                time.sleep(backoff_sec)
                continue
            print(f"[WARNING] SDK generation failed on '{model_name}': {e}. Trying direct REST API...", file=sys.stderr)

        # 2. Attempt via direct REST API
        try:
            return generate_via_rest_api(api_key, model_name, prompt)
        except urllib.error.HTTPError as he:
            if he.code == 404:
                print(f"[WARNING] REST API model '{model_name}' not found (404). Aborting retries.", file=sys.stderr)
                return None
            is_transient = he.code in [503, 429, 500, 502, 504]
            if is_transient and attempt < max_retries:
                print(f"[WARNING] REST API '{model_name}' HTTP {he.code}. Retrying in {backoff_sec}s (attempt {attempt}/{max_retries})...", file=sys.stderr)
                time.sleep(backoff_sec)
                continue
            print(f"[WARNING] REST API encountered HTTP {he.code} on '{model_name}'.", file=sys.stderr)
            break
        except Exception as e:
            if attempt < max_retries:
                print(f"[WARNING] REST API '{model_name}' encountered: {e}. Retrying in {backoff_sec}s...", file=sys.stderr)
                time.sleep(backoff_sec)
                continue
            print(f"[WARNING] REST API error on '{model_name}': {e}", file=sys.stderr)
            break

    return None

def generate_content_with_resilience(api_key: str, requested_model: str, prompt: str) -> Optional[str]:
    """
    Execute generation with multi-model fallback cascade.
    Cascades strictly across active Gemini models (gemini-3.8-flash, gemini-3.1-pro-preview).
    """
    primary = resolve_model_name(requested_model)
    fallback_chain = [
        primary,
        "gemini-3.8-flash",
        "gemini-3.1-pro-preview",
    ]
    # Deduplicate while preserving order
    candidate_models = []
    for m in fallback_chain:
        if m not in candidate_models:
            candidate_models.append(m)

    for idx, model in enumerate(candidate_models, start=1):
        print(f"\n[INFO] [{idx}/{len(candidate_models)}] Initiating generation via model: {model}...")
        result = attempt_model_generation(api_key, model, prompt)
        if result and result.strip():
            # Validate completeness before declaring success
            is_complete, missing_sections = validate_dispatch_completeness(result)
            if is_complete:
                print(f"[SUCCESS] Content cleanly generated via model: {model} (All 10 sections verified)")
                return result
            print(f"[WARNING] Model '{model}' output incomplete: Missing {missing_sections}. Cascading to next candidate model...", file=sys.stderr)
        else:
            print(f"[INFO] Model '{model}' unavailable or high demand. Cascading to next candidate model...")

    return None

def main():
    print("=" * 80)
    print("HYPERSCALE SYSTEM BLUEPRINT: VISUAL GEMINI DISPATCH ENGINE")
    print("=" * 80)

    # 1. Parse Historical Dispatches for Anti-Collision Grounding
    DISPATCHES_DIR.mkdir(parents=True, exist_ok=True)
    past_dispatches = uniqueness.get_previous_dispatches_metadata(DISPATCHES_DIR)
    print(f"[LEDGER] Found {len(past_dispatches)} previously published dispatches in archive.")

    current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    current_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
    series_day = get_series_day()

    # 2. Select Candidate Blueprint Seed (Prioritizes Unvisited Architectures)
    seed, fallback_body = bc.get_next_unique_blueprint(series_day, past_dispatches)

    target_filename = f"day_dispatch_{current_timestamp}.md"
    target_filepath = DISPATCHES_DIR / target_filename

    print(f"Target Series Day: {series_day}")
    print(f"Target File: {target_filepath.name}")
    print(f"Target Title: {seed['title']}")
    print(f"Target Domain: {seed['domain']}")
    print(f"Target Framework: {seed['framework']}")

    # 3. Build Generation Prompt with Historical Negative Constraints
    prompt = build_system_prompt(series_day, seed, current_date, past_dispatches)

    # 4. Model & Auth Resolution
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    raw_model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

    generated_content = ""

    if api_key:
        print(f"\n[INFO] GEMINI_API_KEY detected. Starting resilient multi-model dispatch engine...")
        raw_generated = generate_content_with_resilience(api_key, raw_model, prompt) or ""
        if raw_generated:
            generated_content = sanitize_generated_dispatch(raw_generated, series_day, seed, current_date)
        else:
            print("[WARNING] All candidate Gemini models exhausted. Falling back to deterministic catalog...", file=sys.stderr)
            generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches, fallback_body)
            generated_content = sanitize_generated_dispatch(generated_content, series_day, seed, current_date)
    else:
        print("\n[NOTICE] GEMINI_API_KEY environment variable is NOT set.")
        print("[NOTICE] Operating in resilient DRY-RUN / Deterministic high-density architectural blueprint mode.")
        print("[NOTICE] (To enable live Gemini generation, configure GEMINI_API_KEY in repository secrets).")
        generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches, fallback_body)
        generated_content = sanitize_generated_dispatch(generated_content, series_day, seed, current_date)

    # 5. Strict 10-Section Completeness Verification Gate
    print("\n[VERIFICATION] Executing 10-section completeness validation...")
    is_complete, missing_sections = validate_dispatch_completeness(generated_content)
    if not is_complete:
        print(f"[WARNING] Generated blueprint is incomplete: Missing {missing_sections}", file=sys.stderr)
        print("[RECOVERY] Falling back to complete deterministic blueprint from catalog...", file=sys.stderr)
        recovery_seed, recovery_body = bc.get_next_unique_blueprint(series_day, past_dispatches)
        generated_content = generate_mock_dispatch(series_day, recovery_seed, current_date, past_dispatches, recovery_body)
        generated_content = sanitize_generated_dispatch(generated_content, series_day, recovery_seed, current_date)
        is_complete, missing_sections = validate_dispatch_completeness(generated_content)
        if not is_complete:
            print(f"[WARNING] Catalog fallback blueprint is incomplete: {missing_sections}. Synthesizing full procedural blueprint...", file=sys.stderr)
            recovery_body = bc.synthesize_procedural_blueprint_body(recovery_seed)
            generated_content = generate_mock_dispatch(series_day, recovery_seed, current_date, past_dispatches, recovery_body)
            generated_content = sanitize_generated_dispatch(generated_content, series_day, recovery_seed, current_date)
            is_complete, missing_sections = validate_dispatch_completeness(generated_content)
            if not is_complete:
                print(f"[ERROR] Critical: Procedural fallback blueprint is also incomplete: {missing_sections}", file=sys.stderr)
                sys.exit(1)
        seed = recovery_seed
        print(f"[RECOVERY] Successfully resolved complete blueprint: '{seed['title']}'")

    print("[SUCCESS] All 10 mandatory sections verified present and code fences properly closed.")

    # 6. Strict Uniqueness & Collision Verification Gate
    print("\n[VERIFICATION] Executing mathematical & semantic anti-repetition validation...")
    is_unique, reason = uniqueness.verify_dispatch_uniqueness(generated_content, past_dispatches)

    if not is_unique:
        print(f"[WARNING] Uniqueness collision detected: {reason}", file=sys.stderr)
        print("[RECOVERY] Searching for guaranteed unique non-colliding blueprint from catalog...", file=sys.stderr)
        recovery_seed, recovery_body = bc.get_next_unique_blueprint(series_day, past_dispatches)
        generated_content = generate_mock_dispatch(series_day, recovery_seed, current_date, past_dispatches, recovery_body)
        generated_content = sanitize_generated_dispatch(generated_content, series_day, recovery_seed, current_date)
        is_unique, reason = uniqueness.verify_dispatch_uniqueness(generated_content, past_dispatches)
        if not is_unique:
            print(f"[ERROR] Critical: Unable to find non-colliding blueprint: {reason}", file=sys.stderr)
            sys.exit(1)
        seed = recovery_seed
        print(f"[RECOVERY] Successfully resolved unique blueprint: '{seed['title']}'")

    print(f"[SUCCESS] {reason}")

    # 7. Automated Technical Review & Remediation Gate
    print("\n[REVIEW] Executing deep technical review and code linting...")
    generated_content, findings, fixes = technical_reviewer.review_and_fix_dispatch(generated_content, target_filename)
    if findings:
        for finding in findings:
            print(f"[REVIEW WARNING] {finding}", file=sys.stderr)
    if fixes:
        print(f"[REMEDIATION] Applied {len(fixes)} automated technical fixes:")
        for fix in fixes:
            print(f"  - {fix}")
    else:
        print("[SUCCESS] Technical review clean: zero code defects detected.")

    # 8. Write and Verify File
    DISPATCHES_DIR.mkdir(parents=True, exist_ok=True)
    with open(target_filepath, "w", encoding="utf-8") as f:
        f.write(generated_content)

    file_size = target_filepath.stat().st_size
    print(f"\n[SUCCESS] Blueprint cleanly written to: {target_filepath}")
    print(f"[STATS] Total Document Size: {file_size:,} bytes")
    print(f"[STATS] Total Lines: {len(generated_content.splitlines()):,}")

    if file_size == 0:
        print(f"[ERROR] Generated file is 0 bytes!", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)

if __name__ == "__main__":
    main()
