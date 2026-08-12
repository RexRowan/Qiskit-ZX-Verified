# Scope: what is (and isn't) formally verified here

This is deliberately a small, precisely-scoped first release. Read this
before describing the project to anyone (including in an Ecosystem
submission) -- it's easy to accidentally overclaim "formally verified
ZX-calculus" when what's actually true is narrower and more useful:
**one specific rewrite rule, proved exactly for one specific (but
common) fragment of phases, with a working cross-checked bridge between
the proof and the Qiskit-facing code that uses it.**

## What is proved

`lean/ZXVerify/SpiderFusion.lean` proves, by exhaustive case check
(`decide`) over all 16 cases:

```
theorem spider_fusion (j k : Fin 4) :
    composeDiag (spider j) (spider k) = spider (j + k)
```

i.e. **spider fusion for degree-2 Z-spiders (phase gates) with Clifford
phases** (multiples of pi/2: 0, pi/2, pi, 3pi/2). This is a real,
checked, `sorry`-free proof (`#print axioms` shows only Lean's core
`propext` axiom, nothing added). Run `#print axioms
ZXVerify.spider_fusion` yourself to confirm.

Identity removal (`spider(0)` acts as the identity) follows as a direct
corollary, `spider_fusion_identity`.

## What is NOT proved (yet)

- **General (non-Clifford) phases.** The proof works because Clifford
  phase factors are exactly the four Gaussian integers `{1, i, -1, -i}`,
  letting `decide` finish a finite case check with exact integer
  arithmetic. A general phase `e^{i theta}` for arbitrary real `theta`
  needs Mathlib's `Complex` (built on Cauchy sequences / real analysis),
  which is a substantially larger dependency. `qiskit_zx.fusion_pass`
  still *correctly* fuses non-Clifford phase gates (ordinary real-number
  addition of angles is just true), but honestly reports those fusions
  as `lean_certified=False`. See `roadmap.md` for the path to closing
  this gap.
- **Spiders of degree != 2**, i.e. genuine multi-legged ZX diagram
  fusion (three or more wires meeting at a spider). The current proof
  only covers two-legged spiders, which correspond exactly to ordinary
  single-qubit phase gates in sequence -- a real and useful special
  case, but not the general ZX-calculus fusion rule as usually stated
  for arbitrary-arity spiders.
- **Other ZX rewrite rules** (bialgebra, color change / Hadamard rule,
  Euler decomposition, etc.) are not formalized in this repository at
  all yet.
- **The Qiskit-facing pass's *placement* logic** (deciding which gates
  in a circuit form a fusable "run", where non-phase gates interrupt a
  run) is ordinary Python, checked by unit tests and exact-matrix
  equivalence against `qiskit.quantum_info.Operator` -- not something
  Lean reasons about. Lean verifies the *arithmetic identity*; Python
  and the test suite are responsible for correctly *applying* it inside
  a circuit.

## Why this scope, and why it's still useful

Clifford-angle phase gates (`Z`, `S`, `Sdg`) are extremely common in
real circuits -- they show up constantly as byproducts of decomposition,
basis gate translation, and error correction constructions. A correctly
scoped, honestly labeled Clifford-only certified fusion pass is a real,
usable contribution even though it doesn't cover every phase gate in
existence. Overclaiming "verified ZX-calculus fusion" for the general
case would be actively misleading; this document exists so that never
happens by accident.
