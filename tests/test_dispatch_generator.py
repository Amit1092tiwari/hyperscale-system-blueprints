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
        self.assertEqual(gd.resolve_model_name("gemini-3.0-flash"), "gemini-3.0-flash")
        self.assertEqual(gd.resolve_model_name("gemini-2.5-flash"), "gemini-2.5-flash")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-pro"), "gemini-1.5-pro")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-flash"), "gemini-1.5-flash")
        # Deprecated gemini-2.0-flash automatically upgrades to active default
        self.assertEqual(gd.resolve_model_name("gemini-2.0-flash"), "gemini-3.8-flash")
        self.assertEqual(gd.resolve_model_name("unknown-model"), "gemini-3.8-flash")

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

if __name__ == '__main__':
    unittest.main()

