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
        self.assertIn("Senior Peer Review & Systems Architecture Audit", remediated)
        self.assertIn("- **Reviewing Architect:**", remediated)
        self.assertIn("Principal Systems Architect", remediated)
        self.assertIn("- **Completeness Status:** Complete / Verified (10/10 Sections Verified)", remediated)
        self.assertIn("- **Architectural Evaluation Matrix:**", remediated)
        self.assertIn("- **Senior Peer Architectural Critique:**", remediated)
        self.assertIn("- **Unique Flag:** `true`", remediated)

    def test_senior_peer_evaluation_domains(self):
        meta_b = {"pillar": "B", "title": "WireGuard NVMe Offload"}
        eval_b = tr.evaluate_senior_peer_architecture("wireguard qat nvme", meta_b)
        self.assertIn("Linux Kernel-Bypass Networking", eval_b["focus_areas"])
        self.assertIn("Low-Latency Hardware Offload", eval_b["focus_areas"])
        self.assertIn("ksoftirqd", eval_b["critique"])

        meta_a = {"pillar": "A", "title": "FP8 Quantized GEMM"}
        eval_a = tr.evaluate_senior_peer_architecture("fp8 tensor gemm", meta_a)
        self.assertIn("Tensor Virtualization", eval_a["focus_areas"])
        self.assertIn("amax", eval_a["critique"])

    def test_fix_wireguard_hardware_ring_software_fallback(self):
        flawed = 'if not self.accel.submit_transform(desc):\n            raise BufferError("Hardware accelerator ring full; throttling required.")'
        fixed, fixes = tr.fix_wireguard_cryptographic_defects(flawed)
        self.assertIn("_execute_software_fallback_encrypt", fixed)
        self.assertNotIn("BufferError", fixed)
        self.assertIn("Implemented in-process AVX-512 SIMD software fallback on hardware offload ring saturation", fixes)

    def test_fix_wireguard_counter_window_size_injection(self):
        flawed = "class AntiReplayWindow:\n    def __init__(self, window_size: int = 64) -> None:\n"
        fixed, fixes = tr.fix_wireguard_cryptographic_defects(flawed)
        self.assertIn("COUNTER_WINDOW_SIZE: int = 2048", fixed)
        self.assertTrue(any("2048" in f for f in fixes))

    def test_fix_wireguard_anti_replay_test_assertion_contradiction(self):
        flawed = (
            "assert window_2048.validate_and_update(1) is True\n"
            "assert window_2048.validate_and_update(2048) is True\n"
            "assert window_2048.validate_and_update(1) is True   # Distance 2048 - 1 = 2047 < 2048 (still in window!)\n"
            "assert window_2048.validate_and_update(2049) is True"
        )
        fixed, fixes = tr.fix_wireguard_cryptographic_defects(flawed)
        self.assertIn("assert window_2048.validate_and_update(1) is False", fixed)
        self.assertIn("assert window_2048.validate_and_update(2) is True", fixed)
        self.assertTrue(any("reject replayed packet 1" in f for f in fixes))

    def test_senior_peer_evaluation_pillar_d_fhe(self):
        meta_d = {"pillar": "D", "title": "Hardware-Enclaved TFHE Torus Bootstrapping Fabric"}
        eval_d = tr.evaluate_senior_peer_architecture("tfhe torus homomorphic enclave sgx sev-snp", meta_d)
        self.assertIn("Principal Cryptographic Systems Architect", eval_d["reviewer_title"])
        self.assertIn("Homomorphic Lattice Cryptography (TFHE/LWE)", eval_d["focus_areas"])
        self.assertIn("Side-Channel Timing Resistance", eval_d["focus_areas"])
        matrix_titles = [m[0] for m in eval_d["matrix"]]
        self.assertIn("Cryptographic Noise Budget & Variance Reset", matrix_titles)
        self.assertIn("Constant-Time Oblivious Evaluation", matrix_titles)
        self.assertIn("Hardware Enclave Attestation & Memory Isolation", matrix_titles)
        self.assertIn("Enclave Page Cache (EPC) Allocation", matrix_titles)
        self.assertIn("SEV-SNP", eval_d["critique"])

    def test_fix_tfhe_cryptographic_defects_end_to_end(self):
        flawed = '''
class EnclaveTFHEEngine:
    def __init__(self, lwe_dim: int = 64, ring_dim: int = 256):
        self.n = lwe_dim
        self.N = ring_dim
        self._secret_key_lwe = np.random.randint(0, 2, size=self.n, dtype=np.int32)
        self._secret_key_ring = np.random.randint(0, 2, size=self.N, dtype=np.int32)

    def encrypt_lwe(self, message_bit: int):
        mu = 0.25 if message_bit == 1 else 0.0

    def decrypt_lwe(self, ct):
        dist_0 = min(phase, 1.0 - phase)
        dist_1 = min(abs(phase - 0.25), 1.0 - abs(phase - 0.25))

    def programmable_bootstrapping(self, ct_in, lut_poly):
        for i in range(self.n):
            shift_amount = a_bar[i]
            if self._secret_key_lwe[i] == 1:
                acc_b = self._negacyclic_monomial_mul(acc_b, shift_amount)
                acc_a = self._negacyclic_monomial_mul(acc_a, shift_amount)
        for i in range(min(self.n, self.N)):
            new_a[i] = acc_b[i]
        new_b = float(acc_b[0] + noise_reset) % 1.0

    def homomorphic_nand(self, ct1, ct2):
        b_nand = (0.625 - ct1.b - ct2.b) % 1.0
        lut_poly = np.zeros(self.N, dtype=np.float64)
        for i in range(self.N):
            lut_poly[i] = 0.25 if i < (self.N // 2) else 0.0

    def evaluate_splice_site_match(self, cand, target):
        xnor_out = self.homomorphic_nand(nand2, nand3)
        gate_count += 4
        peak_noise = max(peak_noise, xnor_out.noise_variance)

    def test_pbs(self):
        lut = np.zeros(self.engine.N, dtype=np.float64)
        lut[: self.engine.N // 2] = 0.25  # Identity LUT for bit 1
'''
        fixed, fixes = tr.fix_tfhe_cryptographic_defects(flawed)
        self.assertIn("_oblivious_cmux_rotate", fixed)
        self.assertIn("self.bootstrapping_key =", fixed)
        self.assertIn("b_nand = (0.875 - ct1.b - ct2.b) % 1.0", fixed)
        self.assertIn("lut_poly[: self.N // 2] = 0.125", fixed)
        self.assertIn("lut_poly[self.N // 2 :] = 0.875", fixed)
        self.assertIn("mu = 0.125 if message_bit == 1 else 0.875", fixed)
        self.assertIn("xor_out = self.homomorphic_nand(nand2, nand3)", fixed)
        self.assertIn("xnor_out = self.homomorphic_nand(xor_out, xor_out)", fixed)
        self.assertIn("(-acc_a[self.N - i]) % 1.0", fixed)
        self.assertIn("np.dot(new_a, self._secret_key_lwe)", fixed)
        self.assertGreaterEqual(len(fixes), 5)


if __name__ == "__main__":
    unittest.main()


