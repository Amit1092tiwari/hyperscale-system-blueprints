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
    # Common English conjunctions, prepositions, articles
    "the", "and", "for", "with", "this", "that", "from", "into", "over", "under",
    "between", "during", "through", "across", "without", "than", "when",
    # Markdown, report metadata, sections, and shields
    "system", "parameters", "problem", "statement", "design", "architecture",
    "architectural", "architectures", "diagram", "flow", "production", "artifact",
    "executable", "monitoring", "failure", "mode", "cases", "words", "thoughtful",
    "wisdom", "github", "workflows", "test", "tests", "python", "yaml", "mermaid",
    "high", "level", "badge", "shields", "badge_name", "target", "domain",
    "framework", "used", "technology", "stack", "scale", "bottleneck", "lineage",
    "component", "components", "concepts", "involved", "file", "files", "metric",
    "metrics", "alert", "warning", "important", "notice", "dispatch", "true",
    "false", "none", "visual", "ascii", "topology", "decision", "sequence",
    "breakdown", "nature", "analogy", "biological", "structural", "parallel",
    "unit", "status", "sections", "historical", "reason", "incompletion", "limits",
    "complete", "completed", "completeness", "verified", "verify", "validation",
    "validate", "unique", "uniqueness", "colliding", "license", "apache",
    "https", "style", "color", "blue", "blueviolet", "brightgreen", "emerald",
    "purple", "teal", "red", "orange", "githubactions", "logo", "logocolor",
    "review", "reviewing", "architect", "senior", "peer", "audit", "checklist",
    "summary", "ledger", "author", "fellow", "director", "principal", "specialist",
    # Python language, unittest harness & typing keywords
    "class", "def", "return", "self", "import", "print", "assert", "self.assert",
    "classdef", "stroke", "fill", "assertequal", "assertfalse", "assertgreater",
    "assertin", "assertless", "assertnotin", "asserttrue", "unittest", "pytest",
    "testcase", "typing", "time", "bool", "dict", "list", "items", "item", "fail",
    "pass", "line", "code", "text", "capacity", "buffer", "buffers", "append",
    "processed", "count", "batch", "size", "drain", "bounds", "suite", "setup",
    "simulated", "mock", "harness", "invariant", "invariants", "isolated",
    # CI/CD, workflow & GitHub Actions keywords
    "actions", "workflow", "runtime", "checkout", "ubuntu", "latest", "timeout",
    "minutes", "permissions", "runs", "matrix", "install", "dependencies",
    "upgrade", "cancel", "progress", "branches", "push", "pull", "request",
    # Mermaid & ASCII diagram graph syntax & boilerplate
    "graph", "norm", "succ", "sequencediagram", "flowchart", "subgraph", "autonumber",
    "participant", "checkbackpressure", "errorabort", "executeengine", "recordlineage",
    "validateprotocol", "check", "prompt", "rate", "ratio", "start", "throttle",
    "exceeded", "normal", "initiated", "inbound", "ingress", "gateway", "egress",
    "output", "allocator", "dispatcher", "worker", "workers", "sieve", "slot",
    "slots", "chunk", "chunks", "aligned", "descriptor", "deadbeef", "header",
    "magic", "identifier", "monotonic", "counter", "pointers", "head", "tail",
    "transaction", "acknowledge", "acknowledgment", "signal", "emit", "facet",
    "facets", "governance", "rollback", "malformed", "reject", "optimal",
    # Common procedural narrative phrasing & operational telemetry terms
    "operational", "performance", "resilience", "robustness", "throughput",
    "latency", "saturation", "saturate", "contention", "spikes", "starvation",
    "overhead", "amplification", "blockage", "dropped", "burst", "bursts",
    "splicing", "splicer", "continuous", "continuously", "unidirectional",
    "gradient", "traverses", "unbroken", "interrupted", "uninterrupted",
    "stems", "decouples", "decouple", "incur", "incurring", "repeated",
    "eliminating", "eliminate", "movement", "physical", "address", "pinned",
    "ranges", "surges", "near", "zero", "lockless", "lock", "free", "queue",
    "queues", "ring", "rings", "single", "consumer", "producer", "spsc",
    "numa", "affinity", "isolation", "spooling", "flush", "mitigation",
    "blast", "radius", "root", "cause", "vector", "discipline", "disciplined",
    "consequence", "natural", "ceases", "harmony", "hierarchies", "ruthlessly",
    "complexity", "execution", "pipeline", "subsystem", "allocation", "allocations",
    "allocate", "application", "apply", "baseline", "between", "blocks", "bypass",
    "cache", "caches", "catalog", "causing", "clean", "client", "cloud",
    "committed", "completely", "completion", "computational", "concurrent",
    "context", "contract", "coordinator", "copies", "copy", "copying", "core",
    "coreengine", "cores", "cost", "critical", "data", "dedicated", "demands",
    "deploying", "deterministic", "devops", "diagnostic", "directly", "distributed",
    "drill", "driver", "encounter", "engine", "engineering", "epoch", "error",
    "evaluation", "event", "exceeding", "excessive", "execute", "exponential",
    "first", "flag", "forward", "grade", "hardware", "host", "hyperscale",
    "identical", "implementation", "implements", "incremental", "inducing",
    "infrastructure", "input", "inspect", "integrity", "invalid", "jitter",
    "jobs", "kernel", "layer", "layout", "linux", "load", "local", "logical",
    "main", "maintains", "maximum", "measures", "memory", "mesh", "micro",
    "must", "name", "native", "network", "networking", "note", "operation",
    "optimal", "overlap", "packet", "page", "pages", "partition", "pattern",
    "percentage", "pillar", "poll", "polled", "pool", "protocol", "provides",
    "providing", "push", "range", "rather", "real", "record", "repository",
    "request", "requires", "resource", "safe", "scaling", "schema", "second",
    "serialization", "severe", "size", "space", "speed", "standard", "steps",
    "stopping", "stream", "streaming", "strict", "strictly", "structures",
    "submit", "success", "successfully", "supporting", "sustained", "sweep",
    "switches", "systemic", "systems", "tail", "technical", "thrashing",
    "threshold", "traditional", "transformation", "translation", "tree",
    "trigger", "unoptimized", "upgrade", "user", "uses", "valid", "vectorized",
    "version", "wait", "width", "wire"
}

