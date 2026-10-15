import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import generate_dispatch as gd

class TestDispatchGenerator(unittest.TestCase):
    def test_pillar_definitions(self):
        self.assertEqual(len(gd.PILLARS), 4)
        pillar_ids = {p["pillar_id"] for p in gd.PILLARS}
        self.assertEqual(pillar_ids, {"A", "B", "C", "D"})

    def test_model_name_resolution(self):
        self.assertEqual(gd.resolve_model_name("gemini-3.8-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("gemini-3.1-pro-preview"), "gemini-3.1-pro-preview")
        # Obsolete models upgrade to active defaults
        self.assertEqual(gd.resolve_model_name("gemini-3.0-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("gemini-2.5-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("gemini-2.0-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("gemini-2.5-pro"), "gemini-3.1-pro-preview")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-pro"), "gemini-3.1-pro-preview")
        self.assertEqual(gd.resolve_model_name("gemini-pro"), "gemini-3.1-pro-preview")
        self.assertEqual(gd.resolve_model_name("unknown-model"), "gemini-3.8-flash")

    def test_sanitize_generated_dispatch_enforces_line1_title(self):
        seed = gd.PILLARS[0]
        # Case 1: Badges above title
        content_with_badges_first = f"""[![Pillar](https://img.shields.io/badge/Pillar-A-red)]()

# ⚡ 2026-10-14 - Dispatch #36: {seed['title']}

## 1. System Parameters
- **Target Domain:** {seed['domain']}
"""
        sanitized = gd.sanitize_generated_dispatch(content_with_badges_first, 36, seed, "2026-10-14")
        lines = sanitized.splitlines()
        self.assertTrue(lines[0].startswith("# ⚡ 2026-10-14 - Dispatch #36:"))
        self.assertIn("## 1. System Parameters", sanitized)

        # Case 2: Outer markdown code fence
        fenced_content = f"""```markdown
# ⚡ 2026-10-14 - Dispatch #36: {seed['title']}

## 1. System Parameters
- **Target Domain:** {seed['domain']}
```"""
        sanitized = gd.sanitize_generated_dispatch(fenced_content, 36, seed, "2026-10-14")
        self.assertFalse(sanitized.startswith("```"))
        self.assertTrue(sanitized.startswith("# ⚡ 2026-10-14 - Dispatch #36:"))

    def test_day_36_generation_uniqueness(self):
        """Verify that Day 36 specifically generates a 100% unique blueprint against all actual dispatches."""
        past = gd.uniqueness.get_previous_dispatches_metadata(gd.DISPATCHES_DIR)
        self.assertGreaterEqual(len(past), 36)
        past_for_36 = [d for d in past if d["day_number"] < 36]
        seed, body = gd.bc.get_next_unique_blueprint(36, past_for_36)

        self.assertEqual(seed["pillar_id"], "D", "Day 36 must belong to Pillar D")
        content = gd.generate_mock_dispatch(36, seed, "2026-10-14", past_for_36, body)
        sanitized = gd.sanitize_generated_dispatch(content, 36, seed, "2026-10-14")
        is_unique, reason = gd.uniqueness.verify_dispatch_uniqueness(sanitized, past_for_36)
        self.assertTrue(is_unique, f"Day 36 collision: {reason}")

    def test_day_37_generation_uniqueness(self):
        """Verify that Day 37 specifically generates a 100% unique blueprint against all actual dispatches."""
        past = gd.uniqueness.get_previous_dispatches_metadata(gd.DISPATCHES_DIR)
        self.assertGreaterEqual(len(past), 37)
        seed, body = gd.bc.get_next_unique_blueprint(37, past)

        self.assertEqual(seed["pillar_id"], "A", "Day 37 must belong to Pillar A")
        content = gd.generate_mock_dispatch(37, seed, "2026-10-15", past, body)
        sanitized = gd.sanitize_generated_dispatch(content, 37, seed, "2026-10-15")
        is_unique, reason = gd.uniqueness.verify_dispatch_uniqueness(sanitized, past)
        self.assertTrue(is_unique, f"Day 37 collision: {reason}")

    def test_attempt_model_generation_aborts_immediately_on_404(self):
        """Verify that a 404 NOT_FOUND response aborts immediately without burning retries."""
        from unittest.mock import patch
        import urllib.error

        mock_404 = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )

        with patch("generate_dispatch.generate_via_google_genai_sdk", side_effect=RuntimeError("404 NOT_FOUND")):
            with patch("generate_dispatch.generate_via_rest_api", side_effect=mock_404) as mock_rest:
                result = gd.attempt_model_generation("mock-key", "gemini-obsolete-model", "test-prompt", max_retries=4)
                self.assertIsNone(result)
                # Should not have called REST API because SDK failed with 404 and aborted
                mock_rest.assert_not_called()

    def test_all_four_pillars_generation(self):
        generated_titles = set()
        generated_domains = set()

        for day in range(1, 5):
            pillar_idx = (day - 1) % len(gd.PILLARS)
            seed = gd.PILLARS[pillar_idx]
            content = gd.generate_mock_dispatch(day, seed)
            
            # Assert document completeness and minimum length
            self.assertGreater(len(content), 10000, f"Pillar {seed['pillar_id']} too short")
            
            # Assert mandatory 10 sections exist
            self.assertIn(f"Dispatch #{day}:", content)
            self.assertIn("## 1. System Parameters", content)
            self.assertIn("## 2. Problem Statement", content)
            self.assertIn("## 3. High-Level Design (HLD)", content)
            self.assertIn("## 4. Low-Level Design (LLD)", content)
            self.assertIn("## 5. Logical Flow Diagram", content)
            self.assertIn("## 6. Architectural Drill & Nature Analogy", content)
            self.assertIn("## 7. Production-Grade Executable Artifact", content)
            self.assertIn("## 8. KPI Monitoring Framework", content)
            self.assertIn("## 9. Failure Mode & Production Edge Cases", content)
            self.assertIn("## 10. Thoughtful Wisdom Words", content)

            # Assert rich markdown features
            self.assertIn("```mermaid", content)
            self.assertIn("> [!WARNING]", content)
            self.assertIn("> [!TIP]", content)
            
            generated_titles.add(seed["title"])
            generated_domains.add(seed["domain"])

        # Assert all 4 dispatches are distinct
        self.assertEqual(len(generated_titles), 4)
        self.assertEqual(len(generated_domains), 4)

    def test_dispatch_uniqueness_across_extended_catalog(self):
        """Verify that sequential calls without explicit seed yield strictly unique blueprints."""
        history = []
        titles = set()
        domains = set()

        for day in range(1, 9):
            content = gd.generate_mock_dispatch(day, seed=None, past_dispatches=history)
            
            # Extract title and domain from content
            lines = content.splitlines()
            title_line = lines[0] if lines else ""
            self.assertIn(f"Dispatch #{day}:", title_line)
            
            # Check uniqueness against history
            is_unique, reason = gd.uniqueness.verify_dispatch_uniqueness(content, history)
            self.assertTrue(is_unique, f"Day {day} failed uniqueness check: {reason}")
            
            # Track history for subsequent days
            meta = {
                "day_number": day,
                "title": title_line.split(":", 1)[1].strip() if ":" in title_line else title_line,
                "domain": "test",
                "framework": "test",
                "tokens": gd.uniqueness.extract_tokens(content),
                "filename": f"test_day_{day}.md"
            }
            history.append(meta)
            titles.add(meta["title"])

        self.assertEqual(len(titles), 8)

    def test_day_32_generation_uniqueness(self):
        """Verify that Day 32 specifically generates a 100% unique blueprint against all actual dispatches."""
        past = gd.uniqueness.get_previous_dispatches_metadata(gd.DISPATCHES_DIR)
        seed, body = gd.bc.get_next_unique_blueprint(32, past)
        
        self.assertEqual(seed["pillar_id"], "D", "Day 32 must belong to Pillar D")
        content = gd.generate_mock_dispatch(32, seed, "2026-10-12", past, body)
        is_unique, reason = gd.uniqueness.verify_dispatch_uniqueness(content, past)
        self.assertTrue(is_unique, f"Day 32 collision: {reason}")

    def test_resilient_gemini_fallback_on_simulated_503(self):
        """Verify that attempt_model_generation and fallback chain handle transient 503 gracefully."""
        from unittest.mock import patch
        import urllib.error

        # Simulate 503 HTTPError from REST API
        mock_503 = urllib.error.HTTPError(
            url="https://generativelanguage.googleapis.com",
            code=503,
            msg="Service Unavailable",
            hdrs={},
            fp=None
        )

        with patch("generate_dispatch.generate_via_google_genai_sdk", side_effect=RuntimeError("503 UNAVAILABLE: high demand")):
            with patch("generate_dispatch.generate_via_rest_api", side_effect=mock_503):
                result = gd.attempt_model_generation("mock-key", "gemini-3.8-flash", "test-prompt", max_retries=1)
                self.assertIsNone(result, "Should return None on exhausted 503 retries without throwing uncaught exception")

    def test_validate_dispatch_completeness_success(self):
        """Verify that a dispatch with all 10 sections passes completeness check."""
        full_content = """# ⚡ 2026-10-15 - Dispatch #40: Test Blueprint
## 1. System Parameters
- **Target Domain:** AI
## 2. Problem Statement
Warning text.
## 3. High-Level Design (HLD)
HLD text.
## 4. Low-Level Design (LLD)
LLD text.
## 5. Logical Flow Diagram
Flow text.
## 6. Architectural Drill & Nature Analogy
Analogy text.
## 7. Production-Grade Executable Artifact
```python
x = 1
```
## 8. KPI Monitoring Framework
- Metric 1
## 9. Failure Mode & Production Edge Cases
Table
## 10. Thoughtful Wisdom Words
> Quote
"""
        is_complete, missing = gd.validate_dispatch_completeness(full_content)
        self.assertTrue(is_complete)
        self.assertEqual(missing, [])

    def test_validate_dispatch_completeness_detects_missing_sections(self):
        """Verify that missing sections are detected accurately."""
        truncated_content = """# ⚡ 2026-10-15 - Dispatch #40: Test Blueprint
## 1. System Parameters
## 2. Problem Statement
## 3. High-Level Design (HLD)
## 4. Low-Level Design (LLD)
## 5. Logical Flow Diagram
## 6. Architectural Drill & Nature Analogy
## 7. Production-Grade Executable Artifact
```python
x = 1
```
"""
        is_complete, missing = gd.validate_dispatch_completeness(truncated_content)
        self.assertFalse(is_complete)
        self.assertIn("8. KPI Monitoring Framework", missing)
        self.assertIn("9. Failure Mode & Production Edge Cases", missing)
        self.assertIn("10. Thoughtful Wisdom Words", missing)

    def test_validate_dispatch_completeness_detects_unclosed_fence(self):
        """Verify that odd code fences are detected."""
        broken_fence_content = """# ⚡ 2026-10-15 - Dispatch #40: Test Blueprint
## 1. System Parameters
## 2. Problem Statement
## 3. High-Level Design (HLD)
## 4. Low-Level Design (LLD)
## 5. Logical Flow Diagram
## 6. Architectural Drill & Nature Analogy
## 7. Production-Grade Executable Artifact
```python
x = 1
## 8. KPI Monitoring Framework
## 9. Failure Mode & Production Edge Cases
## 10. Thoughtful Wisdom Words
"""
        is_complete, missing = gd.validate_dispatch_completeness(broken_fence_content)
        self.assertFalse(is_complete)
        self.assertTrue(any("Unclosed Code Fence" in m for m in missing))

    def test_all_repository_dispatches_are_complete(self):
        """Verify that all dispatches currently in the repository have all 10 mandatory sections."""
        dispatches = list(gd.DISPATCHES_DIR.glob("day_dispatch_*.md"))
        self.assertGreaterEqual(len(dispatches), 39)
        for d in dispatches:
            content = d.read_text(encoding="utf-8")
            is_complete, missing = gd.validate_dispatch_completeness(content)
            self.assertTrue(is_complete, f"{d.name} is incomplete: missing {missing}")

    def test_technical_reviewer_integrated_in_dispatch_generation(self):
        """Verify that newly generated content passes technical review and receives audit annotations."""
        past = gd.uniqueness.get_previous_dispatches_metadata(gd.DISPATCHES_DIR)
        seed, body = gd.bc.get_next_unique_blueprint(40, past)
        raw_mock = gd.generate_mock_dispatch(40, seed, "2026-10-15", past, body)
        sanitized = gd.sanitize_generated_dispatch(raw_mock, 40, seed, "2026-10-15")

        reviewed_content, findings, fixes = gd.technical_reviewer.review_and_fix_dispatch(sanitized, "day_dispatch_test.md")
        self.assertEqual(findings, [])
        self.assertIn("Dispatch Technical Review & Completeness Audit", reviewed_content)
        self.assertIn("Complete / Verified (10/10 Sections Verified)", reviewed_content)


if __name__ == '__main__':
    unittest.main()


