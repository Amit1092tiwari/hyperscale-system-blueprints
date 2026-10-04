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
        self.assertEqual(gd.resolve_model_name("gemini-2.0-flash"), "gemini-2.0-flash")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-pro"), "gemini-1.5-pro")
        self.assertEqual(gd.resolve_model_name("gemini-1.5-flash"), "gemini-1.5-flash")
        # Legacy/hypothetical models fall back cleanly
        self.assertEqual(gd.resolve_model_name("gemini-2.5-pro"), "gemini-2.0-flash")
        self.assertEqual(gd.resolve_model_name("unknown-model"), "gemini-2.0-flash")

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

if __name__ == '__main__':
    unittest.main()
