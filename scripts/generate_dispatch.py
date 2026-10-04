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

def generate_header(series_day: int, seed: dict, current_date: str = "") -> str:
    """Build Section 1 and header badges with dynamic seed metadata."""
    if not current_date:
        current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return f"""# ⚡ {current_date} - Dispatch #{series_day}: {seed['title']}

[![Pillar](https://img.shields.io/badge/Pillar-{seed['badge_name']}-{seed['badge_color']}?style=for-the-badge)]()
[![Validation](https://img.shields.io/badge/Validation-Local--First%20CI%20Verified-emerald?style=for-the-badge&logo=githubactions)]()
[![Architecture](https://img.shields.io/badge/Architecture-Zero--Cost%20Mock%20Harness-blueviolet?style=for-the-badge)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)]()

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
    past_dispatches: Optional[List[Dict]] = None
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
"""

def generate_via_google_genai_sdk(api_key: str, model_name: str, prompt: str) -> str:
    """Attempt generation via official google-genai SDK."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8192,
        ),
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
            "maxOutputTokens": 8192
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

def resolve_model_name(requested_model: str) -> str:
    """Ensure a valid, active Gemini model identifier is utilized."""
    valid_models = {
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
    }
    if requested_model in valid_models:
        return valid_models[requested_model]
    if "2.5" in requested_model or "pro" in requested_model:
        print(f"[NOTICE] Model '{requested_model}' mapped to verified 'gemini-2.0-flash'.")
        return "gemini-2.0-flash"
    return "gemini-2.0-flash"

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
    raw_model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()
    model_name = resolve_model_name(raw_model)

    generated_content = ""

    if api_key:
        print(f"\n[INFO] GEMINI_API_KEY detected. Initiating generation via model: {model_name}...")
        try:
            print("[INFO] Attempting generation with 'google-genai' SDK...")
            generated_content = generate_via_google_genai_sdk(api_key, model_name, prompt)
            print("[SUCCESS] Content generated via google-genai SDK.")
        except ImportError:
            print("[INFO] 'google-genai' package not installed. Falling back to direct REST API...")
            try:
                generated_content = generate_via_rest_api(api_key, model_name, prompt)
                print("[SUCCESS] Content generated via Gemini REST API.")
            except Exception as e:
                print(f"[WARNING] REST API encountered: {e}. Falling back to deterministic catalog...", file=sys.stderr)
                generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches)
        except Exception as e:
            print(f"[WARNING] SDK generation encountered: {e}. Trying direct REST API...", file=sys.stderr)
            try:
                generated_content = generate_via_rest_api(api_key, model_name, prompt)
                print("[SUCCESS] Content generated via Gemini REST API.")
            except Exception as inner_e:
                print(f"[WARNING] REST API encountered: {inner_e}. Falling back to deterministic catalog...", file=sys.stderr)
                generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches)
    else:
        print("\n[NOTICE] GEMINI_API_KEY environment variable is NOT set.")
        print("[NOTICE] Operating in resilient DRY-RUN / Deterministic high-density architectural blueprint mode.")
        print("[NOTICE] (To enable live Gemini generation, configure GEMINI_API_KEY in repository secrets).")
        generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches)

    # 5. Strict Uniqueness & Collision Verification Gate
    print("\n[VERIFICATION] Executing mathematical & semantic anti-repetition validation...")
    is_unique, reason = uniqueness.verify_dispatch_uniqueness(generated_content, past_dispatches)

    if not is_unique:
        print(f"[WARNING] Uniqueness collision detected: {reason}", file=sys.stderr)
        print("[RECOVERY] Selecting guaranteed unique blueprint from catalog...", file=sys.stderr)
        seed, fallback_body = bc.get_next_unique_blueprint(series_day, past_dispatches)
        generated_content = generate_mock_dispatch(series_day, seed, current_date, past_dispatches)
        is_unique, reason = uniqueness.verify_dispatch_uniqueness(generated_content, past_dispatches)
        if not is_unique:
            print(f"[ERROR] Critical: Blueprint still collided: {reason}", file=sys.stderr)
            sys.exit(1)

    print(f"[SUCCESS] {reason}")

    # 6. Write and Verify File
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
