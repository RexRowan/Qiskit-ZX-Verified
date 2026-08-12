# Roadmap

Scoped, concrete next steps, roughly in order of how naturally each
builds on what's already proved. See `docs/scope.md` first for exactly
what's already done.

## 1. General continuous phases (Mathlib `Complex`)

Replace the `Fin 4` / `GaussianInt` representation with Mathlib's
`Complex` and `Real.cos`/`Real.sin`, and restate:

```
theorem spider_fusion_general (a b : Real) :
    composeDiag (spider a) (spider b) = spider (a + b)
```

This is mathematically just `Complex.exp_add` (`e^{i(a+b)} = e^{ia}
e^{ib}`), already proved in Mathlib -- the work here is mostly plumbing
(adding the Mathlib dependency to `lakefile.lean`, which will pull in a
`lake exe cache get` step and a noticeably longer first build) rather
than new mathematics. This is the highest-value next step: it would let
`fusion_pass.py` certify *every* fusion, not just the Clifford ones.

## 2. Multi-legged spiders

Extend `spider`/`composeDiag` from 2x2 diagonal matrices to general
`n`-to-`m` ZX spider tensors, and prove fusion for spiders connected by
one or more shared legs (the general form of the rule, matching
Coecke & Duncan's original statement). This needs a real tensor/diagram
representation in Lean, which is a bigger lift than (1) -- worth doing
after general phases, not before, so the tensor formalization only has
to handle `Complex` amplitudes once.

## 3. Additional rewrite rules

Once (1) and (2) are in place, natural next rules to formalize and wire
into the Qiskit pass:

- **Hadamard / color-change rule** (turns Z-spiders into X-spiders
  through a Hadamard edge) -- needed for anything beyond
  single-qubit-diagonal-gate fusion.
- **Bialgebra rule** -- needed for two-qubit gate simplification
  (e.g. CNOT-adjacent simplifications), which is where a ZX-based
  optimizer starts actually competing with PyZX on real circuits.

## 4. A general (non-diagonal-gate) ZX diagram representation

The current Python side (`qiskit_zx`) only represents diagonal
single-qubit phase gates, because that's exactly what's proved. A full
ZX diagram class (spiders + wires + Hadamard edges, convertible to/from
arbitrary Qiskit circuits) is a separate, larger undertaking -- and
should be built *after* the rules it needs to use are proved, not
before, so the engine's rewrite rules stay backed by proofs rather than
becoming "PyZX but Apache-licensed and less complete."

## 5. Wire into `qiskit-lean-bridge`

This project's Lean side currently has zero dependencies on
`qiskit-lean-bridge` / `LeanQuantum` (see `docs/scope.md` for why: kept
deliberately small and dependency-free for a fast first build). Once (1)
is done, revisit whether `ZXVerify`'s lemmas belong as a module inside
`LeanQuantum` directly, so the wider gate-equivalence extraction
pipeline can reference ZX rewrite soundness the same way it references
standard gate equivalences.
