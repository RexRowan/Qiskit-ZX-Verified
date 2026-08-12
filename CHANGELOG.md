# Changelog

## 0.1.0 -- initial release

- `lean/ZXVerify/SpiderFusion.lean`: formal, `sorry`-free proof of ZX
  spider fusion for degree-2 Clifford-phase spiders, plus the identity-
  removal corollary. Zero external Lean dependencies (no Mathlib).
- `qiskit_zx.fuse_phase_gates`: a Qiskit-native pass that fuses runs of
  phase-family gates (`P`, `Z`, `S`, `Sdg`, `T`, `Tdg`), honestly
  distinguishing Lean-certified (Clifford) fusions from merely-correct
  (non-Clifford) ones.
- `scripts/extract_lean_certificate.py`: cross-checks Lean's proved
  16-case table against Python's independent implementation.
- Full test suite (34 tests) including exact-matrix equivalence checks
  against `qiskit.quantum_info.Operator`.
- `docs/scope.md` and `docs/roadmap.md`: honest treatment of exactly
  what's proved and how the scope is meant to grow.
