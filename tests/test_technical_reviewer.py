import unittest
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import technical_reviewer as tr


class TestTechnicalReviewer(unittest.TestCase):
    def setUp(self):
        self.sample_valid_dispatch = """# ⚡ 2026-10-15 - Dispatch #99: Hyperscale Zero-Copy Packet Engine

[![Pillar](https://img.shields.io/badge/Pillar-Systems-purple?style=for-the-badge)]()
[![Validation](https://img.shields.io/badge/Validation-Local--First%20CI%20Verified-emerald?style=for-the-badge)]()

---

## 1. System Parameters
- **Target Domain:** High-Throughput Packet Processing

## 2. Problem Statement
High throughput causes context switching bottlenecks.

## 3. High-Level Design (HLD)
Zero-copy DMA ring buffer architecture.

## 4. Low-Level Design (LLD)
Memory-mapped hugepage circular queue.

## 5. Logical Flow Diagram
```mermaid
graph TD
    A[Ingress] --> B[Process]
```

## 6. Architectural Drill & Nature Analogy
Avian respiratory continuous cross-current ventilation.

## 7. Production-Grade Executable Artifact
```python
def process_packet(pkt: bytes) -> bool:
    return len(pkt) > 0

if __name__ == "__main__":
    assert process_packet(b"test")
```

## 8. KPI Monitoring Framework
| Metric | Target |
|---|---|
| Latency | <10 µs |

## 9. Failure Mode & Production Edge Cases
| Failure Mode | Impact |
|---|---|
| Memory leak | OOM |

## 10. Thoughtful Wisdom Words
Simplicity and purity in zero-allocation designs preserve determinism.
"""

    def test_check_section_completeness_complete(self):
        missing = tr.check_section_completeness(self.sample_valid_dispatch)
        self.assertEqual(missing, [])

    def test_check_section_completeness_missing_section(self):
        incomplete = self.sample_valid_dispatch.replace("## 8. KPI Monitoring Framework", "")
        missing = tr.check_section_completeness(incomplete)
        self.assertIn("8. KPI Monitoring Framework", missing)

    def test_check_python_syntax_valid(self):
        valid, errors = tr.check_python_syntax(self.sample_valid_dispatch)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_check_python_syntax_invalid(self):
        broken = self.sample_valid_dispatch + "\n```python\ndef broken_func(:\n    pass\n```\n"
        valid, errors = tr.check_python_syntax(broken)
        self.assertFalse(valid)
        self.assertGreaterEqual(len(errors), 1)
        self.assertIn("SyntaxError", errors[0])

    def test_fix_wireguard_cryptographic_nonce_packing(self):
        flawed = """
        # Software fallback
        nonce = struct.pack("<LL", 0, pkt.counter)
        nonce = nonce.ljust(12, b"\\x00")
        """
        fixed, fixes = tr.fix_wireguard_cryptographic_defects(flawed)
        self.assertIn('struct.pack("<IQ", 0, pkt.counter)', fixed)
        self.assertNotIn("<LL", fixed)
        self.assertGreaterEqual(len(fixes), 1)

    def test_fix_wireguard_anti_replay_bounded_bitmask(self):
        flawed = """
        if diff < self.window_size:
            self.bitmap = (self.bitmap << diff) | 1
        """
        fixed, fixes = tr.fix_wireguard_cryptographic_defects(flawed)
        self.assertIn("((self.bitmap << diff) | 1) & ((1 << self.window_size) - 1)", fixed)
        self.assertGreaterEqual(len(fixes), 1)

    def test_fix_typography_and_formatting(self):
        flawed = 'print(\\"\\"\\"Hello World\\"\\"\\")\n```\nExtra line'
        fixed, fixes = tr.fix_typography_and_formatting(flawed)
        self.assertNotIn(r'\"\"\"', fixed)
        self.assertIn('"""', fixed)
        # Check code fence parity was balanced
        fence_count = len([l for l in fixed.splitlines() if l.strip().startswith("```")])
        self.assertEqual(fence_count % 2, 0)
        self.assertGreaterEqual(len(fixes), 1)

    def test_review_and_fix_dispatch_end_to_end(self):
        remediated, findings, fixes = tr.review_and_fix_dispatch(self.sample_valid_dispatch, "day_dispatch_test.md")
        self.assertEqual(findings, [])
        self.assertEqual(fixes, [])
        self.assertIn("Dispatch Technical Review & Completeness Audit", remediated)
        self.assertIn("- **Completeness Status:** Complete / Verified (10/10 Sections Verified)", remediated)
        self.assertIn("- [x] 10-Section Architecture Completeness Verified", remediated)
        self.assertIn("- [x] Python AST Syntax & Execution Compilation Verified", remediated)
        self.assertIn("- **Unique Flag:** `true`", remediated)


if __name__ == "__main__":
    unittest.main()