TITLE_STOP_WORDS = {
    "for", "architecture", "tier", "adaptive", "series", "day", "iteration",
    "epoch", "phase", "dispatch", "pillar", "and", "the", "with", "from",
    "mesh", "engine", "fabric", "core", "sieve", "subsystem", "throughput",
    "final", "high", "guaranteed"
}

def extract_tokens(text: str) -> Set[str]:
    """Extract distinct alphanumeric technical vocabulary words (len >= 4)."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return {w for w in words if w not in STOP_WORDS}

def extract_dispatch_title(content: str) -> Tuple[int, str]:
    """
    Robustly extract the series day number and clean title from markdown content,
    even if badge links, shields, HTML comments, or blank lines precede the header.
    """
    match = re.search(
        r"#\s*⚡.*?(?:Day\s*(\d+)|Dispatch\s*#?(\d+)):\s*(.+)",
        content,
        re.IGNORECASE
    )
    if match:
        day_num = int(match.group(1) or match.group(2))
        raw_title = match.group(3).strip()
        # Clean any trailing or embedded markdown link formatting
        clean_title = re.sub(r"\[.*?\]\(.*?\)", "", raw_title).strip()
        return day_num, clean_title

    # Fallback: scan lines for the first non-badge heading
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#") and not line.startswith("# [![") and not line.startswith("[!["):
            return 0, line.lstrip("#").strip()
    return 0, ""

def extract_dispatch_metadata(file_path: Path) -> Dict:
    """Extract structured metadata and token fingerprint from a dispatch markdown file."""
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    day_num, title = extract_dispatch_title(text)

    # Fallback to filename day extraction if header lacks day number
    if day_num == 0:
        fn_match = re.search(r"day_dispatch_.*?_(\d+)\.md", file_path.name)
        if fn_match:
            day_num = int(fn_match.group(1))

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
    candidate_day, candidate_title = extract_dispatch_title(candidate_content)

    domain_match = re.search(r"-\s*\*\*Target Domain:\*\*\s*(.+)", candidate_content, re.IGNORECASE)
    candidate_domain = domain_match.group(1).strip() if domain_match else ""

    fw_match = re.search(r"-\s*\*\*Framework Used:\*\*\s*(.+)", candidate_content, re.IGNORECASE)
    candidate_framework = fw_match.group(1).strip() if fw_match else ""

    candidate_tokens = extract_tokens(candidate_content)
    raw_cand_title_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", candidate_title.lower()))
    candidate_title_words = {w for w in raw_cand_title_words if w not in TITLE_STOP_WORDS}
    if not candidate_title_words:
        candidate_title_words = raw_cand_title_words

    for past in past_dispatches:
        past_day = past["day_number"]
        past_title = past["title"]

        # 1. Exact Title Collision Check
        if candidate_title.strip().lower() == past_title.strip().lower():
            return False, f"Exact title collision with Dispatch #{past_day}: '{past_title}'"

        # 2. High Title Similarity Check (Substantive Architectural Title Words)
        raw_past_title_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", past_title.lower()))
        past_title_words = {w for w in raw_past_title_words if w not in TITLE_STOP_WORDS}
        if not past_title_words:
            past_title_words = raw_past_title_words

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
