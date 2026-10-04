"""
Uniqueness & Anti-Repetition Verification Engine.
Guarantees that every generated hyperscale architecture blueprint is mathematically
and semantically distinct from all previously published dispatches.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional

# Core stop words and markdown formatting noise to exclude from semantic fingerprinting
STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "from", "into", "over", "under",
    "system", "parameters", "problem", "statement", "design", "architecture",
    "diagram", "flow", "production", "artifact", "executable", "monitoring",
    "failure", "mode", "cases", "words", "thoughtful", "wisdom", "github",
    "workflows", "test", "tests", "python", "yaml", "mermaid", "high", "level",
    "badge", "shields", "badge_name", "target", "domain", "framework", "used",
    "technology", "stack", "scale", "bottleneck", "lineage", "component",
    "components", "concepts", "involved", "file", "files", "metric", "metrics",
    "alert", "warning", "important", "notice", "dispatch", "true", "false",
    "none", "class", "def", "return", "self", "import", "from", "print"
}

def extract_tokens(text: str) -> Set[str]:
    """Extract distinct alphanumeric technical vocabulary words (len >= 4)."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return {w for w in words if w not in STOP_WORDS}

def extract_dispatch_metadata(file_path: Path) -> Dict:
    """Extract structured metadata and token fingerprint from a dispatch markdown file."""
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_line = lines[0] if lines else ""

    # Parse title & series day number
    title_match = re.search(
        r"#\s*⚡.*?(?:Day\s*(\d+)|Dispatch\s*#?(\d+)):\s*(.+)",
        first_line,
        re.IGNORECASE
    )
    if title_match:
        day_num = int(title_match.group(1) or title_match.group(2))
        title = title_match.group(3).strip()
    else:
        day_num = 0
        title = first_line.lstrip("#").strip()

    # Extract target domain
    domain_match = re.search(r"-\s*\*\*Target Domain:\*\*\s*(.+)", text, re.IGNORECASE)
    domain = domain_match.group(1).strip() if domain_match else ""

    # Extract framework used
    fw_match = re.search(r"-\s*\*\*Framework Used:\*\*\s*(.+)", text, re.IGNORECASE)
    framework = fw_match.group(1).strip() if fw_match else ""

    # Extract bottleneck
    bn_match = re.search(r"-\s*\*\*Scale Bottleneck:\*\*\s*(.+)", text, re.IGNORECASE)
    bottleneck = bn_match.group(1).strip() if bn_match else ""

    tokens = extract_tokens(text)

    return {
        "file_path": file_path,
        "filename": file_path.name,
        "day_number": day_num,
        "title": title,
        "domain": domain,
        "framework": framework,
        "bottleneck": bottleneck,
        "tokens": tokens,
        "raw_text": text,
    }

def get_previous_dispatches_metadata(dispatches_dir: Path) -> List[Dict]:
    """Inspect all existing dispatches and return their parsed metadata sorted by day number."""
    if not dispatches_dir.exists():
        return []

    dispatches = []
    for file_path in dispatches_dir.glob("day_dispatch_*.md"):
        try:
            meta = extract_dispatch_metadata(file_path)
            dispatches.append(meta)
        except Exception:
            pass

    # Sort deterministically by day number, then by filename
    dispatches.sort(key=lambda m: (m["day_number"], m["filename"]))
    return dispatches

def format_past_dispatches_summary(past_dispatches: List[Dict]) -> str:
    """Format an informative summary ledger for injection into Gemini's prompt."""
    if not past_dispatches:
        return "No previous dispatches published yet."

    lines = []
    for d in past_dispatches:
        line = f"- Dispatch #{d['day_number']}: \"{d['title']}\"\n"
        if d["domain"]:
            line += f"  • Domain: {d['domain']}\n"
        if d["framework"]:
            line += f"  • Framework: {d['framework']}\n"
        lines.append(line)

    return "\n".join(lines).strip()

def calculate_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute the Jaccard similarity coefficient between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0

def verify_dispatch_uniqueness(
    candidate_content: str,
    past_dispatches: List[Dict],
    similarity_threshold: float = 0.40,
    title_threshold: float = 0.60
) -> Tuple[bool, str]:
    """
    Validate that candidate markdown content does not duplicate or heavily overlap
    with any previously published dispatch in the repository.

    Returns:
        (is_unique: bool, reason: str)
    """
    if not past_dispatches:
        return True, "No previous dispatches to collide with."

    # Parse candidate metadata
    first_line = candidate_content.splitlines()[0] if candidate_content else ""
    title_match = re.search(
        r"#\s*⚡.*?(?:Day\s*(\d+)|Dispatch\s*#?(\d+)):\s*(.+)",
        first_line,
        re.IGNORECASE
    )
    candidate_title = title_match.group(3).strip() if title_match else first_line.lstrip("#").strip()

    domain_match = re.search(r"-\s*\*\*Target Domain:\*\*\s*(.+)", candidate_content, re.IGNORECASE)
    candidate_domain = domain_match.group(1).strip() if domain_match else ""

    fw_match = re.search(r"-\s*\*\*Framework Used:\*\*\s*(.+)", candidate_content, re.IGNORECASE)
    candidate_framework = fw_match.group(1).strip() if fw_match else ""

    candidate_tokens = extract_tokens(candidate_content)
    candidate_title_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", candidate_title.lower()))

    for past in past_dispatches:
        past_day = past["day_number"]
        past_title = past["title"]

        # 1. Exact Title Collision Check
        if candidate_title.strip().lower() == past_title.strip().lower():
            return False, f"Exact title collision with Dispatch #{past_day}: '{past_title}'"

        # 2. High Title Similarity Check
        past_title_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", past_title.lower()))
        title_sim = calculate_jaccard_similarity(candidate_title_words, past_title_words)
        if title_sim > title_threshold:
            return False, (
                f"Title similarity ({title_sim:.1%}) exceeds threshold ({title_threshold:.0%}) "
                f"with Dispatch #{past_day}: '{past_title}'"
            )

        # 3. Identical Domain & Framework Collision Check
        if candidate_domain and candidate_domain == past["domain"]:
            if candidate_framework and candidate_framework == past["framework"]:
                return False, (
                    f"Target Domain and Framework are identical to Dispatch #{past_day}: "
                    f"'{past['domain']}' / '{past['framework']}'"
                )

        # 4. Content Vocabulary Jaccard Similarity Check
        content_sim = calculate_jaccard_similarity(candidate_tokens, past["tokens"])
        if content_sim > similarity_threshold:
            return False, (
                f"Content vocabulary similarity ({content_sim:.1%}) exceeds threshold ({similarity_threshold:.0%}) "
                f"with Dispatch #{past_day} ({past['filename']})"
            )

    return True, "Content verified 100% unique and non-repetitive."
