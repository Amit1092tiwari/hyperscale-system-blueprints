import unittest
import sys
from pathlib import Path

# Add project root and scripts to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import blueprints_catalog as bc
import uniqueness

class TestUniquenessIntegration(unittest.TestCase):
    def setUp(self):
        self.dispatches_dir = PROJECT_ROOT / "dispatches"
        self.past_dispatches = uniqueness.get_previous_dispatches_metadata(self.dispatches_dir)

    def test_past_dispatches_parsing(self):
        self.assertGreaterEqual(len(self.past_dispatches), 3)
        day_numbers = [d["day_number"] for d in self.past_dispatches]
        self.assertIn(1, day_numbers)
        self.assertIn(2, day_numbers)
        self.assertIn(3, day_numbers)

    def test_existing_dispatches_are_unique_among_each_other(self):
        for i, d1 in enumerate(self.past_dispatches):
            for d2 in self.past_dispatches[i+1:]:
                # Titles must not be equal
                self.assertNotEqual(d1["title"].lower(), d2["title"].lower())
                # Domain & framework combination must not be equal
                self.assertFalse(d1["domain"] == d2["domain"] and d1["framework"] == d2["framework"])
                # Jaccard token similarity must be < 0.35
                sim = uniqueness.calculate_jaccard_similarity(d1["tokens"], d2["tokens"])
                self.assertLess(sim, 0.35, f"Similarity between #{d1['day_number']} and #{d2['day_number']} was {sim:.3f}")

    def test_uniqueness_verification_rejects_duplicate_dispatch(self):
        first_file = self.past_dispatches[0]["file_path"].read_text(encoding="utf-8")
        is_unique, reason = uniqueness.verify_dispatch_uniqueness(first_file, self.past_dispatches)
        self.assertFalse(is_unique)
        self.assertIn("Exact title collision", reason)

    def test_uniqueness_verification_accepts_novel_blueprint(self):
        seed, body = bc.get_next_unique_blueprint(4, self.past_dispatches)
        header = f"# ⚡ 2026-10-04 - Dispatch #4: {seed['title']}\n\n- **Target Domain:** {seed['domain']}\n- **Framework Used:** {seed['framework']}\n"
        full_content = header + body
        is_unique, reason = uniqueness.verify_dispatch_uniqueness(full_content, self.past_dispatches)
        self.assertTrue(is_unique, f"Verification failed: {reason}")

    def test_sequential_blueprints_rotation_is_strictly_unique(self):
        # Simulate 8 sequential dispatches starting from day 1
        simulated_history = []
        for day in range(1, 9):
            seed, body = bc.get_next_unique_blueprint(day, simulated_history)
            header = f"# ⚡ 2026-10-04 - Dispatch #{day}: {seed['title']}\n\n- **Target Domain:** {seed['domain']}\n- **Framework Used:** {seed['framework']}\n"
            full_content = header + body

            # Verify uniqueness against history
            is_unique, reason = uniqueness.verify_dispatch_uniqueness(full_content, simulated_history)
            self.assertTrue(is_unique, f"Day {day} ({seed['title']}) was not unique: {reason}")

            # Append to simulated history
            tokens = uniqueness.extract_tokens(full_content)
            simulated_history.append({
                "day_number": day,
                "title": seed["title"],
                "domain": seed["domain"],
                "framework": seed["framework"],
                "tokens": tokens,
                "filename": f"day_dispatch_sim_{day}.md"
            })

        # Verify all 8 titles are distinct
        all_titles = [d["title"] for d in simulated_history]
        self.assertEqual(len(set(all_titles)), 8)

if __name__ == '__main__':
    unittest.main()
